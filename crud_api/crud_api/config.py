import omegaconf

config = omegaconf.OmegaConf.load("config.yaml")


API_V1_PREFIX = "/api/v1"
# db_connection_string = "postgresql://admin:admin123@localhost:5432/invamar"
DB_ASYNC_CONNECTION_STR=config.db_connection_string#"postgresql+asyncpg://admin:admin123@localhost:5432/invamar"#"postgresql+asyncpg://hero:heroPass123@0.0.0.0:5436/heroes_db"
DB_ECHO = False

# secure.py
SECRET_KEY = config.secret_key
ALGORITHM = config.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REST_PASSWORD_TOKEN_EXPIRE_MINUTES = 10
SENDER_EMAIL = config.sender_email
SENDER_EMAIL_PASSWORD = config.email_password