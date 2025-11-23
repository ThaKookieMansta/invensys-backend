# from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy import create_engine
from typing import Generator, AsyncGenerator

from core.config import Settings

DB_URL = Settings.DB_URL
engine = create_async_engine(DB_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
