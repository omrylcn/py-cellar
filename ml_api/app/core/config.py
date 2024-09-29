from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ML API"
    PROJECT_VERSION: str = "1.0.0"
    MODEL_PATH: str = "ml/siglip-base-patch16-224.xml"
    PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()