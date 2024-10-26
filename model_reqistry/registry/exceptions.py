"""
Exceptions for the model registry system.

This module defines custom exceptions for handling various error scenarios
in the model registry, storage, and metadata operations.
"""

class RegistryError(Exception):
    """Base exception for all model registry errors."""
    def __init__(self, message: str = "An error occurred in the model registry"):
        self.message = message
        super().__init__(self.message)

class StorageError(RegistryError):
    """
    Exception raised for errors in storage operations.

    Examples:
        - MinIO connection failures
        - File storage/retrieval errors
        - Bucket operations errors
    """
    def __init__(self, message: str = "Storage operation failed"):
        super().__init__(f"Storage error: {message}")

class ModelNotFoundError(RegistryError):
    """
    Exception raised when a requested model is not found.

    Examples:
        - Model file not found in storage
        - Model metadata not found in database
    """
    def __init__(self, model_id: str):
        super().__init__(f"Model not found: {model_id}")

class ValidationError(RegistryError):
    """
    Exception raised for validation errors.

    Examples:
        - Missing required metadata fields
        - Invalid model format
        - Invalid parameters
    """
    def __init__(self, message: str = "Validation failed"):
        super().__init__(f"Validation error: {message}")

class MetadataError(RegistryError):
    """
    Exception raised for metadata-related errors.

    Examples:
        - MongoDB connection failures
        - Metadata storage/retrieval errors
        - Invalid metadata format
    """
    def __init__(self, message: str = "Metadata operation failed"):
        super().__init__(f"Metadata error: {message}")

class DuplicateModelError(RegistryError):
    """
    Exception raised when attempting to register a duplicate model.

    Examples:
        - Same model ID already exists
        - Same name and version combination exists
    """
    def __init__(self, model_info: str):
        super().__init__(f"Duplicate model: {model_info}")

class RegistryConnectionError(RegistryError):
    """
    Exception raised for connection-related errors.

    Examples:
        - Failed to connect to storage service
        - Failed to connect to metadata database
        - Network issues
    """
    def __init__(self, service: str, message: str = "Connection failed"):
        super().__init__(f"Failed to connect to {service}: {message}")

class InvalidOperationError(RegistryError):
    """
    Exception raised for invalid operations on models.

    Examples:
        - Attempting to modify a deprecated model
        - Invalid state transitions
        - Unauthorized operations
    """
    def __init__(self, operation: str, reason: str):
        super().__init__(f"Invalid operation '{operation}': {reason}")

class BucketError(StorageError):
    """
    Exception raised for bucket-related operations.

    Examples:
        - Bucket creation failure
        - Bucket access denied
        - Bucket not found
    """
    def __init__(self, bucket: str, message: str):
        super().__init__(f"Bucket operation failed for '{bucket}': {message}")

class ConfigurationError(RegistryError):
    """
    Exception raised for configuration-related errors.

    Examples:
        - Missing required settings
        - Invalid configuration values
        - Environment setup issues
    """
    def __init__(self, message: str = "Invalid configuration"):
        super().__init__(f"Configuration error: {message}")

# Utility functions for exception handling
def wrap_storage_errors(func):
    """
    Decorator to wrap storage-related errors.
    
    Converts MinIO exceptions to appropriate registry exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, RegistryError):
                raise
            raise StorageError(str(e))
    return wrapper

def wrap_metadata_errors(func):
    """
    Decorator to wrap metadata-related errors.
    
    Converts MongoDB exceptions to appropriate registry exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, RegistryError):
                raise
            raise MetadataError(str(e))
    return wrapper



# Example usage:
"""
try:
    # Storage operations
    model_data = storage.get_model(model_id)
except ModelNotFoundError:
    # Handle missing model
    logger.error(f"Model {model_id} not found")
except StorageError as e:
    # Handle storage errors
    logger.error(f"Storage error: {e}")
except ValidationError as e:
    # Handle validation errors
    logger.error(f"Validation error: {e}")
except RegistryError as e:
    # Handle other registry errors
    logger.error(f"Registry error: {e}")

# Using decorators
@wrap_storage_errors
def store_model(model_data):
    # Storage operations
    pass

@wrap_metadata_errors
def update_metadata(metadata):
    # Metadata operations
    pass
"""