from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status as http_status
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession
from crud_api.schemas import DeviceCreate, DeviceUpdate
from crud_api.models import Device  # Update these imports according to your project structure
from crud_api.secure import  hash_password


class DeviceCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: DeviceCreate) -> Device:
        values = data.model_dump()
        values["created_date"] = datetime.now()
        device = Device(**values)
        # print("new device :",device)
        # print(type(device))
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def get(self, device_id: int) -> Device:
        
        statement = select(Device).where(Device.id == device_id)
        results = await self.session.exec(statement=statement)
        device = results.scalar_one_or_none()  # type: Device | None
        return device

    async def patch(self, device_id: int, data: DeviceUpdate) -> Device:
        device = await self.get(device_id=device_id)
        values = data.model_dump(exclude_unset=True)
        
        if device is None:
            return device
            
        values["updated_date"] = datetime.utcnow()
        
        for k, v in values.items():
            if k == "password":
                v = hash_password(v)
            setattr(device, k, v)

        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def delete(self, device_id: int) -> bool:
        statement = delete(Device).where(Device.id == device_id)
        await self.session.exec(statement=statement)
        await self.session.commit()
        return True