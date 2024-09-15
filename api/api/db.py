from typing import AsyncGenerator

from api.config import DB_ASYNC_CONNECTION_STR,DB_ECHO
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = create_async_engine(DB_ASYNC_CONNECTION_STR, echo=DB_ECHO, future=True)


async def db_session() -> AsyncGenerator:
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session