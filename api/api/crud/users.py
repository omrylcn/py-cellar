from typing import Optional
from datetime import datetime
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.schemas import UserCreate, UserUpdate
from api.models import Users
from api.secure import hash_password


class UsersCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserCreate) -> Users:
        values = data.model_dump()
        values["created_date"] = datetime.now(datetime.timezone.utc)
        values["password"] = hash_password(values["password"])
        user = Users(**values)
    
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get(self, user_id: int) -> Users:
        
        statement = select(Users).where(Users.id == user_id)
        results = await self.session.exec(statement=statement)
        user = results.scalar_one_or_none()  # type: Users | None
        return user

    async def update(self, user_id: int, data: UserUpdate) -> Optional[Users]:
        user = await self.get(user_id)
        if user is None:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            if key == "password":
                value = hash_password(value)
            setattr(user, key, value)
        user.updated_date = datetime.now(datetime.timezone.utc)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        statement = delete(Users).where(Users.id == user_id)
        await self.session.exec(statement=statement)
        await self.session.commit()
        return True
    
