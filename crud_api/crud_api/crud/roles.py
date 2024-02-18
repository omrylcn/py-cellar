from datetime import datetime
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession
from crud_api.models import Roles
from crud_api.schemas import RolesCreate, RolesUpdate

class RolesCRUD():
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: RolesCreate) -> Roles:
        values = data.dict()
        values["created_date"] = datetime.utcnow()
        role = Roles(**values)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role
    
    async def get(self, id: int) -> Roles:
        
        statement = select(Roles).where(Roles.id == id)
        results = await self.session.execute(statement=statement)
        role = results.scalar_one_or_none()
        return role

    async def patch(self, id: int, data: RolesUpdate) -> Roles:
        role = await self.get(id=id)
        values = data.dict(exclude_unset=True)
        if role is None:
            return role
        values["updated_date"] = datetime.utcnow()
        for k, v in values.items():
            setattr(role, k, v)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role
    
    async def delete(self, id: int) -> bool:
        statement = delete(Roles).where(Roles.id == id)
        await self.session.execute(statement=statement)
        await self.session.commit()
        return True