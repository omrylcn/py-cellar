from .base import BaseStorage
from minio import Minio
from typing import BinaryIO
import io
from ..config import settings


class MinioStorage(BaseStorage):
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )
        self._ensure_bucket()

    def _ensure_bucket(self, bucket_name: str = settings.MINIO_BUCKET):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def store_model(self, model_file: BinaryIO, path: str, bucket_name: str = None) -> str:
        file_size = model_file.seek(0, 2)
        model_file.seek(0)

        bucket_name = bucket_name if bucket_name else settings.MINIO_BUCKET
        self._ensure_bucket(bucket_name)
        
        self.client.put_object(bucket_name,path, model_file, file_size)
        return path

    def get_model(self, path: str) -> BinaryIO:
        try:
            response = self.client.get_object(settings.MINIO_BUCKET, path)
            return io.BytesIO(response.read())
        finally:
            response.close()
            response.release_conn()

    def delete_model(self, path: str) -> None:
        self.client.remove_object(settings.MINIO_BUCKET, path)
