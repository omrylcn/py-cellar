from typing import Optional, Dict, Any, Tuple, BinaryIO, Union
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
import json
import io

from .schemas import ModelMetadata, ModelInfo
from .logger import logger


class RegistryClientError(Exception):
    """
    Base exception for registry client errors.

    This exception is raised when general registry operations fail.

    Parameters
    ----------
    message : str
        The error message describing what went wrong.
    """

    def __init__(self, message: str):
        super().__init__(message)
        logger.error(f"Registry error: {message}")


class ModelNotFoundError(RegistryClientError):
    """
    Exception raised when a requested model cannot be found in the registry.

    This is a specific type of RegistryClientError used to indicate that
    the requested model does not exist in the system.
    """

    pass


class RegistryConnectionError(RegistryClientError):
    """
    Exception raised when connection to the registry service fails.

    This error indicates network connectivity issues or service unavailability.
    """

    pass


class ModelUploadError(RegistryClientError):
    """
    Exception raised when model upload operation fails.

    This error is used for any failures during the model upload process,
    including network issues or invalid model data.
    """

    pass


class MetadataDownloadError(RegistryClientError):
    """
    Exception raised when model metadata retrieval fails.

    This error indicates failures in retrieving or parsing model metadata.
    """

    pass


class ModelFileDownloadError(RegistryClientError):
    """
    Exception raised when downloading model files fails.

    This error indicates failures in downloading model files from the registry,
    including network issues, invalid file paths, or insufficient permissions.
    """

    pass


