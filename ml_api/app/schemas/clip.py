from pydantic import BaseModel
from typing import Optional

class CLIPResponse(BaseModel):
    predicted_label: str
    confidence: float
    request_id: str
    error: Optional[str] = None
    top_predictions: Optional[list[dict[str, float]]] = None