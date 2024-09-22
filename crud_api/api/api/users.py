from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from api.db import db_session
from api.crud import UsersCRUD

from api.schemas import UserCreate, UserUpdate, UserResponse
from api.secure import get_current_user


users_router = APIRouter()

@users_router.post("/")
async def create_user(user: UserCreate, db: AsyncSession = Depends(db_session), current_user: str = Depends(get_current_user)):
    crud = UsersCRUD(session=db)
    try:
        user = await crud.create(data=user)
        return JSONResponse(content={f"message": "User created successfully! , user_id : {user.id}"},status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": f"Error! : {e}"},status_code=500) 


@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(db_session), current_user: str = Depends(get_current_user)):
    crud = UsersCRUD(session=db)
    user = await crud.get(user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found with id: {user_id}")
    return user

@users_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(db_session), current_user: str = Depends(get_current_user)):
    crud = UsersCRUD(session=db)
    try:
        updated_user = await crud.update(user_id=user_id, data=user_update)
        if updated_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found with id: {user_id}")
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(db_session), current_user: str = Depends(get_current_user)):
    crud = UsersCRUD(session=db)
    try:
        success = await crud.delete(user_id=user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
