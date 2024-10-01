from pydantic import BaseModel

class CLIPResponse(BaseModel):
    predicted_label: str
    confidence: float

