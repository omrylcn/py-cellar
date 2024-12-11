"""
REST API endpoints for the Model Registry service.

This module provides FastAPI routes for interacting with the model registry,
including uploading models and their metadata.

Notes
-----
The API uses FastAPI for routing and request handling, and supports
multipart/form-data for file uploads along with JSON metadata.
"""

from typing import Optional, Dict
import io
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ModelMetadata, ModelResponse, GetMetadataModelResponse
from .registry import ModelRegistry
from .exceptions import RegistryError
from .logger import logger

app = FastAPI(
    title="Model Registry API",
    description="REST API for managing ML models and their metadata",
    version="1.0.0",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegistryContainer:
    def __init__(self):
        self._registry: Optional[ModelRegistry] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize registry if not already initialized"""
        if not self._initialized:
            try:
                self._registry = ModelRegistry()
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize registry: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to initialize model registry",
                )

    async def get_registry(self) -> ModelRegistry:
        """Get or initialize registry instance"""
        if not self._initialized:
            await self.initialize()
        return self._registry


registry_container = RegistryContainer()


async def get_registry() -> ModelRegistry:
    """FastAPI dependency for getting registry instance"""
    return await registry_container.get_registry()


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint returning service information"""
    return {"service": "Model Registry", "version": "1.0.0", "status": "active"}


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


@app.post("/models/upload", response_model=ModelResponse)
async def upload_model(
    metadata: str = Form(...),
    model_file: UploadFile = File(...),
    registry: ModelRegistry = Depends(get_registry),
):
    """Upload a model file with its metadata"""
    try:
        # Validate metadata
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

        content = await model_file.read()
        file_obj = io.BytesIO(content)

        # Register model
        return registry.register_model(model_file=file_obj, metadata=metadata_model.model_dump())

    except RegistryError as e:
        logger.error(f"Model registration failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error during model registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get("/models/metadata/{file_path}")
async def get_model_metadata(
    file_path: str,
    metadata_id: str,
    bucket_name: Optional[str] = None,
    registry: ModelRegistry = Depends(get_registry),
):
    """Retrieve model metadata"""
    try:
        _, metadata = registry.get_model(file_path=file_path, metadata_id=metadata_id, bucket_name=bucket_name)

        try:
            metadata_response = GetMetadataModelResponse(
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
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Missing required metadata field: {str(e)}",
            )

        return metadata_response.model_dump_json()

    except RegistryError as e:
        logger.error(f"Failed to retrieve model metadata: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    except Exception as e:
        logger.error(f"Unexpected error retrieving model metadata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model metadata",
        )


@app.get("/models/file/{file_path}")
async def get_model_file(
    file_path: str,
    metadata_id: str,
    bucket_name: Optional[str] = None,
    registry: ModelRegistry = Depends(get_registry),
):
    """Stream model file content"""
    try:
        file_obj, metadata = registry.get_model(file_path=file_path, metadata_id=metadata_id, bucket_name=bucket_name)

        try:
            # Get file size
            file_obj.seek(0, 2)
            file_size = file_obj.tell()
            file_obj.seek(0)

            filename = metadata.get("name", file_path)
            file_extension = metadata.get("file_extension", "")
            content_filename = f"{filename}.{file_extension}"

            return StreamingResponse(
                file_obj,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f'attachment; filename="{content_filename}"',
                    "Content-Length": str(file_size),
                },
            )
        except Exception as e:
            logger.error(f"Error preparing file response: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error preparing file response",
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
