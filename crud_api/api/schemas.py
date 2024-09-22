from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserCreate(BaseModel):
    name: str = Field(..., description="The user's name", example="John")
    surname: str = Field(..., description="The user's surname", example="Doe")
    username: str = Field(..., description="The user's username", example="johndoe")
    password: str = Field(..., description="The user's password", example="secret")
    created_user: Optional[str] = Field(None, description="The username of the creator", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "username": "johndoe",
                "password": "secret",
                "created_user": "admin",
                "updated_user": "admin",
            }
        }


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The user's name", example="John")
    surname: Optional[str] = Field(None, description="The user's surname", example="Doe")
    username: Optional[str] = Field(None, description="The user's username", example="johndoe")
    password: Optional[str] = Field(None, description="The user's password", example="secret")
    updated_user: Optional[str] = Field(None, description="The username of the last updater", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "username": "johndoe",
                "password": "secret",
                "updated_user": "admin",
            }
        }


class UserResponse(BaseModel):
    id: Optional[int] = Field(None, description="The user ID", example=123)
    name: str = Field(..., description="The user's name", example="John")
    surname: str = Field(..., description="The user's surname", example="Doe")
    username: str = Field(..., description="The user's username", example="johndoe")
    password: Optional[str] = Field(None, description="The user's password", example="secret")
    created_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="The date the user was created"
    )
    created_user: Optional[str] = Field(None, description="The username of the creator", example="admin")
    updated_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="The date the user was last updated"
    )
    updated_user: Optional[str] = Field(None, description="The username of the last updater", example="admin")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "username": "johndoe",
                "password": "secret",
                "created_user": "admin",
                "updated_user": "admin",
            }
        }


class UserDataCreate(BaseModel):
    user_id: int = Field(..., description="The ID of the user", example=1)
    data: str = Field(..., description="The data recorded from the device", example="[42.0, 43.0, 44.0]")
    data_type: int = Field(..., description="The type of data recorded", example=0)
    created_user: Optional[str] = Field(description="The username of the user who created this entry", example="admin")
    created_date: datetime = Field(
        ..., description="The date the user data was created", example="2022-01-01T00:00:00Z"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "data": "[42.0, 43.0, 44.0]",
                "data_type": 0,
                "created_user": "admin",
                "created_date": "2022-01-01T00:00:00Z",
            }
        }


class UserDataUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="The ID of the user", example=1)
    data: Optional[str] = Field(None, description="The data recorded from the device", example="42.0")
    data_type: Optional[int] = Field(None, description="The type of data recorded", example=0)
    updated_user: Optional[str] = Field(
        None, description="The username of the user who last updated this entry", example="admin"
    )
    updated_date: Optional[datetime] = Field(
        None, description="The date the user data was last updated", example="2022-01-01T00:00:00Z"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "data": "42.0",
                "data_type": 1,
                "updated_user": "admin",
                "updated_date": "2022-01-01T00:00:00Z",
            }
        }


class UserDataResponse(BaseModel):
    id: int
    user_id: int
    data: str
    data_type: int
    created_date: datetime
    created_user: str
    updated_date: datetime
    updated_user: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "data": "[42.0, 43.0, 44.0]",
                "data_type": 0,
                "created_date": "2022-01-01T00:00:00Z",
                "created_user": "admin",
                "updated_date": "2022-01-01T00:00:00Z",
                "updated_user": "admin",
            }
        }
