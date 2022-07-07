from typing import Iterable, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.services.database.models import Administrator, Parent, Family

T = TypeVar("T")


class AdminRepo:
    def __init__(self, session: AsyncSession, telegram_id: int) -> None:
        self.session = session
        self.telegram_id = telegram_id

    async def get_id(self):
        return await self.session.scalar(
            select(Administrator.id).where(
                Administrator.telegram_id == self.telegram_id
            )
        )

    async def get_registry(self, registry: T, offset, limit: int = 9) -> Iterable[T]:
        aid = await self.get_id()
        result = await self.session.scalars(
            select(registry)
            .where(registry.admin_id == aid)
            .order_by(registry.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(lazyload("*"))
        )

        return result.all(), offset, limit

    async def get_parents_by_id(self, student_id: int) -> Iterable[Parent]:
        result = await self.session.scalars(
            select(Parent).join(Family).where(Family.student_id == student_id)
        )

        return result.all()
