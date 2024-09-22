import omegaconf
from dotenv import dotenv_values
import os

def load_config(env="dev"):
    public_config = omegaconf.OmegaConf.load("config.yaml")

    env_file = ".env.test" if env == "test" else ".env"
    secret_config = omegaconf.DictConfig(dotenv_values(env_file))

    config = omegaconf.OmegaConf.merge(public_config, secret_config)

    return config

# Load the appropriate config based on the FASTAPI_ENV environment variable
config = load_config(os.getenv("FASTAPI_ENV", "test"))

API_V1_PREFIX = config.api_v1_prefix
DB_ASYNC_CONNECTION_STR = config.db_async_connection_string
DB_SYNC_CONNECTION_STR = config.db_sync_connection_string
SECRET_KEY = config.secret_key
ALGORITHM = config.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.access_token_expire_minutes
DB_ECHO = config.db_echo



