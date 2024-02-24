from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import DeviceCRUD
from crud_api.schemas import DeviceCreate, DeviceUpdate
from crud_api.secure import get_current_user


users_router = APIRouter()

@users_router.post("/")
async def create_device(device: DeviceCreate, db: AsyncSession = Depends(db_session)):
    try:
        crud = DeviceCRUD(session=db)
        device = await crud.create(data=device)
        return JSONResponse(content={"message": "User created successfully!"},status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": f"Error! : {e}"},status_code=500) 

@users_router.get("/")
async def get_user(device_id: int, db: AsyncSession = Depends(db_session),current_username: str = Depends(get_current_user)):

    try:
        crud = DeviceCRUD(session=db)
        user = await crud.get(device_id=device_id)
        if user is None:
            return {"message": "No users found!"}
        else:
            return user
    except Exception as e:

        return {"message": f"Error! : {e}"} 

@users_router.patch("/")
async def update_user(device_id: int, device_update: DeviceUpdate, db: AsyncSession = Depends(db_session)):
    try:
        crud = DeviceCRUD(session=db)
        device = await crud.patch(user_id=device_id, data=device_update)

        if device is None:
            return {"message": "No users found!"}
        else:
            return device
     
    except Exception as e:
        return {"message": f"Error! : {e}"} 

@users_router.delete("/")
async def delete_user(device_id: int, db: AsyncSession = Depends(db_session)):
    try:
        crud = DeviceCRUD(session=db)
        success = await crud.delete(user_id=device_id)
        if success is False:
            return {"message": "No users found!"}
        else:
            return {"message": "User deleted successfully!"}
    except Exception as e:
        return {"message": f"Error! : {e}"}