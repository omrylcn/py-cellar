"""
MongoDB storage implementation for model metadata.

This module provides a concrete implementation of the BaseMetadataStorage interface
using MongoDB for storing model metadata.
"""

import logging
from typing import Dict, Any
from pymongo import MongoClient
from bson import ObjectId

from .base import BaseMetadataStorage
from ..config import settings
from ..exceptions import RegistryError

logger = logging.getLogger(__name__)


class MongoStorage(BaseMetadataStorage):
    """
    MongoDB-based implementation of model metadata storage.

    This class implements the BaseMetadataStorage interface using MongoDB.
    It handles storing and retrieving model metadata with automatic
    timestamp management.

    Attributes
    ----------
    client : MongoClient
        MongoDB client instance
    db : Database
        MongoDB database instance
    collection : Collection
        MongoDB collection for storing model metadata
    """

    def __init__(self):
        """
        Initialize MongoDB storage client.

        Raises
        ------
        RegistryError
            If connection to MongoDB server fails
        """
        try:
            self.client = MongoClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB]
            self.collection = self.db.models
            logger.info("Successfully initialized MongoDB storage")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {str(e)}")
            raise RegistryError(f"MongoDB initialization failed: {str(e)}")

    def store_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Store model metadata in MongoDB.

        Parameters
        ----------
        metadata : Dict[str, Any]
            Dictionary containing model metadata

        Returns
        -------
        str
            Unique identifier (ObjectId) of the stored metadata

        Raises
        ------
        RegistryError
            If storing the metadata fails
        """
        try:
            # Add timestamp

            result = self.collection.insert_one(metadata)
            logger.info(f"Successfully stored metadata with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to store metadata: {str(e)}")
            raise RegistryError(f"Failed to store metadata: {str(e)}")

    def get_metadata(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve model metadata from MongoDB by ID.

        Parameters
        ----------
        model_id : str
            Unique identifier of the model

        Returns
        -------
        Dict[str, Any]
            Dictionary containing the model metadata

        Raises
        ------
        RegistryError
            If retrieving the metadata fails or model not found
        """
        try:
            result = self.collection.find_one({"_id": ObjectId(model_id)})
            if not result:
                logger.error(f"Metadata not found for ID: {model_id}")
                raise RegistryError(f"Metadata not found: {model_id}")

            # Convert ObjectId to string for JSON serialization
            result["_id"] = str(result["_id"])
            return result

        except Exception as e:
            logger.error(f"Failed to retrieve metadata: {str(e)}")
            raise RegistryError(f"Failed to retrieve metadata: {str(e)}")
