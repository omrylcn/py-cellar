import io

from fastapi import FastAPI
from fastapi import APIRouter, File, UploadFile, HTTPException

from .schemas import ModelMetadata, ModelResponse
from .storage.minio import MinioStorage
from .storage.mongo import MongoStorage
from .registry import ModelRegistry


app = FastAPI()
registry = ModelRegistry()

@app.get("/")
async def root():
    return {"Hello from Model Registry"}

@app.post("/models/upload", response_model=ModelResponse)
async def upload_model(
    metadata: ModelMetadata,
    model_file: UploadFile = File(...)
):
   
    content = await model_file.read()
    file_obj = io.BytesIO(content)
    
    try:
        return registry.register_model(
            model_file=file_obj,
            metadata=metadata.model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    


