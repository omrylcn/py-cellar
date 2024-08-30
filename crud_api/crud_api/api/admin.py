from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import LoginCRUD
from crud_api.secure import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

admin_router = APIRouter()

@admin_router.post("/token", response_model=dict)
async def get_access_token(
    db: AsyncSession = Depends(db_session), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    crud = LoginCRUD(db)
    user, error_message = await crud.authenticate_user(form_data.username, form_data.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES,
        "token_type": "Bearer",
        "userid": user.id,
    }
