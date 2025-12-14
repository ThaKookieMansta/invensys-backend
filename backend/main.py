from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine
from db.sessions import engine
from db.base import Base
from core.config import Settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.seed import seed_data, safe_seed_data
from apis.base import api_router
from core.minio_client import init_minio
from core.logging_config import logger
from fastapi.middleware.cors import CORSMiddleware


async def init_models():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database Models initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database models")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"{Settings.PROJECT_NAME} (ver: {Settings.PROJECT_VERSION}) Application starting up")
    try:
        await init_models()
        await safe_seed_data()
        await init_minio()
        logger.info("Startup tasks completed successfully.")
    except Exception as e:
        logger.critical(f"Startup Failed")
        raise

    yield

    logger.info(
        f"{Settings.PROJECT_NAME} (ver: {Settings.PROJECT_VERSION}) Application shutting down")


app = FastAPI(title=Settings.PROJECT_NAME, version=Settings.PROJECT_VERSION,
              lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
