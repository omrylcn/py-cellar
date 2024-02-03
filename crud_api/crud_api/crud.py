from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status as http_status
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession
from crud_api.schemas import UserCreate, UserUpdate
from crud_api.models import Users  # Update these imports according to your project structure



class UsersCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserCreate) -> Users:
        values = data.dict()
        values["created_date"] = datetime.utcnow()
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

        # if user is None:
        #     raise HTTPException(
        #         status_code=http_status.HTTP_404_NOT_FOUND,
        #         detail="The user hasn't been found!"
        #     )
        return user

    async def patch(self, user_id: int, data: UserUpdate) -> Users:
        user = await self.get(user_id=user_id)
        values = data.dict(exclude_unset=True)
        values["updated_date"] = datetime.utcnow()
        
        for k, v in values.items():
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