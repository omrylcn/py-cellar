"""
Model Registry implementation for managing ML models and metadata.

This module provides a centralized registry for managing machine learning models
and their metadata using MinIO for model storage and MongoDB for metadata storage.
"""

import logging
from typing import BinaryIO, Dict, Any, Tuple, Optional
import datetime

from .storage.minio import MinioStorage
from .storage.mongo import MongoStorage
from .schemas import ModelResponse
from .exceptions import RegistryError
from .logger import logger


class ModelRegistry:
    """
    A registry for managing ML models and their metadata.

    This class provides functionality to store and retrieve machine learning models
    along with their associated metadata using MinIO for model storage and MongoDB 
    for metadata storage.

    Attributes
    ----------
    model_storage : MinioStorage
        Storage handler for model binary files
    metadata_storage : MongoStorage
        Storage handler for model metadata
    """

    def __init__(self):
        """Initialize registry with storage backends."""
        try:
            self.model_storage = MinioStorage()
            self.metadata_storage = MongoStorage()
            logger.info("Successfully initialized ModelRegistry")
        except Exception as e:
            logger.error(f"Failed to initialize ModelRegistry: {str(e)}")
            raise RegistryError(f"Registry initialization failed: {str(e)}")

    def _generate_storage_path(self, metadata: Dict[str, Any]) -> str:
        """Generate storage path for model file."""
        return (f"{metadata['id']}_{metadata['name']}_"
                f"{metadata['version']}.{metadata['file_extension']}")

    def register_model(
        self,
        model_file: BinaryIO,
        metadata: Dict[str, Any]
    ) -> ModelResponse:
        """
        Register a new model with its metadata.

        Parameters
        ----------
        model_file : BinaryIO
            Binary file object containing the model data
        metadata : Dict[str, Any]
            Dictionary containing model metadata including:
            - id : str
                Unique identifier for the model
            - name : str
                Name of the model
            - version : str
                Version of the model
            - storage_group : str
                Storage bucket/group name
            - file_extension : str
                File extension (e.g., 'pkl', 'h5')
            - description : str, optional
                Model description
            - framework : str, optional
                ML framework used

        Returns
        -------
        ModelResponse
            Object containing the stored model information

        Raises
        ------
        RegistryError
            If registration process fails
        """
        try:
            # Generate storage path
            file_path = self._generate_storage_path(metadata)
        
            # Store model file
            storage_info = self.model_storage.store_model(
                model_file,
                file_path,
                metadata['storage_group']
            )
            
            # Prepare complete metadata
            full_metadata = {
                **metadata,
                'storage_path': file_path,
                'storage_info': storage_info,
                'registration_time': datetime.datetime.now(datetime.timezone.utc)
            }
            
            # Store metadata
            metadata_id = self.metadata_storage.store_metadata(full_metadata)
            
            logger.info(f"Successfully registered model: {metadata['id']} v{metadata['version']}")
            
            return ModelResponse(
                id=metadata['id'],
                name=metadata['name'],
                version=metadata['version'],
                metadata_id=metadata_id,
                storage_group=metadata['storage_group'],
                storage_path=file_path,
                created_at=datetime.datetime.now(datetime.timezone.utc),
                description=metadata.get('description'),
                framework=metadata.get('framework')
            )
            
        except Exception as e:
            logger.error(f"Model registration failed: {str(e)}")
            self._cleanup_failed_registration(file_path, metadata['storage_group'])
            raise RegistryError(f"Failed to register model: {str(e)}")

    def _cleanup_failed_registration(self, file_path: str, bucket: str) -> None:
        """Clean up resources after failed registration."""
        try:
            self.model_storage.delete_model(file_path, bucket)
        except Exception as e:
            logger.error(f"Cleanup after failed registration failed: {str(e)}")

    def get_model(
        self,
        file_path: str,
        metadata_id: str,
        bucket_name: Optional[str] = None
    ) -> Tuple[BinaryIO, Dict[str, Any]]:
        """
        Retrieve model and its metadata.

        Parameters
        ----------
        file_path : str
            Path to the model file
        metadata_id : str
            Metadata ID of the model
        bucket_name : str, optional
            Override storage bucket name

        Returns
        -------
        Tuple[BinaryIO, Dict[str, Any]]
            Model file and its metadata

        Raises
        ------
        RegistryError
            If retrieval fails
        """
        try:
            # Get metadata first
            metadata = self.metadata_storage.get_metadata(metadata_id)
          
            
            # Use bucket from metadata if not specified
            bucket = bucket_name or metadata.get('storage_group')
            
            # Get model file
            model_file = self.model_storage.get_model(
                file_path,
                bucket
            )
            
            return model_file, metadata
            
        except Exception as e:
            logger.error(f"Failed to retrieve model: {str(e)}")
            raise RegistryError(f"Failed to retrieve model: {str(e)}")