import torch
from datetime import datetime

from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from app.utils.object_storage import ObjectStorage
from app.core.config import settings, BaseSettings
from app.core.config import settings as config_settings
from app.core.logging import DBLogger
from app.services.base import AbstractModelService
from app.utils.monitoring.qa import *
from app.utils.embedding import EmbeddingService

from prometheus_client import Gauge

# New metric for embedding distances
EMBEDDING_DISTANCE = Gauge('qa_embedding_distance', 'Distance')


class QAService(AbstractModelService):
    def __init__(self, settings: BaseSettings = None, db_logger: DBLogger = None):

        self.settings = settings if settings else config_settings
        self.model = None
        self.model_name = self.settings.QA_NAME
        self.model_tag = self.settings.QA_TAG
        self.model_version = self.settings.QA_VERSION
        # make unique name

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
        self.model.eval()

        self.embedding_service = EmbeddingService()

        

    def load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.settings.QA_MODEL_PATH)
            self.model = AutoModelForQuestionAnswering.from_pretrained(self.settings.QA_MODEL_PATH)
            self.db_logger.log_operation(f"Model loaded successfully: {self.settings.QA_MODEL_PATH}")
            self.db_logger.log_metadata(
                {
                    "model_path": self.settings.QA_MODEL_PATH,
                    "tokenizer_type": type(self.tokenizer).__name__,
                    "model_type": type(self.model).__name__,
                }
            )
        except Exception as e:
            self.db_logger.log_operation(f"Error loading model: {str(e)}", "error", exc_info=True)
            raise

    def answer_question(self, question, context):

        request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.db_logger.log_operation(f"Processing question. Request ID: {request_id}")

        result = {"answer": None, "start": None, "end": None, "confidence": None, "request_id": request_id}

        try:
            st = datetime.now()
            # Tokenize input
            inputs = self.tokenizer(question, context, return_tensors="pt", max_length=512, truncation=True)

            # Generate answer
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Process output
            start_scores, end_scores = outputs.start_logits, outputs.end_logits
            start_index = torch.argmax(start_scores)
            end_index = torch.argmax(end_scores)

            # Ensure end_index is not before start_index
            if end_index < start_index:
                end_index = start_index + torch.argmax(end_scores[start_index:])

            answer_tokens = inputs["input_ids"][0][start_index : end_index + 1]
            answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True)

            # Calculate confidence score
            confidence = float(torch.max(start_scores) + torch.max(end_scores))

            result.update(
                {"answer": answer, "start": int(start_index), "end": int(end_index), "confidence": confidence}
            )
            ft= datetime.now()
            taken = (ft - st).total_seconds()
            self.db_logger.log_operation(f"Processing time: {taken}")
            #print(taken)


            ### Log Parts
            
            embedding_distance = self.embedding_service.process_text(question)


            # Log results
            self.db_logger.log_model_results(
                input_info={"question": question, "context": context},
                results={
                    "request_id": request_id,
                    "question_length": len(question),
                    "context_length": len(context),
                    "answer_length": len(answer),
                    "confidence": confidence,
                    "result": result,
                },
            )

            # Store prediction
            self._store_prediction(question, context, result, request_id)

            print(embedding_distance)
            self._monitor_performance(question, context, result,taken,embedding_distance,request_id)

        except Exception as e:
            self.db_logger.log_operation(
                f"Error answering question. Request ID: {request_id}, Error: {str(e)}", "error", exc_info=True
            )
            result["error"] = str(e)
            

        finally:
            return result

    def predict(self, question, context):
        return self.answer_question(question, context)

    def _store_prediction(self, question, context, result,request_id=None):
        prediction_data = {
            "question": question,
            "context": context,
            "result": result,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_name": self.model_name,
            "model_tag": self.model_tag,
        }

        object_name = f"prediction_{request_id}.json"
        self.storage.store_json(self.bucket_name, object_name, prediction_data)
    def _monitor_performance(self,question, context,result,taken,embedding_distance,request_id=None):
        # Get current time
      
        QA_REQUESTS_TOTAL.inc()

        QUESTION_LENGTH.observe(len(question))
        CONTEXT_LENGTH.observe(len(context))
        ANSWER_LENGTH.observe(len(result["answer"]))
        QA_CONFIDENCE.observe(result["confidence"])
        QA_LATENCY.observe(float(taken))
        EMBEDDING_DISTANCE.set(embedding_distance)
        




    def get_prediction(self, object_name):
        return self.storage.get_json(self.bucket_name, object_name)


# import torch
# from transformers import AutoTokenizer, AutoModelForQuestionAnswering

# from app.core.config import settings


# class QAService:
#     def __init__(self):
#         self.tokenizer = AutoTokenizer.from_pretrained(settings.QA_MODEL_PATH)
#         self.model = AutoModelForQuestionAnswering.from_pretrained(settings.QA_MODEL_PATH)
#         self.model.eval()

#     def answer_question(self, question, context):

#         inputs = self.tokenizer(question, context, return_tensors="pt")

#         with torch.no_grad():
#             outputs = self.model(**inputs)

#         # Process outputs
#         start_scores = outputs.start_logits
#         end_scores = outputs.end_logits

#         # Get the most likely beginning and end of answer
#         start_index = torch.argmax(start_scores)
#         end_index = torch.argmax(end_scores)

#         # Convert tokens to string
#         answer_tokens = inputs["input_ids"][0][start_index : end_index + 1]
#         answer = self.tokenizer.decode(answer_tokens)

#         return {"answer": answer, "start": int(start_index), "end": int(end_index)}
