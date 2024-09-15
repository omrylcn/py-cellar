from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status as http_status
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession
from api.models import Users  # Update these imports according to your project structure
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password for storing.
    """
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


class LoginCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, username: str) -> Users:
        statement = select(Users).where(Users.username == username)
        results = await self.session.execute(statement=statement)
        user = results.scalar_one_or_none()

        return user

    async def authenticate_user(self, username: str, password: str) -> Users:
        user = await self.get_user(username)

        hashed_password = hash_password(password)
        # print(hashed_password)
        # print(user.password)
        if user is None:
            return user, "User not found"
        if not await verify_password(hashed_password, user.password):
            return user, "Incorrect password"
        return user, "User authenticated"


class PasswordResetCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, username: str) -> Users:
        statement = select(Users).where(Users.username == username)
        results = await self.session.execute(statement=statement)
        user = results.scalar_one_or_none()

        return user

    async def get_password_reset(self, token: UUID) -> Optional[Users]:
        statement = select(Users).where(Users.reset_token == token)
        results = await self.session.execute(statement=statement)
        user = results.scalar_one_or_none()

        return user

    async def reset_password(self, token: UUID, new_password: str) -> Users:
        user = await self.get_password_reset(token)
        if user is None:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Token not found")
        user.password = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiration = None
        user.updated_at = datetime.now()
        await self.session.commit()
        return user