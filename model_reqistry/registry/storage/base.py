from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any
from datetime import datetime

class BaseStorage(ABC):
    """Base interface for model storage implementations"""
    
    @abstractmethod
    def store_model(self, model_file: BinaryIO, path: str) -> str:
        """Store model file and return storage path"""
        pass
    
    @abstractmethod
    def get_model(self, path: str) -> BinaryIO:
        """Retrieve model file by path"""
        pass
    
    @abstractmethod
    def delete_model(self, path: str) -> None:
        """Delete model file"""
        pass

class BaseMetadataStorage(ABC):
    """Base interface for metadata storage implementations"""
    
    @abstractmethod
    def store_metadata(self, metadata: Dict[str, Any]) -> str:
        """Store model metadata and return ID"""
        pass
    
    @abstractmethod
    def get_metadata(self, model_id: str) -> Dict[str, Any]:
        """Retrieve model metadata by ID"""
        pass
    
    @abstractmethod
    def update_metadata(self, model_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update model metadata"""
        pass