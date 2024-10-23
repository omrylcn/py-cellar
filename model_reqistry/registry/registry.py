from typing import BinaryIO, Dict, Any
from .storage.minio import MinioStorage
from .storage.mongo import MongoStorage
from .schemas import ModelResponse

class ModelRegistry:
    """
    A registry for managing ML models and their metadata.

    This class provides functionality to store and retrieve machine learning models
    along with their associated metadata using MinIO for model storage and MongoDB 
    for metadata storage.

    Attributes
    ----------
    model_storage : MinioStorage
        Storage handler for model binary files using MinIO
    metadata_storage : MongoStorage
        Storage handler for model metadata using MongoDB

    Examples
    --------
    >>> registry = ModelRegistry()
    >>> with open('model.pkl', 'rb') as f:
    ...     metadata = {
    ...         'id': 'model-123',
    ...         'name': 'sentiment-model',
    ...         'version': '1.0.0',
    ...         'file_extension': 'pkl',
    ...         'storage_group': 'nlp-models'
    ...     }
    ...     response = registry.register_model(f, metadata)
    """

    def __init__(self):
        """
        Initialize the ModelRegistry with storage backends.

        Creates instances of MinIO and MongoDB storage handlers for managing
        model files and metadata respectively.
        """
        self.model_storage = MinioStorage()
        self.metadata_storage = MongoStorage()
    
    def register_model(
        self,
        model_file: BinaryIO,
        metadata: Dict[str, Any]
    ) -> ModelResponse:
        """
        Register a new model with its metadata.

        Parameters
        ----------
        model_file : BinaryIO
            Binary file object containing the model data
        metadata : dict
            Dictionary containing model metadata with the following required fields:
            
            - id : str
                Unique identifier for the model
            - name : str
                Name of the model
            - version : str
                Version of the model
            - file_extension : str
                File extension of the model file
            - storage_group : str
                Name of the storage bucket where model will be stored
            - description : str, optional
                Model description
            - framework : str, optional
                ML framework used
            - metrics : dict, optional
                Model performance metrics
            - parameters : dict, optional
                Model parameters

        Returns
        -------
        ModelResponse
            Object containing the stored model information including:
            
            - model_id : str
                Unique identifier of the stored model
            - name : str
                Name of the model
            - version : str
                Version of the model
            - storage_path : str
                Path where the model is stored
            - created_at : datetime
                Timestamp of model registration
            - metrics : dict, optional
                Model performance metrics

        Raises
        ------
        ValueError
            If required metadata fields are missing

        Notes
        -----
        The storage path is automatically generated using the format:
        "{id}_{name}_{version}.{file_extension}"
        """
        bucket_name = metadata['storage_group']
        file_path = f"{metadata['id']}_{metadata['name']}_{metadata['version']}.{metadata['file_extension']}"
        
        self.model_storage.store_model(model_file, file_path, bucket_name)
        
        metadata['storage_path'] = file_path
        model_id = self.metadata_storage.store_metadata(metadata)
        
        stored_metadata = self.metadata_storage.get_metadata(model_id)
        
        return ModelResponse(
            model_id=model_id,
            **stored_metadata
        )
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve model metadata by ID.

        Parameters
        ----------
        model_id : str
            Unique identifier of the model to retrieve

        Returns
        -------
        dict
            Dictionary containing all stored metadata for the model

        Raises
        ------
        ValueError
            If no model is found with the given ID
        """
        metadata = self.metadata_storage.get_metadata(model_id)
        if not metadata:
            raise ValueError(f"Model not found: {model_id}")
        return metadata