from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import UserDevicesCRUD  # Ensure you have this CRUD class
from crud_api.schemas import UserDevicesCreate, UserDevicesUpdate  # Update imports as necessary
from crud_api.secure import get_current_user

from pydantic import BaseModel, Field
from typing import Any

# class UserDeviceGet(BaseModel):
#     column_name: str = Field(..., description="The name of the column to search for", example="user_id")
#     column_value: Any = Field(..., description="The value of the column to search for", example=1)

#     class Config:
#         schema_extra = {
#             "example": {
#                 "column_name": "user_id",
#                 "column_value": 1  # Example can be of any type, here an integer is used
#             }
#         }


user_devices_router = APIRouter()

@user_devices_router.post("/")
async def create_user_device(user_device: UserDevicesCreate, db: AsyncSession = Depends(db_session)):
    try:
        crud = UserDevicesCRUD(session=db)
        new_user_device = await crud.create(user_device)
        return JSONResponse(content={"message": "User device created successfully!"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": f"Error! : {e}"}, status_code=500)

@user_devices_router.get("/")
async def get_user_device( user_id: int,device_unique_id:str, db: AsyncSession = Depends(db_session)):
    try:
        crud = UserDevicesCRUD(session=db)
        user_device = await crud.get(user_id=user_id,device_unique_id=device_unique_id)
        if user_device is None:
            return {"message": "No user device found!"}
        else:
            return user_device
    except Exception as e:
        return {"message": f"Error! : {e}"}

@user_devices_router.patch("/{user_id}")
async def update_user_device(user_id: int, user_device_update: UserDevicesUpdate, db: AsyncSession = Depends(db_session)):
    try:
        crud = UserDevicesCRUD(session=db)
        updated_user_device = await crud.patch(user_id=user_device_update.user_id, device_id=user_device_update.device_id)
        if updated_user_device is None:
            return {"message": "No user device found!"}
        else:
            return updated_user_device
    except Exception as e:
        return {"message": f"Error! : {e}"}

@user_devices_router.delete("")
async def delete_user_device(user_id: int, db: AsyncSession = Depends(db_session)):
    try:
        crud = UserDevicesCRUD(session=db)
        success = await crud.delete(id=user_id)
        if success is False:
            return {"message": "No user_device found!"}
        else:
            return {"message": "User-device deleted successfully!"}
    except Exception as e:
        return {"message": f"Error! : {e}"}

#             return {"message": "User device deleted successfully!"}
#         else:
#             return {"message": "User device not found!"}
#     except Exception as e:
#         return {"message": f"Error! : {e}"}
