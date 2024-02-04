from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UserResponse(BaseModel):
    id: Optional[int] = Field(None, description="The user ID", example=123)
    name: str = Field(..., description="The user's name", example="John")
    surname: str = Field(..., description="The user's surname", example="Doe")
    username: str = Field(..., description="The user's username", example="johndoe")
    password: Optional[str] = Field(None, description="The user's password", example="secret")
    created_date: Optional[datetime] = Field(default_factory=datetime.utcnow, description="The date the user was created")
    created_user: Optional[str] = Field(None, description="The username of the creator", example="admin")
    updated_date: Optional[datetime] = Field(default_factory=datetime.utcnow, description="The date the user was last updated")
    updated_user: Optional[str] = Field(None, description="The username of the last updater", example="admin")
    company_id: Optional[int] = Field(None, description="The company ID associated with the user", example=1)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "username": "johndoe",
                "password": "secret",
                "created_user": "admin",
                "updated_user": "admin",
                "company_id": 1
            }
        }


class UserCreate(BaseModel):
    name: str = Field(..., description="The user's name", example="John")
    surname: str = Field(..., description="The user's surname", example="Doe")
    username: str = Field(..., description="The user's username", example="johndoe")
    password: str = Field(..., description="The user's password", example="secret")
    created_user: Optional[str] = Field(None, description="The username of the creator", example="admin")
    company_id: Optional[int] = Field(None, description="The company ID associated with the user", example=1)

    class Config:
        schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "username": "johndoe",
                "password": "secret",
                "created_user": "admin",
                "updated_user": "admin",
                "company_id": 1
            }
        }

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The user's name", example="John")
    surname: Optional[str] = Field(None, description="The user's surname", example="Doe")
    username: Optional[str] = Field(None, description="The user's username", example="johndoe")
    password: Optional[str] = Field(None, description="The user's password", example="secret")
    updated_user: Optional[str] = Field(None, description="The username of the last updater", example="admin")
    company_id: Optional[int] = Field(None, description="The company ID associated with the user", example=1)

    class Config:
        schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",
                "username": "johndoe",
                "password": "secret",
                "updated_user": "admin",
                "company_id": 1
            }
        }

class UserDeviceDataCreate(BaseModel):
    user_id: int = Field(..., description="The ID of the user", example=1)
    device_unique_id: str = Field(..., description="The unique identifier of the device", example="1")
    data: float = Field(..., description="The data recorded from the device", example=42.0)
    created_user: Optional[str] = Field(None, description="The username of the user who created this entry", example="admin")
    #updated_user: Optional[str] = Field(None, description="The username of the user who last updated this entry", example="admin")

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "device_unique_id": "1",
                "data": 42.0,
                "created_user": "admin",
            }
        }

class UserDeviceDataUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="The ID of the user", example=1)
    device_unique_id: Optional[str] = Field(None, description="The unique identifier of the device", example="1")
    data: Optional[float] = Field(None, description="The data recorded from the device", example=42.0)
    updated_user: Optional[str] = Field(None, description="The username of the user who last updated this entry", example="admin")

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "device_unique_id": "1",
                "data": 42.0,
                "updated_user": "admin"
            }
        }


# # schemas.py
# from pydantic import BaseModel

# class UserCreate(BaseModel):
#     username: str
#     password: str

# class UserLogin(BaseModel):
#     username: str
#     password: str

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: Optional[str] = None