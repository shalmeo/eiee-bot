import datetime
from typing import Sequence, Iterable
from uuid import uuid4

import sqlalchemy
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.models import (
    HomeWork,
    HomeWorkFile,
    Student,
    HomeTask,
    Group,
    Section,
    HomeTaskFile,
)


class StudentRepo:
    def __init__(self, session: AsyncSession, telegram_id: int) -> None:
        self.session = session
        self.telegram_id = telegram_id

    async def get_id(self):
        return await self.session.scalar(
            select(Student.id).where(Student.telegram_id == self.telegram_id)
        )

    async def add_home_work(self, home_task_id: str) -> HomeWork:
        student_id = await self.get_id()
        home_work = HomeWork(
            uuid=str(uuid4()),
            home_task_id=home_task_id,
            student_id=student_id,
            date=datetime.datetime.utcnow(),
        )
        self.session.add(home_work)
        return home_work

    def attach_file(self, fid: str, ftype: str, home_work_id: str) -> None:
        file = HomeWorkFile(id=fid, type=ftype, home_work_id=home_work_id)
        self.session.add(file)

    async def get_home_works(self, task_uuid: str) -> Sequence[HomeWork]:
        student_id = await self.get_id()
        home_works = await self.session.scalars(
            select(HomeWork).where(
                and_(
                    HomeWork.home_task_id == task_uuid,
                    HomeWork.student_id == student_id,
                )
            )
        )

        return home_works.all()

    async def get_groups(self) -> Iterable[tuple]:
        student_id = await self.get_id()
        sql = sqlalchemy.sql.text(
            """
            select uuid, title from groups
            join sections on groups.uuid = sections.group_id 
            where sections.student_id = :stu_id
            """
        )

        groups = await self.session.execute(sql, params={"stu_id": student_id})
        return groups.all()

    async def get_home_tasks(
        self, group_uuid: str, offset: int, limit: int = 5
    ) -> Iterable[HomeTask]:
        result = await self.session.scalars(
            select(HomeTask)
            .where(HomeTask.group_id == group_uuid)
            .order_by(HomeTask.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.all(), limit

    async def get_home_works_in_check(self) -> Iterable[HomeWork]:
        student_id = await self.get_id()
        home_works = await self.session.scalars(
            select(HomeWork)
            .where(
                and_(HomeWork.student_id == student_id, HomeWork.state == "in_check")
            )
            .order_by(HomeWork.created_at.desc())
        )
        return home_works.all()

    async def get_count_home_works(self, task_uuid: str) -> int:
        student_id = await self.get_id()
        count = await self.session.scalar(
            select(func.count())
            .select_from(HomeWork)
            .where(
                and_(
                    HomeWork.student_id == student_id,
                    HomeWork.home_task_id == task_uuid,
                )
            )
        )

        return count

    async def get_accepted_home_works(self) -> Iterable[HomeWork]:
        student_id = await self.get_id()
        home_works = await self.session.scalars(
            select(HomeWork)
            .where(
                and_(HomeWork.student_id == student_id, HomeWork.state == "accepted")
            )
            .order_by(HomeWork.created_at.desc())
            .limit(5)
        )
        return home_works.all()

    async def get_count_home_tasks(self, group_uuid: str) -> int:
        return await self.session.scalar(
            select(func.count())
            .select_from(HomeTask)
            .where(HomeTask.group_id == group_uuid)
        )

    async def get_home_task_files(self, task_uuid: str) -> Iterable[HomeTaskFile]:
        files = await self.session.scalars(
            select(HomeTaskFile).where(HomeTaskFile.home_task_id == task_uuid)
        )

        return files.all()
