from typing import Dict, Any
from datetime import datetime
import torch
from fastapi import UploadFile
from prometheus_client import Gauge, Counter, Histogram
from transformers import CLIPTokenizerFast, CLIPProcessor, CLIPModel
from PIL import Image
import io

from app.core.config import settings as config_settings, BaseSettings
from app.core.logging import DBLogger
from app.utils.object_storage import ObjectStorage
from app.services.base import AbstractModelService
from app.utils.monitoring.clip import *
from app.utils.embedding import EmbeddingService
from app.schemas.clip import CLIPResponse

class CLIPService(AbstractModelService):
    def __init__(self, settings: BaseSettings = None, db_logger: DBLogger = None):
        self.settings = settings if settings else config_settings
        self.model = None
        self.processor = None
        self.tokenizer = None

        self.model_name = self.settings.CLIP_NAME
        self.model_tag = self.settings.CLIP_TAG
        self.model_version = self.settings.CLIP_VERSION
        self.name = f"{self.model_name}-{self.model_tag}-{self.model_version.replace('.','-')}"

        self.logger_params = {
            "model_name": self.model_name,
            "model_tag": self.model_tag,
            "model_version": self.model_version,
            "name": self.name,
        }
        self.db_logger = db_logger if db_logger else DBLogger(logger=self.settings.LOGGER_HANDLER, **self.logger_params)

        self.bucket_name = self.name
        self.storage = ObjectStorage(
            endpoint=self.settings.MINIO_ENDPOINT,
            access_key=self.settings.MINIO_ACCESS_KEY,
            secret_key=self.settings.MINIO_SECRET_KEY,
        )

        self.storage.create_bucket(self.bucket_name)
        self.load_model()

       # self.embedding_service = EmbeddingService()

    def load_model(self):
        try:
            self.model = CLIPModel.from_pretrained(self.settings.CLIP_MODEL_PATH)
            self.processor = CLIPProcessor.from_pretrained(self.settings.CLIP_MODEL_PATH)
            self.tokenizer = CLIPTokenizerFast.from_pretrained(self.settings.CLIP_MODEL_PATH)

            GPU_MEMORY_USAGE.set(torch.cuda.memory_allocated() if torch.cuda.is_available() else 0)

            self.db_logger.log_operation(f"Model loaded successfully: {self.settings.CLIP_MODEL_PATH}")
            self.db_logger.log_metadata(
                {
                    "model_path": self.settings.CLIP_MODEL_PATH,
                    "model_type": type(self.model).__name__,
                }
            )
        except Exception as e:
            self.db_logger.log_operation(f"Error loading model: {str(e)}", "error", exc_info=True)
            CLIP_ERRORS.labels(error_type="model_loading").inc()
            raise

    def predict(self, file: UploadFile, labels: list[str]) -> CLIPResponse:
        request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.db_logger.log_operation(f"Processing image. Request ID: {request_id}")

        result = {"label": None, "confidence": None, "request_id": request_id}

        try:
            st = datetime.now()

            image_data = file.read()
            image = Image.open(io.BytesIO(image_data))

            inputs = self.processor(text=labels, images=image, return_tensors="pt", padding=True)
            outputs = self.model(**inputs)

            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)

            max_prob, max_idx = torch.max(probs, dim=1)
            predicted_label = labels[max_idx.item()]
            confidence = max_prob.item()

            result["label"] = predicted_label
            result["confidence"] = confidence

            ft = datetime.now()
            taken = (ft - st).total_seconds()

            # Process image name with EmbeddingService
            embedding_distance = None #self.embedding_service.process_text(file.filename)

            # Log results
            self.db_logger.log_model_results(
                input_info={"filename": file.filename},
                results={
                    "request_id": request_id,
                    "label": result["label"],
                    "confidence": result["confidence"],
                },
            )

            # Store prediction
            self._store_prediction(file.filename, result, request_id)

            self._monitor_performance(file.filename, result, taken, embedding_distance, request_id, image.size)

            CLIP_REQUESTS_TOTAL.inc()

        except Exception as e:
            self.db_logger.log_operation(
                f"Error processing image. Request ID: {request_id}, Error: {str(e)}", "error", exc_info=True
            )
            CLIP_ERRORS.labels(error_type="prediction").inc()
            result["error"] = str(e)

        finally:
        
            return CLIPResponse(predicted_label=result["label"], confidence=result["confidence"], request_id=request_id)

    def _store_prediction(self, filename, result, request_id=None):
        prediction_data = {
            "filename": filename,
            "result": result,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_name": self.model_name,
            "model_tag": self.model_tag,
        }

        object_name = f"prediction_{request_id}.json"
        self.storage.store_json(self.bucket_name, object_name, prediction_data)

    def _monitor_performance(self, filename, result, taken, embedding_distance, request_id, image_size):
        CLIP_LATENCY.observe(float(taken))
        CLIP_CONFIDENCE.observe(result["confidence"])
        IMAGE_SIZE.observe(self.storage.get_object_size(self.bucket_name, filename))
        IMAGE_DIMENSIONS.observe(image_size[0] * image_size[1])
        FILE_EXTENSION.labels(extension=filename.split('.')[-1].lower()).inc()
        #EMBEDDING_DISTANCE.set(embedding_distance)
        LABEL_DISTRIBUTION.labels(label=result["label"]).inc()

    def get_prediction(self, object_name):
        return self.storage.get_json(self.bucket_name, object_name)