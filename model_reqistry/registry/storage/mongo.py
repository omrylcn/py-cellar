"""
MongoDB storage implementation for model metadata.

This module provides a concrete implementation of the BaseMetadataStorage interface
using MongoDB for storing model metadata.
"""

from .base import BaseMetadataStorage
from pymongo import MongoClient
from typing import Dict, Any
from bson import ObjectId
from datetime import datetime
from ..config import settings

class MongoStorage(BaseMetadataStorage):
    """
    MongoDB-based implementation of model metadata storage.

    This class implements the BaseMetadataStorage interface using MongoDB.
    It handles storing, retrieving, and updating model metadata with automatic
    timestamp management.

    Attributes
    ----------
    client : MongoClient
        MongoDB client instance
    db : Database
        MongoDB database instance
    collection : Collection
        MongoDB collection for storing model metadata

    Notes
    -----
    The storage configuration is read from settings including:
    - MONGODB_URL
    - MONGODB_DB
    
    Timestamps are automatically added:
    - created_at: When metadata is first stored
    - updated_at: When metadata is updated
    """

    def __init__(self):
        """
        Initialize MongoDB storage client.

        Creates a MongoDB client instance and sets up the database and collection.

        Raises
        ------
        ConnectionError
            If connection to MongoDB server fails
        """
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
        self.collection = self.db.models
    
    def store_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Store model metadata in MongoDB.

        Parameters
        ----------
        metadata : dict
            Dictionary containing model metadata

        Returns
        -------
        str
            Unique identifier (ObjectId) of the stored metadata

        Raises
        ------
        StorageError
            If storing the metadata fails
        ValidationError
            If the metadata is invalid
        """
        metadata['created_at'] = datetime.now()
        result = self.collection.insert_one(metadata)
        return str(result.inserted_id)
    
    def get_metadata(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve model metadata from MongoDB by ID.

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
        ValueError
            If no metadata exists for the given ID
        StorageError
            If retrieving the metadata fails
        """
        result = self.collection.find_one({'_id': ObjectId(model_id)})
        if result:
            result['_id'] = str(result['_id'])
        return result
    
    def update_metadata(self, model_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update model metadata in MongoDB.

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
        ValueError
            If no metadata exists for the given ID
        StorageError
            If updating the metadata fails
        ValidationError
            If the new metadata is invalid

        Notes
        -----
        The updated_at timestamp is automatically set to the current UTC time.
        """
        metadata['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(model_id)},
            {'$set': metadata}
        )
        return self.get_metadata(model_id)