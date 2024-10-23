from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource
)
from pydantic import Field
from typing import Tuple, Type

CONFIG_YAML_PATH = "config/registry.yaml"

class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="Registry")
    PROJECT_VERSION: str = Field(default="0.0.0")
    PORT: int = Field(default=8000)
    
    #logger
    LOG_LEVEL: str = Field(default="INFO")
    LOGGER_HANDLER: str = Field(default="file")
    LOG_DIR: str = Field(default="logs")

    #minio
    MINIO_ENDPOINT: str = Field(default="localhost")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_BUCKET: str = Field(default="models")
    
    #mongo db
    MONGODB_PORT:int = Field(default=27017)
    MONGODB_ROOT_USERNAME: str = Field(default="root")
    MONGODB_ROOT_PASSWORD: str = Field(default="root")
    MONGODB_HOST: str = Field(default="localhost")
    MONGODB_DB: str = Field(default="metadata")
    MONGODB_URL:str = Field(default="mongodb://root:root@localhost:27017")
    #MONGODB_URL: str = Field(default="mongodb://root:example@localhost:27017")


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
        return (      
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            init_settings,
            file_secret_settings,
        )

settings = Settings()
