from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ModelMetadata(BaseModel):
    id:str
    name: str
    file_extension: str
    storage_group: str = Field(..., description="Name of storage like bucket name for minio") # for bucket name in minio
    version: str = Field(..., description="Version of the model")
    description: Optional[str] = None
    framework: str = None
    metrics: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class ModelResponse(BaseModel):
    name: str
    version: str
    storage_path: str
    created_at: datetime
    metrics: Optional[Dict[str, Any]] = None
    description: Optional[str] = None