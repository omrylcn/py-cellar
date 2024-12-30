from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_PORT: int = 8000
    API_HOST: str = '0.0.0.0'

    MODEL_PATH: str = "models/candy-8.onnx"
    MODEL_SIZE: int = 224
    
    # RabbitMQ configuration
    RABBITMQ_USER: str = 'guest'
    RABBITMQ_PASSWORD: str = 'guest'
    RABBITMQ_HOST: str = 'rabbitmq'
    RABBITMQ_PORT: int = 5672
    RABBITMQ_MANAGEMENT_PORT: int = 15672
    
    
    # Redis configuration
    REDIS_HOST: str = 'redis'
    REDIS_PASSWORD: str = ''
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    
    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"

settings = Settings()