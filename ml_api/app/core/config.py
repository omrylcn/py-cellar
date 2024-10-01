from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ML API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Model paths
    CLIP_MODEL_PATH: str = "ml/siglip-base-patch16-224.xml"
    QA_MODEL_PATH: str = "distilbert-base-cased-distilled-squad"
    
    #M
    CLIP_ENABLE: bool = False
    QA_ENABLE: bool = False
    
    PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()