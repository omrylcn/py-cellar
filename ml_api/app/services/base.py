from abc import ABC, abstractmethod
from pydantic_settings import BaseSettings
from pydantic import Field,BaseModel

class ModelSettings(BaseModel):
    MODEL_NAME: str = Field(..., description="Name of the model")
    MODEL_VERSION: str= Field(..., description="Version of the model")
    MODEL_TAG: str = Field(..., description="Tag of the model")


class AbstractModelService(ABC):
    def __init__(self):
        self.settings = None
        self.storage = None
        self.bucket_name = None
    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def predict(self, *args, **kwargs):
        pass

    @abstractmethod
    def _store_prediction(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def get_prediction(self, *args, **kwargs):
        pass