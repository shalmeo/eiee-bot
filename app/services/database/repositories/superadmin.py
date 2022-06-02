from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.models import Administrator

class SuperAdminRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def get_registryof_admins(self, offset: int = None, limit: int = 9) -> Iterable[Administrator]:
        if offset is None:
            admins = await self.session.scalars(select(Administrator))
        else:
            admins = await self.session.scalars(
                select(Administrator)\
                    .order_by(Administrator.created_at.desc())\
                    .offset(offset)\
                    .limit(limit)
                )
        
        return admins.all(), offset, limit
    
    async def get_count_admins(self) -> int:
        return await self.session.scalar(select(func.count(Administrator.id)))

        