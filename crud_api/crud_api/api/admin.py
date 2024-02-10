from fastapi import APIRouter, Depends,Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import LoginCRUD, PasswordResetCRUD
from crud_api.secure import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, REST_PASSWORD_TOKEN_EXPIRE_MINUTES,reset_access_token_expires
from crud_api.notify import send_reset_password_mail
from pydantic import BaseModel

class ForgotPassword(BaseModel):
    username: str
    email: str

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

@admin_router.post("/forgot-password")
async def forgot_password(request: Request ,fpr:ForgotPassword,db: AsyncSession = Depends(db_session)):
    #username = form_data.username
    #mail = form_data.email
    try:
        username = fpr.username
        mail = fpr.email
        url  = str(request.url).split("/forgot-password")[0]
        print(url)
        print(mail)
        #print(request.base_url)
        
        #return {"message": "forgot-password!"}
        print(f"username: {username}, mail: {mail}")
        crud = PasswordResetCRUD(db)
        user = await crud.get_user(username)
        

        if user is None:
            return JSONResponse(content={"message": "User not found!"}, status_code=404)
        
        token =  create_access_token(data={"sub": user.username},expires_delta=reset_access_token_expires)
        print(token)
        url = f"{url}/reset_password_template?access_token={token}"
        await send_reset_password_mail(mail, user, url, REST_PASSWORD_TOKEN_EXPIRE_MINUTES)
    
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

    return JSONResponse(content={"message": "Token sent to your email!"}, status_code=200)    
    


@admin_router.post("/reset-password")
async def reset_password():
    return {"message": "reset-password!"}
