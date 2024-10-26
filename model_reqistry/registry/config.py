from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings import PydanticBaseSettingsSource, YamlConfigSettingsSource
from pydantic import Field
from typing import Tuple, Type

CONFIG_YAML_PATH = "config/registry.yaml"

class Settings(BaseSettings):
    """
    Configuration settings for the model registry.

    This class uses Pydantic settings management to handle configuration from
    multiple sources including environment variables and YAML files.

    Parameters
    ----------
    PROJECT_NAME : str
        Name of the project
    PROJECT_VERSION : str
        Version of the project
    PORT : int
        Port number for the service
    LOG_LEVEL : str
        Logging level (e.g., 'INFO', 'DEBUG')
    LOGGER_HANDLER : str
        Type of logger handler to use
    LOG_DIR : str
        Directory for log files
    MINIO_ENDPOINT : str
        MinIO server endpoint
    MINIO_ACCESS_KEY : str
        MinIO access key
    MINIO_SECRET_KEY : str
        MinIO secret key
    MINIO_BUCKET : str
        Default MinIO bucket name
    MONGODB_PORT : int
        MongoDB server port
    MONGODB_ROOT_USERNAME : str
        MongoDB root username
    MONGODB_ROOT_PASSWORD : str
        MongoDB root password
    MONGODB_HOST : str
        MongoDB server host
    MONGODB_DB : str
        MongoDB database name
    MONGODB_URL : str
        Complete MongoDB connection URL

    Notes
    -----
    Configuration is loaded from multiple sources in the following order:
    1. Environment variables
    2. .env file
    3. YAML config file
    4. Default values
    """
    PROJECT_NAME: str = Field(default="Registry")
    PROJECT_VERSION: str = Field(default="0.0.0")
    PORT: int = Field(default=8000)
    
    LOGGER_NAME: str = Field(default="registry")
    LOG_LEVEL: str = Field(default="INFO")
    LOGGER_HANDLER: str = Field(default="file")
    LOG_DIR: str = Field(default="logs")

    MINIO_ENDPOINT: str = Field(default="localhost")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_BUCKET: str = Field(default="models")
    
    MONGODB_PORT: int = Field(default=27017)
    MONGODB_ROOT_USERNAME: str = Field(default="root")
    MONGODB_ROOT_PASSWORD: str = Field(default="root")
    MONGODB_HOST: str = Field(default="localhost")
    MONGODB_DB: str = Field(default="metadata")
    MONGODB_URL: str = Field(default="mongodb://root:root@localhost:27017")

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="allow",
        yaml_file=CONFIG_YAML_PATH,
        case_sensitive=True
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize the configuration sources priority.

        Returns
        -------
        tuple
            Tuple of configuration sources in priority order
        """
        return (      
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            init_settings,
            file_secret_settings,
        )

settings = Settings()