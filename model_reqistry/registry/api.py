"""
REST API endpoints for the Model Registry service.

This module provides FastAPI routes for interacting with the model registry,
including uploading models and their metadata.

Notes
-----
The API uses FastAPI for routing and request handling, and supports
multipart/form-data for file uploads along with JSON metadata.
"""

import io
from fastapi import FastAPI
from fastapi import APIRouter, File, UploadFile, HTTPException
from .schemas import ModelMetadata, ModelResponse
from .storage.minio import MinioStorage
from .storage.mongo import MongoStorage
from .registry import ModelRegistry

app = FastAPI()
registry = ModelRegistry()

@app.get("/")
async def root():
    """
    Root endpoint to verify API health.

    Returns
    -------
    dict
        A simple hello message indicating the service is running

    Examples
    --------
    >>> curl http://localhost:8000/
    {"Hello from Model Registry"}
    """
    return {"Hello from Model Registry"}

@app.post("/models/upload", response_model=ModelResponse)
async def upload_model(
    metadata: ModelMetadata,
    model_file: UploadFile = File(...)
):
    """
    Upload a model file with its metadata.

    This endpoint accepts a model file and its metadata as a multipart/form-data 
    request. The model file is stored in MinIO and its metadata in MongoDB.

    Parameters
    ----------
    metadata : ModelMetadata
        Model metadata including:
        
        - id : str
            Unique identifier for the model
        - name : str
            Name of the model
        - version : str
            Version of the model
        - file_extension : str
            File extension of the model file
        - storage_group : str
            Name of the storage bucket
        - description : str, optional
            Model description
        - framework : str, optional
            ML framework used
        - metrics : dict, optional
            Model performance metrics
        - parameters : dict, optional
            Model parameters
    
    model_file : UploadFile
        The model file to upload

    Returns
    -------
    ModelResponse
        Response object containing:
        
        - name : str
            Name of the model
        - version : str
            Version of the model
        - storage_path : str
            Path where the model is stored
        - created_at : datetime
            Timestamp of registration
        - metrics : dict, optional
            Model performance metrics
        - description : str, optional
            Model description

    Raises
    ------
    HTTPException
        500 error if model registration fails

    Examples
    --------
    Using curl:
    
    >>> curl -X POST "http://localhost:8000/models/upload" \
    ...     -H "Content-Type: multipart/form-data" \
    ...     -F "model_file=@model.pkl" \
    ...     -F 'metadata={
    ...         "id": "model-123",
    ...         "name": "sentiment-model",
    ...         "version": "1.0.0",
    ...         "file_extension": "pkl",
    ...         "storage_group": "nlp-models"
    ...     }'

    Using Python requests:
    
    >>> import requests
    >>> files = {
    ...     'model_file': open('model.pkl', 'rb'),
    ...     'metadata': {
    ...         'id': 'model-123',
    ...         'name': 'sentiment-model',
    ...         'version': '1.0.0',
    ...         'file_extension': 'pkl',
    ...         'storage_group': 'nlp-models'
    ...     }
    ... }
    >>> response = requests.post(
    ...     "http://localhost:8000/models/upload",
    ...     files=files
    ... )

    Notes
    -----
    The endpoint expects a multipart/form-data request with two parts:
    1. metadata: A JSON object containing model metadata
    2. model_file: The actual model file to upload

    The model file size limit depends on your FastAPI configuration.
    """
    content = await model_file.read()
    file_obj = io.BytesIO(content)
    
    try:
        return registry.register_model(
            model_file=file_obj,
            metadata=metadata.model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )