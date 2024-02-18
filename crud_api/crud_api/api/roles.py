from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import RolesCRUD
from crud_api.schemas import RolesCreate, RolesUpdate
from crud_api.secure import get_current_user


roles_router = APIRouter()

@roles_router.post("/")
async def create_role(user: RolesCreate, db: AsyncSession = Depends(db_session)):
    try:
        crud = RolesCRUD(session=db)
        user = await crud.create(data=user)
        return JSONResponse(content={"message": "Role created successfully!"},status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": f"Error! : {e}"},status_code=500) 


@roles_router.get("/")
async def get_role(id: int, db: AsyncSession = Depends(db_session),current_username: str = Depends(get_current_user)):

    try:
        crud = RolesCRUD(session=db)
        role = await crud.get(id=id)
        if role is None:
            return {"message": "No roles found!"}
        else:
            return role
    except Exception as e:

        return {"message": f"Error! : {e}"}
    
@roles_router.patch("/")
async def update_role(id: int, role_update: RolesUpdate, db: AsyncSession = Depends(db_session)):
    try:
        crud = RolesCRUD(session=db)
        role = await crud.patch(id=id, data=role_update)

        if role is None:
            return {"message": "No roles found!"}
        else:
            return role
     
    except Exception as e:
        return {"message": f"Error! : {e}"}
    
@roles_router.delete("/")
async def delete_role(id: int, db: AsyncSession = Depends(db_session)):
    try:
        crud = RolesCRUD(session=db)
        success = await crud.delete(id=id)
        if success is False:
            return {"message": "No roles found!"}
        else:
            return {"message": "Role deleted successfully!"}
    except Exception as e:
        return {"message": f"Error! : {e}"}

