from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import UserRolesCRUD
from crud_api.schemas import UserRolesCreate, UserRolesUpdate
from crud_api.secure import get_current_user


user_roles_router = APIRouter()


@user_roles_router.post("/")
async def create_user_role(user: UserRolesCreate, db: AsyncSession = Depends(db_session)):
    try:
        crud = UserRolesCRUD(session=db)
        user = await crud.create(data=user)
        return JSONResponse(content={"message": "User Role created successfully!"},status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": f"Error! : {e}"},status_code=500)
    
@user_roles_router.get("/")
async def get_user_role(id: int, db: AsyncSession = Depends(db_session),current_username: str = Depends(get_current_user)):
    try:
        crud = UserRolesCRUD(session=db)
        user = await crud.get(id=id)
        if user is None:
            return {"message": "No user roles found!"}
        else:
            return user
    except Exception as e:
        return {"message": f"Error! : {e}"}
    
@user_roles_router.patch("/")
async def update_user_role(id: int, user_update: UserRolesUpdate, db: AsyncSession = Depends(db_session)):
    try:
        crud = UserRolesCRUD(session=db)
        user = await crud.patch(id=id, data=user_update)
        if user is None:
            return {"message": "No user roles found!"}
        else:
            return user
    except Exception as e:
        return {"message": f"Error! : {e}"}

@user_roles_router.delete("/")
async def delete_user_role(id: int, db: AsyncSession = Depends(db_session)):
    try:
        crud = UserRolesCRUD(session=db)
        success = await crud.delete(id=id)
        if success is False:
            return {"message": "No user roles found!"}
        else:
            return {"message": "User Role deleted successfully!"}
    except Exception as e:
        return {"message": f"Error! : {e}"}