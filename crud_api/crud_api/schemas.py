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
        from_attributes = True
        json_schema_extra = {
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
        json_schema_extra = {
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
        json_schema_extra = {
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
    data: str = Field(..., description="The data recorded from the device", example="[42.0, 43.0, 44.0]")
    created_date: datetime = Field(..., description="The date the data was recorded", example="2021-01-01 00:00:00")
    data_type: int = Field(..., description="The type of data recorded", example=0)
    created_user: Optional[str] = Field(description="The username of the user who created this entry", example="admin")
    #updated_user: Optional[str] = Field(None, description="The username of the user who last updated this entry", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "device_unique_id": "1",
                "data": "42.0",
                "created_date": "2021-01-01 00:00:00",
                "data_type": 0,
                "created_user": "admin",
                
            }
        }

class UserDeviceDataUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="The ID of the user", example=1)
    device_unique_id: Optional[str] = Field(None, description="The unique identifier of the device", example="1")
    data: Optional[float] = Field(None, description="The data recorded from the device", example=42.0)
    update_date: datetime = Field(..., description="The date the data was recorded", example="2021-01-01 00:00:00")
    data_type: int = Field(..., description="The type of data recorded", example=0)
    updated_user: Optional[str] = Field(None, description="The username of the user who last updated this entry", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "device_unique_id": "1",
                "data": "42.0",
                "data_type": 1,
                "updated_date": "2021-01-01 00:00:00",
                "updated_user": "admin"
            }
        }

class UserDevicesCreate(BaseModel):
    user_id: int = Field(..., description="The ID of the user", example=1)
    device_unique_id: str = Field(..., description="The unique identifier of the device", example="1")
    created_user: Optional[str] = Field(None, description="The username of the user who created this entry", example="admin")
    #updated_user: Optional[str] = Field(None, description="The username of the user who last updated this entry", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "device_unique_id": "1",
                "created_user": "admin",
            }
        }

class UserDevicesUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="The ID of the user", example=1)
    device_unique_id: Optional[str] = Field(None, description="The unique identifier of the device", example="1")
    updated_user: Optional[str] = Field(None, description="The username of the user who last updated this entry", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "device_unique_id": "1",
                "updated_user": "admin"
            }
        }

class RolesCreate(BaseModel):
    role_name: str = Field(..., description="The name of the role", example="admin")
    created_user: Optional[str] = Field(None, description="The username of the creator", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "admin",
                "created_user": "admin"
            }
        }

class RolesUpdate(BaseModel):
    role_name: Optional[str] = Field(None, description="The name of the role", example="admin")
    updated_user: Optional[str] = Field(None, description="The username of the last updater", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "role_name": "admin",
                "updated_user": "admin"
            }
        }

class UserRolesCreate(BaseModel):
    user_id: int = Field(..., description="The ID of the user", example=1)
    role_id: int = Field(..., description="The ID of the role", example=1)
    created_user: Optional[str] = Field(None, description="The username of the creator", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "role_id": 1,
                "created_user": "admin"
            }
        }

class UserRolesUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="The ID of the user", example=1)
    role_id: Optional[int] = Field(None, description="The ID of the role", example=1)
    updated_user: Optional[str] = Field(None, description="The username of the last updater", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "role_id": 1,
                "updated_user": "admin"
            }
        }

class CompanyCreate(BaseModel):
    company_name: str = Field(..., description="The name of the company", example="ACME")
    is_active: bool = Field(..., description="The company's active status", example=True)
    created_user: Optional[str] = Field(None, description="The username of the creator", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "ACME",
                "is_active": True,
                "created_user": "admin"
            }
        }

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(None, description="The name of the company", example="ACME")
    is_active: Optional[bool] = Field(None, description="The company's active status", example=True)
    updated_user: Optional[str] = Field(None, description="The username of the last updater", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "ACME",
                "is_active": True,
                "updated_user": "admin"
            }
        }


class DeviceCreate(BaseModel):
    unique_id: str = Field(..., description="The unique identifier of the device", example="1")
    manufacturer: str = Field(..., description="The manufacturer of the device", example="ACME")
    created_user: Optional[str] = Field(None, description="The username of the creator", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "unique_id": "1",
                "manufacturer": "ACME",
                "created_user": "admin"
            }
        }

class DeviceUpdate(BaseModel):
    unique_id: Optional[str] = Field(None, description="The unique identifier of the device", example="1")
    manufacturer: Optional[str] = Field(None, description="The manufacturer of the device", example="ACME")
    updated_user: Optional[str] = Field(None, description="The username of the last updater", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "unique_id": "1",
                "manufacturer": "ACME",
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