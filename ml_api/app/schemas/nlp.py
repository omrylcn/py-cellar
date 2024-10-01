from pydantic import BaseModel


class QAData(BaseModel):
    question: str
    context: str


class QAResponse(BaseModel):
    answer: str
    start: int
    end: int
