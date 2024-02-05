from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from crud_api.db import db_session
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.schemas import UserDeviceDataCreate, UserDeviceDataUpdate
from crud_api.crud import UserDeviceDataCRUD


user_device_data_router = APIRouter()

@user_device_data_router.post("/")
async def get_user_device_data(user_device_data: UserDeviceDataCreate, db:AsyncSession = Depends(db_session)):
    try:
        crud = UserDeviceDataCRUD(session=db)
        user_device_data = await crud.create(data=user_device_data)
        
        return JSONResponse(content={'message':'User Device Data created successfully!'}, status_code=201)

    except Exception as e:
        print(e)
        return JSONResponse({"message": f"Error! : {e}"}, status_code=500)



@user_device_data_router.get("/{data_id}")
async def get_user_device_data(data_id: int, db: AsyncSession = Depends(db_session)):
    try:
        crud = UserDeviceDataCRUD(session=db)
        user_device_data = await crud.get(data_id=data_id)
        if user_device_data is None:
            return JSONResponse(content={"message": "No user device data found!"},status_code=500)
        else:
            return user_device_data
    except Exception as e:
        return JSONResponse(content={"message": f"Error! : {e}"}, status_code=500)