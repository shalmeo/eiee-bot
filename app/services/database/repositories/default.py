from typing import Any, TypeVar, Type

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.services.database.models import (
    Administrator,
    Student,
    Teacher,
    HomeTask,
    Group,
)

T = TypeVar("T")


class DefaultRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity: Type[T], ident: Any) -> T:
        return await self.session.get(entity, ident)

    async def user_is_admin(self, user_id: int) -> bool:
        return bool(await self.session.get(Administrator, user_id))

    async def get_student(self, user_id: int) -> Student:
        return await self.session.scalar(
            select(Student).where(Student.telegram_id == user_id)
        )

    async def get_teacher(self, user_id: int) -> Teacher:
        return await self.session.scalar(
            select(Teacher).where(Teacher.telegram_id == user_id)
        )

    async def get_admin(self, user_id: int) -> Administrator:
        return await self.session.scalar(
            select(Administrator).where(Administrator.telegram_id == user_id)
        )

    async def get_count(self, entity: Type[T], condition: Any = None) -> int:
        stmt = select(func.count()).select_from(entity)
        if not (condition is None):
            stmt = stmt.where(condition)

        return await self.session.scalar(stmt)

    async def get_home_task(self, task_uuid: str) -> HomeTask:
        return await self.session.scalar(
            select(HomeTask).where(HomeTask.uuid == task_uuid)
        )

    async def get_group(self, group_uuid: str) -> Group:
        return await self.session.scalar(select(Group).where(Group.uuid == group_uuid))

    async def get_student_by_tel(self, tel: str) -> Student:
        return await self.session.scalar(
            select(Student).where(Student.tel == tel).options(lazyload("*"))
        )

    async def get_teacher_by_tel(self, tel: str) -> Teacher:
        return await self.session.scalar(
            select(Teacher).where(Teacher.tel == tel).options(lazyload("*"))
        )

    async def get_admin_by_id(self, aid: int) -> Administrator:
        return await self.session.scalar(
            select(Administrator).where(Administrator.id == aid).options(lazyload("*"))
        )

    async def get_teacher_by_id(self, tid: int) -> Teacher:
        return await self.session.scalar(
            select(Teacher).where(Teacher.id == tid).options(lazyload("*"))
        )
