from minio import Minio
from minio.error import S3Error
from core.config import Settings
import asyncio
from core.logging_config import logger

minio_client = Minio(
    endpoint=Settings.MINIO_ENDPOINT,
    access_key=Settings.MINIO_ROOT_USER,
    secret_key=Settings.MINIO_ROOT_PASSWORD,
    secure=False
)

BUCKET_NAME = Settings.MINIO_BUCKET

async def init_minio():
    try:
        found = await asyncio.to_thread(minio_client.bucket_exists, BUCKET_NAME)
        logger.info(f"Checking for MinIO bucket '{BUCKET_NAME}'")
        if not found:
            await asyncio.to_thread(minio_client.make_bucket, BUCKET_NAME)
            logger.info(f"✅ MinIO bucket '{BUCKET_NAME}' created.")
        else:
            logger.info(f"⚡ MinIO bucket '{BUCKET_NAME}' already exists.")
    except S3Error as e:
        print(f"❌ Error creating bucket: {e}")
