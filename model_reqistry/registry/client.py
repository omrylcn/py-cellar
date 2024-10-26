import os
from typing import Optional, Dict, Any, Tuple, BinaryIO, Union
import requests
import json
import io
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from .schemas import ModelMetadata,ModelInfo
from .logger import logger



class RegistryClientError(Exception):
    """Base exception for registry client errors"""
    pass

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
        """
        Initialize the registry client.
        
        Parameters
        ----------
        base_url : str
            Base URL of the registry service
        timeout : int
            Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def health_check(self) -> bool:
        """
        Check if the registry service is healthy.
        
        Returns
        -------
        bool
            True if service is healthy
            
        Raises
        ------
        RegistryConnectionError
            If connection fails
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['status'] == 'healthy'
        except requests.exceptions.RequestException as e:
            raise RegistryConnectionError(f"Failed to connect to registry: {str(e)}")

    def upload_model(
        self,
        model_buffer: Union[BinaryIO, bytes, io.BytesIO],
        metadata: ModelMetadata,
        filename: Optional[str] = None
    ) -> ModelInfo:
        """
        Upload a model from a buffer with metadata to the registry.
        
        Parameters
        ----------
        model_buffer : Union[BinaryIO, bytes, io.BytesIO]
            Buffer containing the model data
        metadata : ModelMetadata
            Model metadata
        filename : Optional[str]
            Custom filename for the upload. If not provided, uses metadata.name
            
        Returns
        -------
        ModelInfo
            Information about the registered model
            
        Raises
        ------
        ModelUploadError
            If upload fails
        """
        try:
            # Convert buffer to BytesIO if needed
            # if isinstance(model_buffer, bytes):
            #     buffer = io.BytesIO(model_buffer)
            # elif isinstance(model_buffer, io.BytesIO):
            #     buffer = model_buffer
            # else:
            #     buffer = io.BytesIO(model_buffer.read())
            
            # Reset buffer position
            model_buffer.seek(0)
            
            # Generate filename if not provided
            if not filename:
                filename = f"{metadata.name}.{metadata.file_extension}"

            # Prepare multipart form data
            files = {
                'model_file': (
                    filename,
                    model_buffer,
                    'application/octet-stream'
                )
            }
            
            data = {
                'metadata': json.dumps(metadata.__dict__)
            }

            # Upload model
            response = self.session.post(
                f"{self.base_url}/models/upload",
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result
            # return ModelInfo(
            #     metadata_id=result['metadata_id'],
            #     storage_path=result['storage_path'],
            #     storage_info=result['storage_info'],
            #     registration_time=datetime.fromisoformat(result['registration_time'])
            # )
            
        except requests.exceptions.RequestException as e:
            raise ModelUploadError(f"Failed to upload model: {str(e)}")
        

    def get_model_buffer(
        self,
        file_path: str,
        metadata_id: str,
        bucket_name: Optional[str] = None
    ) -> Tuple[io.BytesIO, Dict[str, Any]]:
        """
        Retrieve a model and its metadata from the registry as buffer.
        
        Parameters
        ----------
        file_path : str
            Path to the model in registry
        metadata_id : str
            Metadata ID of the model
        bucket_name : Optional[str]
            Override storage bucket name
            
        Returns
        -------
        Tuple[io.BytesIO, Dict[str, Any]]
            Tuple of (model buffer, metadata)
            
        Raises
        ------
        ModelNotFoundError
            If model not found
        RegistryClientError
            For other errors
        """
        try:
            # First get metadata
            params = {'metadata_id': metadata_id}
            if bucket_name:
                params['bucket_name'] = bucket_name
                
            metadata_response = self.session.get(
                f"{self.base_url}/models/metadata/{file_path}",
                params=params,
                timeout=self.timeout
            )
            metadata_response.raise_for_status()
            metadata = metadata_response.json()

            # Then get model file
            file_response = self.session.get(
                f"{self.base_url}/models/file/{file_path}",
                params=params,
                stream=True,
                timeout=self.timeout
            )
            file_response.raise_for_status()

            # Return as BytesIO object
            buffer = io.BytesIO()
            for chunk in file_response.iter_content(chunk_size=8192):
                buffer.write(chunk)
            buffer.seek(0)
            
            return buffer, json.loads(metadata)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ModelNotFoundError(f"Model not found: {file_path}")
            raise RegistryClientError(f"Failed to retrieve model: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise RegistryClientError(f"Failed to retrieve model: {str(e)}")
        

