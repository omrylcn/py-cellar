from fastapi import APIRouter
from app.services.nlp import QAService
from app.schemas.nlp import QAResponse, QAData

qa_service = QAService()
qa_router = APIRouter()


@qa_router.post("/answer", response_model=QAResponse)
async def answer_question(request: QAData):
    result = qa_service.answer_question(request.question, request.context)

    return result