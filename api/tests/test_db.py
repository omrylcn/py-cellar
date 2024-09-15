import pytest
from api.models import Users
from sqlalchemy import inspect,text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# @pytest.mark.asyncio
# async def test_mock(test_engine,create_tables):
#     await create_tables(test_engine)
  

@pytest.mark.asyncio
async def test_tables_exist(create_tables, test_engine):
    await create_tables(test_engine)
    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in result]
        
        assert len(tables) > 0, "No tables were created"
        print(f"Tables found : {tables}")
    
    return True



# @pytest.fixture(scope="function")
# async def async_session(test_engine):
#     async_session = sessionmaker(
#         test_engine, class_=AsyncSession, expire_on_commit=False
#     )
#     async with async_session() as session:
#         yield session
#         await session.rollback()


# @pytest.mark.asyncio
# async def test_add_user(async_session, create_tables, create_user):
#     # Ensure tables are created
    
#    # async with async_session() as session:
#         # Create a new user
#     user = create_user
#     #user.password = hash_password(user.password)  # Hash the password before storing
#     async_session.add(user)
#     await async_session.commit()

# #await create_tables(test_engine)

#     # Create a session
#     #async_session = AsyncSession(test_engine)

#     # user = create_user
#     # #user.password = hash_password(user.password)  # Hash the password before storing
#     # async_session.add(user)
#     # await async_session.commit()
