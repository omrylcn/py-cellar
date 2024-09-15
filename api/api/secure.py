from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import ACCESS_TOKEN_EXPIRE_MINUTES,SECRET_KEY,ALGORITHM
from api.db import db_session
from api.crud.admin import LoginCRUD

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = access_token_expires):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password: str) -> str:
    """
    Hash a password for storing.
    """
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(token: str = Depends(oauth2_scheme), sess: AsyncSession = Depends(db_session)):
   
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    crud = LoginCRUD(sess)
    user = await crud.get_user(username)
    
    if user is None:
         raise credentials_exception
    
    return user.username # user
