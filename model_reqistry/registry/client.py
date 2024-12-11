from typing import Optional, Dict, Any, Tuple, BinaryIO, Union
import requests

# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
import json
import io

# from dataclasses import dataclass
# from datetime import datetime
# from pathlib import Path
# from pydantic import BaseModel, Field
from .schemas import ModelMetadata, ModelInfo
from .logger import logger


class RegistryClientError(Exception):
    """Base exception for registry client errors"""

    def __init__(self, message: str):
        super().__init__(message)
        logger.error(f"Registry error: {message}")


class ModelNotFoundError(RegistryClientError):
    """Raised when a requested model is not found"""

    pass


class RegistryConnectionError(RegistryClientError):
    """Raised when connection to registry fails"""

    pass


class ModelUploadError(RegistryClientError):
    """Raised when model upload fails"""

    pass


class ModelRegistryClient:
    """Client for interacting with the Model Registry API"""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize the registry client"""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        logger.info(f"Initialized registry client with base URL: {base_url}")

    def health_check(self) -> bool:
        """Check if the registry service is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            is_healthy = response.json()["status"] == "healthy"
            logger.info(f"Health check status: {'healthy' if is_healthy else 'unhealthy'}")
            return is_healthy
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {str(e)}")
            raise RegistryConnectionError(f"Failed to connect to registry: {str(e)}")

    def upload_model(self, model_buffer: Union[BinaryIO, bytes, io.BytesIO], metadata: ModelMetadata, filename: Optional[str] = None) -> ModelInfo:
        """Upload a model to the registry"""
        try:
            model_buffer.seek(0)
            if not filename:
                filename = f"{metadata.name}.{metadata.file_extension}"

            files = {"model_file": (filename, model_buffer, "application/octet-stream")}
            data = {"metadata": json.dumps(metadata.__dict__)}

            logger.info(f"Uploading model: {filename}")
            response = self.session.post(f"{self.base_url}/models/upload", files=files, data=data, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Successfully uploaded model: {filename}")
            return ModelInfo(
                name=result["name"],
                version=result["version"],
                metadata_id=result["metadata_id"],
                file_path=result["storage_path"],
                storage_group=result["storage_group"],
                registration_time=result["created_at"],
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload model: {str(e)}")
            raise ModelUploadError(f"Failed to upload model: {str(e)}")

    def get_model_buffer(self, file_path: str, metadata_id: str, bucket_name: Optional[str] = None) -> Tuple[io.BytesIO, Dict[str, Any]]:
        """Retrieve a model and its metadata from the registry"""
        try:
            params = {"metadata_id": metadata_id}
            if bucket_name:
                params["bucket_name"] = bucket_name

            logger.info(f"Retrieving model metadata: {file_path}")
            metadata_response = self.session.get(f"{self.base_url}/models/metadata/{file_path}", params=params, timeout=self.timeout)
            metadata_response.raise_for_status()
            metadata = metadata_response.json()

            logger.info(f"Retrieving model file: {file_path}")
            file_response = self.session.get(f"{self.base_url}/models/file/{file_path}", params=params, stream=True, timeout=self.timeout)
            file_response.raise_for_status()

            buffer = io.BytesIO()
            for chunk in file_response.iter_content(chunk_size=8192):
                buffer.write(chunk)
            buffer.seek(0)

            logger.info(f"Successfully retrieved model: {file_path}")
            return buffer, metadata

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Model not found: {file_path}")
                raise ModelNotFoundError(f"Model not found: {file_path}")
            logger.error(f"Failed to retrieve model: {str(e)}")
            raise RegistryClientError(f"Failed to retrieve model: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve model: {str(e)}")
            raise RegistryClientError(f"Failed to retrieve model: {str(e)}")
