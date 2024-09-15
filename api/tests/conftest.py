
from datetime import datetime
import pytest
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient


from api.db import db_session
from api.app import app
from api.config import DB_ASYNC_CONNECTION_STR
from api.models import Users
from api.secure import hash_password

import asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,AsyncConnection
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import make_url
from api.config import DB_ASYNC_CONNECTION_STR ,DB_ECHO

url = make_url(DB_ASYNC_CONNECTION_STR)
TEST_DB_ASYNC_CONNECTION_STR = url #url.set(database="test_" + url.database)

# Import your database configuration
engine = create_async_engine(TEST_DB_ASYNC_CONNECTION_STR, echo=DB_ECHO)


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(TEST_DB_ASYNC_CONNECTION_STR, echo=DB_ECHO)
    yield engine
    engine.dispose()


async def create_db_and_tables(engine):
    async with engine.begin() as conn:
        #await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        

@pytest.fixture(scope="session")
def create_tables():
    return create_db_and_tables


@pytest.fixture(scope="session")
def create_user():
     new_user = Users(
            name = f'test_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            surname= "test_surname",
            username="test_username",
            password="test_password", # need hash
            created_date= datetime.now(),
            created_user="test_admim",
        )
     
     return new_user






