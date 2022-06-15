from typing import Iterable, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class AdminRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_registry(
        self, registry: T, admin_id: int, offset, limit: int = 9
    ) -> Iterable[T]:
        result = await self.session.scalars(
            select(registry)
            .where(registry.admin_id == admin_id)
            .order_by(registry.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.all(), offset, limit

    async def get_count(self, registry: T, admin_id: int) -> int:
        return await self.session.scalar(
            select(func.count())
            .select_from(registry)
            .where(registry.admin_id == admin_id)
        )

    async def get(self, registry: T, id: int) -> T:
        return await self.session.get(registry, id)
