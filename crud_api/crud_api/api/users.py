from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import UsersCRUD
from crud_api.schemas import UserCreate, UserUpdate
from crud_api.secure import get_current_user


users_router = APIRouter()

@users_router.post("/")
async def create_user(user: UserCreate, db: AsyncSession = Depends(db_session)):
    try:
        crud = UsersCRUD(session=db)
        user = await crud.create(data=user)
        return JSONResponse(content={"message": "User created successfully!"},status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": f"Error! : {e}"},status_code=500) 

@users_router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(db_session),current_username: str = Depends(get_current_user)):

    try:
        crud = UsersCRUD(session=db)
        user = await crud.get(user_id=user_id)
        if user is None:
            return {"message": "No users found!"}
        else:
            return user
    except Exception as e:

        return {"message": f"Error! : {e}"} 

@users_router.patch("/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(db_session)):
    try:
        crud = UsersCRUD(session=db)
        user = await crud.patch(user_id=user_id, data=user_update)

        if user is None:
            return {"message": "No users found!"}
        else:
            return user
     
    except Exception as e:
        return {"message": f"Error! : {e}"} 

@users_router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(db_session)):
    try:
        crud = UsersCRUD(session=db)
        user = await crud.delete(user_id=user_id)
        if user is None:
            return {"message": "No users found!"}
        else:
            return user
    except Exception as e:
        return {"message": f"Error! : {e}"}

# @users_router.patch("/{user_id}")
# async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(db_session)):
#     crud = UsersCRUD(session=db)
#     existing_user = await crud.get(user_id=user_id)
#     if not existing_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     updated_user = await crud.patch(user_id=user_id, data=user_update.dict(exclude_unset=True))
#     return updated_user
