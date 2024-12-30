# app/service.py (Model Service)
import onnxruntime as ort
from PIL import Image
import numpy as np
import io
from celery import Celery
from app.config import settings

# Initialize Celery with RabbitMQ broker
celery_app = Celery('model_tasks', broker=settings.RABBITMQ_URL,backend=settings.REDIS_URL)

class ImageService:
    def __init__(self, model_path: str = settings.MODEL_PATH):
        # Initialize ONNX Runtime session - loaded once per worker
        ort.set_default_logger_severity(3)
        self.session = ort.InferenceSession(model_path)
        

    def process_image(self, image_bytes: bytes, image_size: tuple = (224, 224)):
        """Process image using the ONNX model"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        image = image.resize(image_size, resample=Image.Resampling.LANCZOS)

        # Preprocess
        x = np.array(image).astype('float32')
        x = np.transpose(x, [2, 0, 1])
        x = np.expand_dims(x, axis=0)
        
        # Run inference
        output_name = self.session.get_outputs()[0].name
        input_name = self.session.get_inputs()[0].name
        result = self.session.run([output_name], {input_name: x})[0][0]

        # Postprocess
        result = np.clip(result, 0, 255)
        result = result.transpose(1, 2, 0).astype("uint8")
        
        # Convert back to bytes
        output_image = Image.fromarray(result)
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

# Create a singleton instance
image_service = ImageService()

@celery_app.task(name='process_image_task')
def process_image_task(image_bytes: bytes, image_size: tuple = (224, 224)):
    """Celery task for processing images"""
    return image_service.process_image(image_bytes, image_size)

@celery_app.task(name='demo_process_task')
def demo_process():
    """Demo task for testing"""
    return "Demo task completed"