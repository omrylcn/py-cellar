from .base import BaseMetadataStorage
from pymongo import MongoClient
from typing import Dict, Any
from bson import ObjectId
from datetime import datetime
from ..config import settings

class MongoStorage(BaseMetadataStorage):
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
        self.collection = self.db.models
    
    def store_metadata(self, metadata: Dict[str, Any]) -> str:
        metadata['created_at'] = datetime.now()
        result = self.collection.insert_one(metadata)
        return str(result.inserted_id)
    
    def get_metadata(self, model_id: str) -> Dict[str, Any]:
        result = self.collection.find_one({'_id': ObjectId(model_id)})
        if result:
            result['_id'] = str(result['_id'])
        return result
    
    def update_metadata(self, model_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        metadata['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(model_id)},
            {'$set': metadata}
        )
        return self.get_metadata(model_id)