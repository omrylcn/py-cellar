from typing import List
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete
from crud_api.models import UserDeviceData  # Update import path as needed
from crud_api.schemas import UserDeviceDataCreate, UserDeviceDataUpdate  # Define these schemas based on your model

class UserDeviceDataCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserDeviceDataCreate) -> UserDeviceData:
        values = data.model_dump(exclude_unset=True)
    
        
        values["created_date"] = datetime.now()
        # values["updated_date"] = values["created_date"]
        # values["updated_user"] = values["created_user"]
        device_data = UserDeviceData(**values)
        #print("new device data :",device_data)        
        self.session.add(device_data)
        await self.session.commit()
        await self.session.refresh(device_data)
        
        return device_data
    
    async def create_list(self, data: List[UserDeviceDataCreate]) -> bool:
        device_data_list = []
        for device_data in data:
            values = device_data.dict()#model_dump(exclude_unset=True)
            #values["created_date"] = datetime.now()
            device_data = UserDeviceData(**values)
            self.session.add(device_data)
            device_data_list.append(device_data)
        await self.session.commit()
        return True

    async def get(self, data_id: int) -> UserDeviceData:
        statement = select(UserDeviceData).where(UserDeviceData.id == data_id)
        results = await self.session.execute(statement)
        device_data = results.scalar_one_or_none()
        return device_data

    async def pathc(self, data_id: int, data: UserDeviceDataUpdate) -> UserDeviceData:
        device_data = await self.get(data_id=data_id)
        if device_data is None:
            return device_data
        
        update_values = data.dict(exclude_unset=True)
        update_values["updated_date"] = datetime.utcnow()
        
        for k, v in update_values.items():
            setattr(device_data, k, v)

        self.session.add(device_data)
        await self.session.commit()
        await self.session.refresh(device_data)
        return device_data

    async def delete(self, data_id: int) -> bool:
        statement = delete(UserDeviceData).where(UserDeviceData.id == data_id)
        await self.session.exec(statement)
        await self.session.commit()
        return True
