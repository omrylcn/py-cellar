import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import make_url
from api.config import DB_ASYNC_CONNECTION_STR  # Import your database configuration

async def setup_test_database():
    # Parse the existing connection string
    url = make_url(DB_ASYNC_CONNECTION_STR)
    
    # Create a new URL for the test database
    TEST_DB_NAME = f"test_db_{url.database}"
    test_url = url.set(database=url.database)  # Connect to default db first
    
    engine = create_async_engine(str(test_url), isolation_level="AUTOCOMMIT")
    
    async with engine.connect() as conn:
        # Check if the test database already exists
        result = await conn.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
        exists = result.scalar()
        
        if not exists:
            print(f"Creating test database: {TEST_DB_NAME}")
            await conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
        else:
            print(f"Test database {TEST_DB_NAME} already exists")
    
    await engine.dispose()
    print("Test database setup completed")

if __name__ == "__main__":
    asyncio.run(setup_test_database())