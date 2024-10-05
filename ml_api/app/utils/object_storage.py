from minio import Minio
from minio.error import S3Error
import json
import io
import uuid
from typing import Optional


class ObjectStorage:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def create_bucket(self, bucket_name: str) -> None:
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created successfully")
            else:
                print(f"Bucket '{bucket_name}' already exists")
        except S3Error as e:
            print(f"Error creating bucket '{bucket_name}': {e}")

    def store_object(self, bucket_name: str, object_name: str, data: bytes, content_type: str) -> None:
        try:
            self.client.put_object(
                bucket_name,
                object_name,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type
            )
            print(f"Object '{object_name}' stored in bucket '{bucket_name}'")
        except S3Error as e:
            print(f"Error storing object '{object_name}' in bucket '{bucket_name}': {e}")

    def get_object(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        try:
            response = self.client.get_object(bucket_name, object_name)
            return response.read()
        except S3Error as e:
            print(f"Error retrieving object '{object_name}' from bucket '{bucket_name}': {e}")
            return None

    def store_json(self, bucket_name: str, object_name: str, data: dict) -> None:
        json_data = json.dumps(data).encode('utf-8')
        self.store_object(bucket_name, object_name, json_data, "application/json")

    def get_json(self, bucket_name: str, object_name: str) -> Optional[dict]:
        data = self.get_object(bucket_name, object_name)
        if data:
            return json.loads(data.decode('utf-8'))
        return None

    def generate_unique_id(self) -> str:
        return str(uuid.uuid4())