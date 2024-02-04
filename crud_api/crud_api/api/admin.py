from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import LoginCRUD
from crud_api.secure import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

admin_router = APIRouter()


@admin_router.get("/")
async def get_admin():
    return {"message": "ping!"}


@admin_router.post("/token")
async def get_acces_token(db: AsyncSession = Depends(db_session), form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        crud = LoginCRUD(db)
        res = await crud.authenticate_user(form_data.username, form_data.password)
        if res[0] is None:
            return JSONResponse(content={"message": f"{res[1]}"}, status_code=500)

        user = res[0]
        access_token = create_access_token(data={"sub": user.username})

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

    return {
        "access_token": access_token,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES,
        "token_type": "Bearer",
        "userid": user.id,
        # "state": state,
        # "scope": "SCOPE"
    }
