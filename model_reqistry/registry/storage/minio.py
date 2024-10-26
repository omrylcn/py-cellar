"""
MinIO storage implementation for model files.

This module provides a concrete implementation of the BaseStorage interface
using MinIO object storage for storing model files.
"""

import io
import logging
from typing import BinaryIO, Dict, Any, Tuple
from minio import Minio
from minio.error import MinioException, S3Error

from .base import BaseStorage
from ..config import settings
from ..exceptions import StorageError, ModelNotFoundError

logger = logging.getLogger(__name__)

class MinioStorage(BaseStorage):
    """
    MinIO-based implementation of model file storage.

    This class implements the BaseStorage interface using MinIO object storage
    with error handling and logging.

    Attributes
    ----------
    client : Minio
        MinIO client instance
    """

    def __init__(self):
        """
        Initialize MinIO storage client.

        Raises
        ------
        StorageError
            If connection to MinIO server fails
        """
        try:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False#getattr(settings, 'MINIO_SECURE', False)
            )
            logger.info("Successfully initialized MinIO client")
        except MinioException as e:
            logger.error(f"Failed to initialize MinIO client: {str(e)}")
            raise StorageError(f"MinIO initialization failed: {str(e)}")

    def _ensure_bucket(self, bucket_name: str) -> None:
        """
        Ensure a bucket exists, creating it if necessary.

        Parameters
        ----------
        bucket_name : str
            Name of the bucket to ensure exists

        Raises
        ------
        StorageError
            If bucket creation fails
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created new bucket: {bucket_name}")
        except MinioException as e:
            logger.error(f"Bucket operation failed: {str(e)}")
            raise StorageError(f"Failed to ensure bucket: {str(e)}")

    def store_model(self, model_file: BinaryIO, path: str, 
                   bucket_name: str) -> Dict[str, Any]:
        """
        Store a model file in MinIO.

        Parameters
        ----------
        model_file : BinaryIO
            Binary file object containing the model data
        path : str
            Desired storage path within the bucket
        bucket_name : str
            Name of the bucket to store in

        Returns
        -------
        Dict[str, Any]
            Storage information including path, bucket, size, and etag

        Raises
        ------
        StorageError
            If storing the model fails
        """
        try:
            self._ensure_bucket(bucket_name)
            
            # Get file size
            file_size = model_file.seek(0, 2)
            model_file.seek(0)

            # Store file
            result = self.client.put_object(
                bucket_name,
                path,
                model_file,
                file_size,
                #metadata={'content-type': 'application/octet-stream'}
            )
            
            storage_info = {
                'path': path,
                'bucket': bucket_name,
                'size': file_size,
                'etag': result.etag
            }
            
            logger.info(f"Successfully stored model: {storage_info}")
            return storage_info
            
        except MinioException as e:
            logger.error(f"Failed to store model: {str(e)}")
            raise StorageError(f"Model storage failed: {str(e)}")

    def get_model(self, path: str, bucket_name: str) -> BinaryIO:
        """
        Retrieve a model file from MinIO.

        Parameters
        ----------
        path : str
            Path to the model file within the bucket
        bucket_name : str
            Name of the bucket to retrieve from

        Returns
        -------
        Tuple[BinaryIO, Dict[str, str]]
            Binary file object containing the model data and its metadata

        Raises
        ------
        ModelNotFoundError
            If the model file does not exist
        StorageError
            If retrieving the model fails
        """
        response = None
        try:
            response = self.client.get_object(bucket_name, path)
            data = io.BytesIO(response.read())
            return data
            
        except S3Error as e:
            if e.code == 'NoSuchKey':
                logger.error(f"Model not found: {bucket_name}/{path}")
                raise ModelNotFoundError(f"Model not found: {path}")
            logger.error(f"Failed to retrieve model: {str(e)}")
            raise StorageError(f"Failed to retrieve model: {str(e)}")
        finally:
            if response:
                response.close()
                response.release_conn()

    def delete_model(self, path: str, bucket_name: str) -> None:
        """
        Delete a model file from MinIO.

        Parameters
        ----------
        path : str
            Path to the model file within the bucket
        bucket_name : str
            Name of the bucket to delete from

        Raises
        ------
        ModelNotFoundError
            If the model file does not exist
        StorageError
            If deleting the model fails
        """
        try:
            # Check if object exists first
            try:
                self.client.stat_object(bucket_name, path)
            except S3Error as e:
                if e.code == 'NoSuchKey':
                    raise ModelNotFoundError(f"Model not found: {path}")
                raise
            
            self.client.remove_object(bucket_name, path)
            logger.info(f"Successfully deleted model: {bucket_name}/{path}")
            
        except S3Error as e:
            logger.error(f"Failed to delete model: {str(e)}")
            raise StorageError(f"Failed to delete model: {str(e)}")