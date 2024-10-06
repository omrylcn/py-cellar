import torch
from datetime import datetime

from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from app.core.config import settings as config_settings
from app.utils.object_storage import ObjectStorage
from app.core.config import settings,BaseSettings
from app.services.base import AbstractModelService


class QAService(AbstractModelService):
    def __init__(self,settings:BaseSettings=None):

        self.settings = settings if settings else config_settings
        self.model = None
        self.model_name = self.settings.QA_NAME
        self.model_tag = self.settings.QA_TAG
        self.load_model()
        self.model.eval()
        
        self.storage = ObjectStorage(
            endpoint=self.settings.MINIO_ENDPOINT,
            access_key=self.settings.MINIO_ACCESS_KEY,
            secret_key=self.settings.MINIO_SECRET_KEY
        )

        
        self.bucket_name = self.settings.QA_NAME+"-"+self.settings.QA_TAG+"-"+self.settings.QA_VERSION
        self.storage.create_bucket(self.bucket_name)

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.settings.QA_MODEL_PATH)
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.settings.QA_MODEL_PATH)
    
    def answer_question(self, question, context):
        inputs = self.tokenizer(question, context, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        start_scores = outputs.start_logits
        end_scores = outputs.end_logits

        start_index = torch.argmax(start_scores)
        end_index = torch.argmax(end_scores)

        answer_tokens = inputs["input_ids"][0][start_index : end_index + 1]
        answer = self.tokenizer.decode(answer_tokens)

        result = {"answer": answer, "start": int(start_index), "end": int(end_index)}
        self._store_prediction(question, context, result)

        return result
    
    def predict(self, question, context):
        return self.answer_question(question, context)
    
    def _store_prediction(self, question, context, result):
        prediction_data = {
            "question": question,
            "context": context,
            "result": result,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_name": self.model_name,
            "model_tag": self.model_tag
        }

        object_name = f"prediction_{self.storage.generate_unique_id()}.json"
        self.storage.store_json(self.bucket_name, object_name, prediction_data)

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
