from typing import Optional, Dict
import io
import json
from datetime import datetime

from fastapi import APIRouter,HTTPException, Depends, Form, File, UploadFile, status
from fastapi.responses import StreamingResponse, JSONResponse

from registry.schemas import ModelResponse, ModelMetadata,GetMetadataModelResponse
from registry.core.dependencies import registry_container
from registry.core.dependencies import get_registry
from registry.services import ModelRegistry
from registry.exceptions import RegistryError,ModelNotFoundError
from registry.logger import logger


app = APIRouter()


@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint with enhanced status information"""
    try:
        registry = await registry_container.get_registry()
        return {
            "status": "healthy",
            "service": "Model Registry",
            "timestamp": datetime.utcnow().isoformat(),
            "registry_status": "connected",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "Model Registry",
                "error": str(e),
            },
        )


@app.post("/model/upload", response_model=ModelResponse,summary="Upload Model",description="Upload a model file with its metadata")
async def upload_model_file_and_metadata(
    metadata: str = Form(...),
    model_file: UploadFile = File(...),
    registry: ModelRegistry = Depends(get_registry),
):
    """Upload a model file with its metadata"""

    try:
        metadata_dict = json.loads(metadata)
        metadata_model = ModelMetadata(**metadata_dict)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON metadata: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metadata format: {str(e)}",
        )

    # Validate file
    if not model_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    # Validate file extension
    expected_extension = f".{metadata_model.file_extension}"
    if not model_file.filename.lower().endswith(expected_extension.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension mismatch. Expected {expected_extension}",
        )

 
    try:
        content = await model_file.read()
        file_obj = io.BytesIO(content)

        return registry.register_model(model_file=file_obj, metadata=metadata_model.model_dump())

    except RegistryError as e:
        logger.error(f"Model registration failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/model/metadata/{metadata_id}")
async def get_model_medata(metadata_id:str,registry: ModelRegistry = Depends(get_registry)):

    try:
        metadata = registry.get_metadata(metadata_id=metadata_id)
        return GetMetadataModelResponse(
            id=metadata["id"],
            name=metadata["name"],
            file_extension=metadata["file_extension"],
            storage_group=metadata["storage_group"],
            version=metadata["version"],
            description=metadata.get("description"),
            framework=metadata.get("framework"),
            metrics=metadata.get("metrics", {}),
            parameters=metadata.get("parameters", {}),
            metadata_id=metadata["_id"],
            storage_info=metadata["storage_info"],
            storage_path=metadata["storage_path"],
            registration_time=metadata["registration_time"],
        )
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model metadata not found: {metadata_id}"
        )
    except RegistryError as e:
        logger.error(f"Failed to retrieve metadata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/model/file/{file_path}")
async def get_model_file(
    file_path: str,
    bucket_name: str,
    registry: ModelRegistry = Depends(get_registry),
):
    """Stream model file content"""
    try:
    
        file_obj = registry.get_model_file(file_path=file_path,bucket_name=bucket_name)

        # Get file size
        file_obj.seek(0, 2)
        file_size = file_obj.tell()
        file_obj.seek(0)

        
        return StreamingResponse(
            file_obj,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{file_path}"',
                "Content-Length": str(file_size),
            },
        )
    

    except RegistryError as e:
        logger.error(f"Failed to retrieve file: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    except Exception as e:
        logger.error(f"Unexpected error retrieving file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file",
        )


