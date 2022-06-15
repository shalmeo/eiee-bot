from typing import Any, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.models import Administrator, Student, Teacher

T = TypeVar("T")


class DefaultRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity: T, ident: int) -> T:
        return await self.session.get(entity, ident)

    async def user_is_admin(self, user_id: int) -> bool:
        return bool(await self.session.get(Administrator, user_id))

    async def user_is_student(self, user_id: int) -> bool:
        return bool(await self.session.get(Student, user_id))

    async def user_is_teacher(self, user_id: int) -> bool:
        return bool(await self.session.get(Teacher, user_id))

    async def get_count(self, entity: T, condition: Any = None) -> int:
        stmt = select(func.count()).select_from(entity)
        if not condition is None:
            stmt = stmt.where(condition)

        return await self.session.scalar(stmt)
