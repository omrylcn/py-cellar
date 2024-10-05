from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource
)
from pydantic import Field
from typing import Tuple, Type

CONFIG_YAML_PATH = "config/config.yaml"

class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="ML API_0")
    PROJECT_VERSION: str = Field(default="0.0.0")
    PORT: int = Field(default=8000)
    MINIO_ENDPOINT: str = Field(default="localhost")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    
    
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

# Explanation of configuration priority (highest to lowest):
# 1. Environment variables
# 2. .env file
# 3. YAML config file
# 4. Initialization values
# 5. File secrets
# 6. Default values in Field() (if no other source provides a value)