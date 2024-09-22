from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from api.db import db_session
from api.schemas import UserDataCreate,UserDataResponse
from api.crud import UserDataCRUD
from api.secure import get_current_user

user_data_router = APIRouter()

@user_data_router.post("/", response_model=dict)
async def create_user_data(
    user_device_data: List[UserDataCreate], 
    db: AsyncSession = Depends(db_session),
    current_username: str = Depends(get_current_user)
):
    crud = UserDataCRUD(session=db)
    try:
        await crud.create_list(data=user_device_data)
        return {"message": "User Device Data created successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

@user_data_router.get("/{data_id}", response_model=UserDataResponse)
async def get_user_data(
    data_id: int, 
    db: AsyncSession = Depends(db_session),
    current_username: str = Depends(get_current_user)
):
    crud = UserDataCRUD(session=db)
    try:
        user_device_data = await crud.get(data_id=data_id)
        if not user_device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user device data found!"
            )
        return user_device_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
