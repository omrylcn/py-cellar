from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    surname: str
    username: str #  Field(index=True, unique=True)  # This ensures usernames are unique
    password: str
    created_date: datetime #= Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime # = Field(default_factory=datetime.utcnow)
    updated_user: str
    company_id: Optional[int] = Field(foreign_key="company.id")

class Roles(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    role_name: str
    created_date: datetime #= Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime #= Field(default_factory=datetime.utcnow)
    updated_user: str

class UserRoles(SQLModel,table=True):
    __tablename__ = "user_roles"
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    role_id: int = Field(foreign_key="roles.id")
    created_date: datetime #= Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime #= Field(default_factory=datetime.utcnow)
    updated_user: str

class Company(SQLModel, table=True):
    __tablename__ = "company"
    id: int = Field(default=None, primary_key=True)
    company_name: str
    is_active: bool
    created_date: datetime #= Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime #= Field(default_factory=datetime.utcnow)
    updated_user: str

class Device(SQLModel,table=True):
    __tablename__ = "device"
    unique_id: str = Field(default=None, primary_key=True)
    manufacturer: str
    created_date: datetime #= Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime #= Field(default_factory=datetime.utcnow)
    updated_user: str

class UserDevices(SQLModel,table=True):
    __tablename__ = "user_devices"
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    device_unique_id: str = Field(foreign_key="device.unique_id")
    created_date: datetime #= Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime #= Field(default_factory=datetime.utcnow)
    updated_user: str

class UserDeviceData(SQLModel,table=True):
    __tablename__ = "user_device_data"
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    device_unique_id: str = Field(foreign_key="device.unique_id")
    data: str #float
    data_type: int
    created_date: datetime # = Field(default_factory=datetime.utcnow)
    created_user: str
    updated_date: datetime #= Field(default_factory=datetime.utcnow)
    updated_user: str

