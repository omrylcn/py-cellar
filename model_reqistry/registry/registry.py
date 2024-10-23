from typing import BinaryIO, Dict, Any
from .storage.minio import MinioStorage
from .storage.mongo import MongoStorage
from .schemas import ModelResponse

class ModelRegistry:
    def __init__(self):
        self.model_storage = MinioStorage()
        self.metadata_storage = MongoStorage()
    
    def register_model(
        self,
        model_file: BinaryIO,
        metadata: Dict[str, Any]
    ) -> ModelResponse:
        # Generate storage path
        bucket_name = metadata['storage_group']
        file_path = f"{metadata['id']}_{metadata['name']}_{metadata['version']}.{metadata['file_extension']}"
        
        # Store model file
        self.model_storage.store_model(model_file, file_path, bucket_name)
        
        # Store metadata with storage path
        metadata['storage_path'] = file_path
        model_id = self.metadata_storage.store_metadata(metadata)
        
        # Get complete metadata
        stored_metadata = self.metadata_storage.get_metadata(model_id)
        
        return ModelResponse(
            model_id=model_id,
            **stored_metadata
        )
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        metadata = self.metadata_storage.get_metadata(model_id)
        if not metadata:
            raise ValueError(f"Model not found: {model_id}")
        return metadata