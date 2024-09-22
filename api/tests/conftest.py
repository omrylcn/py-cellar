# conftest.py
from datetime import datetime
import pytest
from sqlmodel import SQLModel, Session
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import database_exists, create_database

from api.config import DB_SYNC_CONNECTION_STR, DB_ECHO
from api.models import Users
from api.secure import hash_password

# Create test database URL
# sync_url = make_url(DB_SYNC_CONNECTION_STR)
TEST_DB_SYNC_CONNECTION_STR =  DB_SYNC_CONNECTION_STR

@pytest.fixture(scope="session")
def test_engine() -> Engine:
   # url = make_url(TEST_DB_SYNC_CONNECTION_STR)
    
    # Create database if it doesn't exist
    if not database_exists(TEST_DB_SYNC_CONNECTION_STR):
        create_database(TEST_DB_SYNC_CONNECTION_STR)
    
    engine = create_engine(TEST_DB_SYNC_CONNECTION_STR, echo=DB_ECHO)
    
    # Verify connection
    try:
        with engine.connect() as conn:
            pass
    except OperationalError:
        pytest.fail(f"Could not connect to the test database: {TEST_DB_SYNC_CONNECTION_STR}")

    yield engine

    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="session", autouse=True)
def create_tables(test_engine: Engine):
    SQLModel.metadata.create_all(test_engine)

@pytest.fixture(scope="session")
def test_session_factory(test_engine: Engine):
    return sessionmaker(bind=test_engine, class_=Session, expire_on_commit=False)

@pytest.fixture(scope="function")
def db_session(test_session_factory) -> Session:
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()



@pytest.fixture(scope="function")
def create_test_user(db_session: Session) -> Users:
    user = Users(
        name="Test",
        surname="User",
        username="testuser",
        password=hash_password("testpassword"),
        created_date=datetime.utcnow(),
        created_user="system",
        updated_date=datetime.utcnow(),
        updated_user="system"
    )
    return user


