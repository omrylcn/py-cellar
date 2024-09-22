# test_db.py
import pytest
from api.models import Users, UserData
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from datetime import datetime



def test_database_connection(db_session):
    try:
        # Execute a simple query
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Database connection test failed"
    except Exception as e:
        pytest.fail(f"Database connection test failed: {str(e)}")


def test_tables_exist(test_engine):
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()

    assert len(tables) > 0, "No tables were created"
    print(f"Tables found: {tables}")
    
    # Check for specific tables
    expected_tables = ["users", "userdata"]  # Adjust if your table names are different
    for table in expected_tables:
        assert table in tables, f"Table '{table}' not found in the database"

def test_create_user(db_session: Session,create_test_user:Users):
    new_user = create_test_user
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    assert new_user.id is not None, "User was not created successfully"
    
    # Fetch the user from the database to ensure it was saved
    fetched_user = db_session.query(Users).filter(Users.username == new_user.username).first()
    assert fetched_user is not None, "User not found in the database"
    assert fetched_user.name == new_user.name, "User name does not match"
    assert fetched_user.surname == new_user.surname, "User surname does not match"

def test_user_table_columns(test_engine):
    inspector = inspect(test_engine)
    columns = inspector.get_columns("users")
    column_names = [col["name"] for col in columns]
    
    expected_columns = ["id", "name", "surname", "username", "password", "created_date", "created_user", "updated_date", "updated_user"]
    for col in expected_columns:
        assert col in column_names, f"Column '{col}' not found in users table"


def test_user_data_table_columns(test_engine):
    inspector = inspect(test_engine)
    columns = inspector.get_columns("userdata")
    column_names = [col["name"] for col in columns]

    expected_columns = ["id", "user_id", "data", "created_date", "created_user", "updated_date", "updated_user"]
    for col in expected_columns:
        assert col in column_names, f"Column '{col}' not found in userdata table"


def test_user_data_creation(db_session: Session, create_test_user_data: UserData):
    new_user_data = create_test_user_data
    db_session.add(new_user_data)
    db_session.commit()
    db_session.refresh(new_user_data)

    assert new_user_data.id is not None, "User data was not created successfully"
    # Fetch the user data from the database to ensure it was saved
    fetched_user_data = db_session.query(UserData).filter(UserData.user_id == new_user_data.user_id).first()
    assert fetched_user_data is not None, "User data not found in the database"
    assert fetched_user_data.data == new_user_data.data, "User data does not match"
    