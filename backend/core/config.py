import os
from dotenv import load_dotenv
from pathlib import Path

from sqlalchemy.testing.config import db_url

env_path = Path ('.') / '.env'

load_dotenv(dotenv_path=env_path)

class Settings:
    """
    This class handles the basic configurations for the system
    """

    PROJECT_NAME = "Invensys"
    PROJECT_VERSION = "1.0.0"

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB = os.getenv("DB")
    DB_PORT = os.getenv("DB_PORT")
    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB}"
    SYNC_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB}"

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRY_MINUTES = 30.0

    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
    MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET")

    FILESCAN_API_KEY = os.getenv("FILESCAN_API_KEY")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()



