from pydantic import BaseModel
import yaml
from dotenv import load_dotenv
import os 

load_dotenv()

CONFIG_YAML = os.getenv("CONFIG_YAML_PATH", "config/config.yaml")


class ModelConfig(BaseModel):
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    batch_size: int = 32
    normalize: bool = False
    onnx_file: str = "model.onnx"
    
class ServiceConfig(BaseModel):
    cpu:int = 2
    memory:str = "2Gi"
    timeout:int = 30
    interval:int = 10
    max_concurrency:int = 10

class Config(BaseModel):
    model: ModelConfig
    service: ServiceConfig

    def load_from_yaml(self):
        yaml_config = yaml.safe_load(open(CONFIG_YAML))
        model_config = ModelConfig(**yaml_config.get("model", {}))
        service_config = ServiceConfig(**yaml_config.get("service", {}))
        return Config(model=model_config, service=service_config)

def load_config():
    config = Config(model=ModelConfig(), service=ServiceConfig())
    return config.load_from_yaml()