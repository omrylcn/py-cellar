from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status as http_status
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession
from crud_api.schemas import UserCreate, UserUpdate
from crud_api.models import Users  # Update these imports according to your project structure
from crud_api.secure import  hash_password


class UsersCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserCreate) -> Users:
        values = data.model_dump()
        values["created_date"] = datetime.now()
        values["password"] = hash_password(values["password"])
        user = Users(**values)
        # print("new user :",user)
        # print(type(user))
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get(self, user_id: int) -> Users:
        
        statement = select(Users).where(Users.id == user_id)
        results = await self.session.execute(statement=statement)
        user = results.scalar_one_or_none()  # type: Users | None
        return user

    async def patch(self, user_id: int, data: UserUpdate) -> Users:
        user = await self.get(user_id=user_id)
        values = data.dict(exclude_unset=True)
        
        if user is None:
            return user
            
        values["updated_date"] = datetime.utcnow()
        
        for k, v in values.items():
            if k == "password":
                v = hash_password(v)
            setattr(user, k, v)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        statement = delete(Users).where(Users.id == user_id)
        await self.session.execute(statement=statement)
        await self.session.commit()
        return True
    
