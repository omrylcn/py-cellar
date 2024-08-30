from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    surname: str
    username: str = Field(index=True, unique=True)  # This ensures usernames are unique
    password: str
    created_date: datetime #= Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime  # = Field(default_factory=datetime.utcnow)
    updated_user: str




class UserData(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    data: str  # Can be any data type you need (float, JSON, etc.)
    data_type: int
    created_date: datetime #= Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime #= Field(default_factory=datetime.utcnow)
    updated_user: str

