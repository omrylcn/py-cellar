"""
Base storage interfaces for the model registry.

This module defines abstract base classes for model and metadata storage,
providing standard interfaces that must be implemented by concrete storage classes.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any
from datetime import datetime

class BaseStorage(ABC):
    """
    Abstract base class for model file storage implementations.

    This class defines the interface for storing and retrieving model files.
    Concrete implementations must handle the actual storage operations
    (e.g., to filesystem, object storage, etc.).

    See Also
    --------
    MinioStorage : Implementation using MinIO object storage
    """
    
    @abstractmethod
    def store_model(self, model_file: BinaryIO, path: str) -> str:
        """
        Store a model file and return its storage path.

        Parameters
        ----------
        model_file : BinaryIO
            Binary file object containing the model data
        path : str
            Desired storage path for the model

        Returns
        -------
        str
            The actual path where the model was stored

        Raises
        ------
        StorageError
            If storing the model fails
        """
        pass
    
    @abstractmethod
    def get_model(self, path: str) -> BinaryIO:
        """
        Retrieve a model file by its path.

        Parameters
        ----------
        path : str
            Path where the model is stored

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
        pass
    
    @abstractmethod
    def delete_model(self, path: str) -> None:
        """
        Delete a model file.

        Parameters
        ----------
        path : str
            Path to the model file to delete

        Raises
        ------
        StorageError
            If deleting the model fails
        FileNotFoundError
            If the model file does not exist
        """
        pass

class BaseMetadataStorage(ABC):
    """
    Abstract base class for model metadata storage implementations.

    This class defines the interface for storing and retrieving model metadata.
    Concrete implementations must handle the actual storage operations
    (e.g., to database, file system, etc.).

    See Also
    --------
    MongoStorage : Implementation using MongoDB
    """
    
    @abstractmethod
    def store_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Store model metadata and return a unique identifier.

        Parameters
        ----------
        metadata : dict
            Dictionary containing model metadata

        Returns
        -------
        str
            Unique identifier for the stored metadata

        Raises
        ------
        StorageError
            If storing the metadata fails
        ValidationError
            If the metadata is invalid
        """
        pass
    
    @abstractmethod
    def get_metadata(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve model metadata by ID.

        Parameters
        ----------
        model_id : str
            Unique identifier of the model

        Returns
        -------
        dict
            Dictionary containing the model metadata

        Raises
        ------
        StorageError
            If retrieving the metadata fails
        ValueError
            If no metadata exists for the given ID
        """
        pass
    
    @abstractmethod
    def update_metadata(self, model_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update model metadata.

        Parameters
        ----------
        model_id : str
            Unique identifier of the model
        metadata : dict
            New metadata to update

        Returns
        -------
        dict
            Updated metadata dictionary

        Raises
        ------
        StorageError
            If updating the metadata fails
        ValueError
            If no metadata exists for the given ID
        ValidationError
            If the new metadata is invalid
        """
        pass