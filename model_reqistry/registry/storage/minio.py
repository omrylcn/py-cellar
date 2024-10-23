"""
MinIO storage implementation for model files.

This module provides a concrete implementation of the BaseStorage interface
using MinIO object storage for storing model files.
"""

from .base import BaseStorage
from minio import Minio
from typing import BinaryIO
import io
from ..config import settings

class MinioStorage(BaseStorage):
    """
    MinIO-based implementation of model file storage.

    This class implements the BaseStorage interface using MinIO object storage.
    It handles automatic bucket creation and provides methods for storing,
    retrieving, and deleting model files.

    Attributes
    ----------
    client : Minio
        MinIO client instance
    
    Notes
    -----
    The storage configuration is read from settings including:
    - MINIO_ENDPOINT
    - MINIO_ACCESS_KEY
    - MINIO_SECRET_KEY
    - MINIO_BUCKET
    """

    def __init__(self):
        """
        Initialize MinIO storage client.

        Creates a MinIO client instance and ensures the default bucket exists.

        Raises
        ------
        ConnectionError
            If connection to MinIO server fails
        """
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )
        self._ensure_bucket()

    def _ensure_bucket(self, bucket_name: str = settings.MINIO_BUCKET):
        """
        Ensure a bucket exists, creating it if necessary.

        Parameters
        ----------
        bucket_name : str, optional
            Name of the bucket to ensure exists, by default from settings.MINIO_BUCKET

        Raises
        ------
        StorageError
            If bucket creation fails
        """
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def store_model(self, model_file: BinaryIO, path: str, bucket_name: str = None) -> str:
        """
        Store a model file in MinIO.

        Parameters
        ----------
        model_file : BinaryIO
            Binary file object containing the model data
        path : str
            Desired storage path within the bucket
        bucket_name : str, optional
            Name of the bucket to store in, by default from settings

        Returns
        -------
        str
            The storage path of the model

        Raises
        ------
        StorageError
            If storing the model fails
        """
        file_size = model_file.seek(0, 2)
        model_file.seek(0)

        bucket_name = bucket_name if bucket_name else settings.MINIO_BUCKET
        self._ensure_bucket(bucket_name)
        
        self.client.put_object(bucket_name, path, model_file, file_size)
        return path

    def get_model(self, path: str) -> BinaryIO:
        """
        Retrieve a model file from MinIO.

        Parameters
        ----------
        path : str
            Path to the model file within the bucket

        Returns
        -------
        BinaryIO
            Binary file object containing the model data

        Raises
        ------
        StorageError
            If retrieving the model fails
        FileNotFoundError
            If the model file does not exist
        """
        try:
            response = self.client.get_object(settings.MINIO_BUCKET, path)
            return io.BytesIO(response.read())
        finally:
            response.close()
            response.release_conn()

    def delete_model(self, path: str) -> None:
        """
        Delete a model file from MinIO.

        Parameters
        ----------
        path : str
            Path to the model file within the bucket

        Raises
        ------
        StorageError
            If deleting the model fails
        FileNotFoundError
            If the model file does not exist
        """
        self.client.remove_object(settings.MINIO_BUCKET, path)