class ModelRegistryClient:
    """
    Client for interacting with the Model Registry API.

    This class provides methods for uploading, downloading, and managing machine
    learning models and their associated metadata in a registry service.

    Parameters
    ----------
    base_url : str
        The base URL of the registry service.
    timeout : int, optional
        Request timeout in seconds. Default is 30.
    max_retries : int, optional
        Maximum number of retry attempts for failed requests. Default is 3.

    Attributes
    ----------
    base_url : str
        The base URL of the registry service.
    timeout : int
        Request timeout in seconds.
    session : requests.Session
        HTTP session used for making requests.

    Raises
    ------
    ValueError
        If base_url is empty, timeout is not positive, or max_retries is negative.

    Notes
    -----
    The client implements automatic retry logic for failed requests and
    provides comprehensive error handling.

    Examples
    --------
    >>> client = ModelRegistryClient("http://registry-service.com", timeout=60)
    >>> is_healthy = client.health_check()
    >>> print(f"Service health status: {is_healthy}")
    """

    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        if not base_url:
            raise ValueError("base_url cannot be empty")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(f"Initialized registry client with base URL: {base_url}")

    def health_check(self) -> bool:
        """
        Check if the registry service is healthy.

        Returns
        -------
        bool
            True if service is healthy, False otherwise.

        Raises
        ------
        RegistryConnectionError
            If connection to registry fails.

        Examples
        --------
        >>> client = ModelRegistryClient("http://registry-service.com")
        >>> try:
        ...     is_healthy = client.health_check()
        ...     print(f"Service is {'healthy' if is_healthy else 'unhealthy'}")
        ... except RegistryConnectionError as e:
        ...     print(f"Connection failed: {e}")
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            is_healthy = response.json()["status"] == "healthy"
            logger.info(f"Health check status: {'healthy' if is_healthy else 'unhealthy'}")
            return is_healthy
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {str(e)}")
            raise RegistryConnectionError(f"Failed to connect to registry: {str(e)}")

    def upload_model(
        self, model_buffer: Union[BinaryIO, bytes, io.BytesIO], metadata: ModelMetadata, filename: Optional[str] = None
    ) -> ModelInfo:
        """
        Upload a model to the registry.

        Parameters
        ----------
        model_buffer : Union[BinaryIO, bytes, io.BytesIO]
            Buffer containing the model file data.
        metadata : ModelMetadata
            Metadata associated with the model.
        filename : str, optional
            Name for the uploaded file. If not provided, generated from metadata.

        Returns
        -------
        ModelInfo
            Information about the uploaded model including its location and metadata.

        Raises
        ------
        ModelUploadError
            If the upload operation fails.

        Notes
        -----
        The model buffer will be reset to position 0 before upload if it supports seeking.

        Examples
        --------
        >>> with open('model.pkl', 'rb') as f:
        ...     metadata = ModelMetadata(name='mymodel', version='1.0')
        ...     info = client.upload_model(f, metadata)
        >>> print(f"Model uploaded with ID: {info.metadata_id}")
        """

        try:
            model_buffer.seek(0)
            if not filename:
                filename = f"{metadata.name}.{metadata.file_extension}"

            files = {"model_file": (filename, model_buffer, "application/octet-stream")}
            data = {"metadata": metadata.model_dump_json()}

            logger.info(f"Uploading model: {filename}")
            response = self.session.post(f"{self.base_url}/model/upload", files=files, data=data, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Successfully uploaded model: {filename}")
            return ModelInfo(
                name=result["name"],
                version=result["version"],
                metadata_id=result["metadata_id"],
                file_path=result["storage_path"],
                storage_group=result["storage_group"],
                registration_time=result["created_at"],
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload model: {str(e)}")
            raise ModelUploadError(f"Failed to upload model: {str(e)}")

    def get_metadata(self, metadata_id: str) -> Dict[str, Any]:
        """
        Retrieve metadata for a model.

        Parameters
        ----------
        metadata_id : str
            Unique identifier for the model metadata.

        Returns
        -------
        dict
            Dictionary containing model metadata.

        Raises
        ------
        MetadataDownloadError
            If metadata retrieval fails.

        Examples
        --------
        >>> try:
        ...     metadata = client.get_metadata("model123")
        ...     print(f"Model name: {metadata['name']}")
        ... except MetadataDownloadError as e:
        ...     print(f"Failed to get metadata: {e}")
        """
        try:
            logger.info(f"Retrieving metadata: {metadata_id}")
            response = self.session.get(f"{self.base_url}/model/metadata/{metadata_id}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get model metadata: {str(e)}")
            raise MetadataDownloadError(f"Failed to get model metadata: {str(e)}")

    def get_model_file(self, file_path: str, bucket_name: str) -> io.BytesIO:
        """
        Download a model file from storage.

        Parameters
        ----------
        file_path : str
            Path to the model file in storage.
        bucket_name : str
            Name of the storage bucket containing the model.

        Returns
        -------
        io.BytesIO
            Buffer containing the downloaded model file.

        Raises
        ------
        RegistryClientError
            If file download fails.

        Notes
        -----
        The downloaded file is streamed in chunks to handle large files efficiently.

        Examples
        --------
        >>> buffer = client.get_model_file("models/mymodel.pkl", "models-bucket")
        >>> with open('downloaded_model.pkl', 'wb') as f:
        ...     f.write(buffer.getvalue())
        """
        try:
            logger.info(f"Retrieving model file: {file_path}")
            params = {"bucket_name": bucket_name}
            response = self.session.get(
                f"{self.base_url}/model/file/{file_path}", params=params, stream=True, timeout=self.timeout
            )
            response.raise_for_status()

            buffer = io.BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                buffer.write(chunk)
            buffer.seek(0)

            return buffer
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve model file: {str(e)}", exc_info=True)
            raise ModelFileDownloadError(f"Failed to retrieve model file: {str(e)}")

    def get_model(
        self, file_path: str, metadata_id: str, bucket_name: Optional[str] = None
    ) -> Tuple[io.BytesIO, Dict[str, Any]]:
        """
        Retrieve a model and its metadata from the registry.

        Parameters
        ----------
        file_path : str
            Path to the model file in storage.
        metadata_id : str
            Unique identifier for the model metadata.
        bucket_name : str, optional
            Storage bucket name. If not provided, extracted from metadata.

        Returns
        -------
        tuple
            A tuple containing:
            - io.BytesIO: Buffer containing the model file
            - dict: Model metadata dictionary

        Raises
        ------
        ModelNotFoundError
            If the requested model is not found.
        RegistryClientError
            If model retrieval fails for other reasons.
        MetadataDownloadError
            If metadata retrieval fails.

        See Also
        --------
        get_metadata : Get only the model metadata
        get_model_file : Get only the model file

        Examples
        --------
        >>> try:
        ...     buffer, metadata = client.get_model("models/mymodel.pkl", "model123")
        ...     print(f"Downloaded model version: {metadata['version']}")
        ... except ModelNotFoundError:
        ...     print("Model not found")
        """
        try:
            # Get metadata first
            metadata = self.get_metadata(metadata_id=metadata_id)

            # Use provided bucket name or fall back to storage group from metadata
            bucket_name = bucket_name or metadata.get("storage_group")
            if not bucket_name:
                raise RegistryClientError("No bucket name provided and no storage group in metadata")

            # Get model file
            buffer = self.get_model_file(file_path=file_path, bucket_name=bucket_name)

            logger.info(f"Successfully retrieved model: {file_path}")
            return buffer, metadata

        except MetadataDownloadError:
            raise

        except ModelFileDownloadError:
            raise

        except Exception as e:
            logger.error(f"Failed to retrieve model: {str(e)}")
            raise RegistryClientError(f"Failed to retrieve model: {str(e)}")
