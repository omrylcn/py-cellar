from typing import List
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete
from crud_api.models import UserData  # Update import path as needed
from crud_api.schemas import UserDataCreate, UserDataUpdate  # Define these schemas based on your model

class UserDataCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserDataCreate) -> UserData:
        values = data.model_dump(exclude_unset=True)
        device_data = UserData(**values)
        self.session.add(device_data)
        await self.session.commit()
        await self.session.refresh(device_data)
        return device_data
    
    
    async def create_list(self, data: List[UserDataCreate]) -> bool:
        device_data_list = [
            UserData(**item.model_dump(exclude_unset=True), created_date=datetime.utcnow())
            for item in data
        ]
        self.session.add_all(device_data_list)
        await self.session.commit()
        return True
    

    async def get(self, data_id: int) -> UserData:
        statement = select(UserData).where(UserData.id == data_id)
        result = await self.session.exec(statement)
        return result.scalar_one_or_none()
    

    async def update(self, data_id: int, data: UserDataUpdate) -> UserData:
        device_data = await self.get(data_id=data_id)
        if not device_data:
            return None
        
        update_values = data.model_dump(exclude_unset=True)
        update_values["updated_date"] = datetime.now(datetime.timezone.utc)

        for key, value in update_values.items():
            setattr(device_data, key, value)

        self.session.add(device_data)
        await self.session.commit()
        await self.session.refresh(device_data)
        return device_data

    async def delete(self, data_id: int) -> bool:
        statement = delete(UserData).where(UserData.id == data_id)
        await self.session.exec(statement)
        await self.session.commit()
        return True
