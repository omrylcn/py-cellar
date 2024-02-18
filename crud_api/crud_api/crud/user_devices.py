from typing import Optional,Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from datetime import datetime
from crud_api.models import UserDevices 
from crud_api.schemas import UserDevicesCreate,UserDevicesUpdate # Make sure to import your UserDevices model

class UserDevicesCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data:UserDevicesCreate) -> UserDevices:
        values = data.dict()
        values["created_date"] = datetime.utcnow()
        new_user_device = UserDevices(**values)
        self.session.add(new_user_device)
        await self.session.commit()
        await self.session.refresh(new_user_device)
        return new_user_device

    async def get(self, user_id:int,device_unique_id:str) -> Optional[UserDevices]:
        query = select(UserDevices).where(UserDevices.user_id == user_id, UserDevices.device_unique_id == device_unique_id)
        result = await self.session.execute(query)
        user_device = result.scalar_one_or_none()
        return user_device

    async def patch(self,user_id:int,device_unique_id, data:UserDevicesUpdate) -> Optional[UserDevices]:
    
        user_device = await self.get(user_id=user_id,device_unique_id=device_unique_id)
        values = data.dict(exclude_unset=True)
        if user_device is None:
            return user_device
        
        values["updated_date"] = datetime.utcnow()
        for k, v in values.items():
            setattr(user_device, k, v)

        self.session.add(user_device)
        await self.session.commit()
        await self.session.refresh(user_device)
        return user_device


    async def delete(self, user_id: int) -> bool:
        query = delete(UserDevices).where(UserDevices.user_id == user_id)
        await self.session.execute(query)
        await self.session.commit()
        return True