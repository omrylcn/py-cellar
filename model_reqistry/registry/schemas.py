from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ModelMetadata(BaseModel):
    """
    Pydantic model for ML model metadata validation.

    Parameters
    ----------
    id : str
        Unique identifier for the model
    name : str
        Name of the model
    file_extension : str
        File extension of the model file (e.g., 'pkl', 'h5')
    storage_group : str
        Name of storage location (bucket name for MinIO)
    version : str
        Version of the model
    description : str, optional
        Description of the model
    framework : str, optional
        ML framework used (e.g., 'pytorch', 'tensorflow')
    metrics : dict, optional
        Dictionary of model performance metrics
    parameters : dict, optional
        Dictionary of model parameters and hyperparameters
    """

    id: str
    name: str
    file_extension: str
    storage_group: str = Field(..., description="Name of storage like bucket name for minio")
    version: str = Field(..., description="Version of the model")
    description: Optional[str] = None
    framework: str = None
    metrics: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


class ModelResponse(BaseModel):
    """
    Pydantic model for model registration response.

    Parameters
    ----------
    id : str
        Unique identifier for the model response
    name : str
        Name of the model
    version : str
        Version of the model
    metadata_id : str
        ID reference to the associated model metadata
    storage_group : str
        Name of storage location (bucket name for MinIO)
    storage_path : str
        Path where the model file is stored
    created_at : datetime
        Timestamp when the model was registered
    description : str, optional
        Description of the model
    framework : str, optional
        ML framework used (e.g., 'pytorch', 'tensorflow')
    """

    id: str
    name: str
    version: str
    metadata_id: str
    storage_group: str
    storage_path: str
    created_at: datetime
    description: Optional[str] = None
    framework: Optional[str] = None


class GetMetadataModelResponse(BaseModel):
    """
    Pydantic model for model registration response.

    Parameters
    ----------
    id : str
        Unique identifier for the model response
    name : str
        Name of the model
    version : str
        Version of the model
    metadata_id : str
        ID reference to the associated model metadata
    storage_group : str
        Name of storage location (bucket name for MinIO)
    storage_path : str
        Path where the model file is stored
    registration_time : datetime
        Timestamp when the model was registered
    description : str, optional
        Description of the model
    framework : str, optional
        ML framework used (e.g., 'pytorch', 'tensorflow')
    file_extension : str
        File extension of the model file
    metrics : dict
        Dictionary of model performance metrics
    parameters : dict
        Dictionary of model parameters
    storage_info : dict
        Dictionary containing storage information
    """

    id: str
    name: str
    file_extension: str
    storage_group: str
    version: str
    metadata_id: str
    storage_info: dict
    storage_path: str
    registration_time: datetime
    description: Optional[str] = None
    framework: str = None
    metrics: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


class ModelInfo(BaseModel):
    """Model information returned after registration"""

    metadata_id: str
    storage_path: str
    storage_info: Dict[str, Any]
    registration_time: datetime
