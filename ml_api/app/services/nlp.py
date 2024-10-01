import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

from app.core.config import settings


class QAService:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(settings.QA_MODEL_PATH)
        self.model = AutoModelForQuestionAnswering.from_pretrained(settings.QA_MODEL_PATH)
        self.model.eval()

    def answer_question(self, question, context):

        inputs = self.tokenizer(question, context, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Process outputs
        start_scores = outputs.start_logits
        end_scores = outputs.end_logits

        # Get the most likely beginning and end of answer
        start_index = torch.argmax(start_scores)
        end_index = torch.argmax(end_scores)

        # Convert tokens to string
        answer_tokens = inputs["input_ids"][0][start_index : end_index + 1]
        answer = self.tokenizer.decode(answer_tokens)

        return {"answer": answer, "start": int(start_index), "end": int(end_index)}
