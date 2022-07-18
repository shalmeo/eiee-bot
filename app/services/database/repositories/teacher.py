import uuid
from typing import Iterable
from uuid import uuid4

from sqlalchemy import select, and_, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.misc.date_utils import local_to_utc
from app.misc.models import HomeTaskModel
from app.services.database.models import (
    Group,
    HomeTask,
    HomeTaskFile,
    Student,
    Teacher,
    HomeWork,
    HomeWorkFile,
    RejectedFile,
)


class TeacherRepo:
    def __init__(self, session: AsyncSession, teacher_id: int = 0) -> None:
        self.session = session
        self.telegram_id = teacher_id

    async def get_id(self):
        teacher_id = await self.session.scalar(
            select(Teacher.id).where(Teacher.telegram_id == self.telegram_id)
        )

        return teacher_id

    async def get_students_group(self, group_uuid: str) -> Iterable[Student]:
        group: Group = await self.session.get(Group, group_uuid)
        return group.students

    def add_new_home_task(self, data: HomeTaskModel, timezone: str) -> HomeTask:
        home_task = HomeTask(
            uuid=str(uuid4()),
            group_id=data.group_uuid,
            number=data.home_task_number,
            lesson_date=data.lesson_date,
            deadline=local_to_utc(data.deadline, timezone),
            description=data.description,
        )

        self.session.add(home_task)

        return home_task

    def attach_file(self, home_task_id: str, file_id: str, file_type: str) -> None:
        file = HomeTaskFile(home_task_id=home_task_id, id=file_id, type=file_type)
        self.session.add(file)

    async def get_home_tasks(
        self, group_uuid: str, offset: int, limit: int = 5
    ) -> tuple[Iterable[HomeTask], int]:
        teacher_id = await self.get_id()
        tasks = await self.session.scalars(
            select(HomeTask)
            .join(Group)
            .where(
                and_(HomeTask.group_id == group_uuid, Group.teacher_id == teacher_id)
            )
            .order_by(HomeTask.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return tasks.all(), limit

    async def get_in_check_home_works(self, home_task_id: str) -> Iterable[HomeWork]:
        home_works = await self.session.scalars(
            select(HomeWork)
            .join(Student)
            .where(
                and_(
                    HomeWork.home_task_id == home_task_id, HomeWork.state == "in_check"
                )
            )
            .order_by(Student.last_name)
        )

        return home_works.all()

    async def get_home_work_files(self, home_work_id: str) -> Iterable[HomeWorkFile]:
        files = await self.session.scalars(
            select(HomeWorkFile).where(HomeWorkFile.home_work_id == home_work_id)
        )

        return files.all()

    async def accept_home_work(self, home_work_id: str) -> None:
        stmt = (
            update(HomeWork)
            .where(HomeWork.uuid == home_work_id)
            .values(state="accepted")
        )
        await self.session.execute(stmt)

    async def reject_home_work(self, home_work_id: str) -> None:
        stmt = (
            update(HomeWork)
            .where(HomeWork.uuid == home_work_id)
            .values(state="rejected")
        )
        await self.session.execute(stmt)

    async def get_home_work(self, home_work_id: str) -> HomeWork:
        stmt = select(HomeWork).where(HomeWork.uuid == home_work_id)

        return await self.session.scalar(stmt)

    async def get_completed_home_works(self, task_id: str) -> Iterable[HomeWork]:
        stmt = (
            select(HomeWork)
            .join(Student)
            .where(
                and_(
                    HomeWork.home_task_id == task_id,
                    HomeWork.state == "accepted",
                )
            )
            .order_by(Student.last_name)
        )

        return (await self.session.scalars(stmt)).all()

    async def get_count_home_tasks(self, group_uuid: str) -> int:
        teacher_id = await self.get_id()
        count = await self.session.scalar(
            select(func.count())
            .select_from(HomeTask)
            .join(Group)
            .where(
                and_(HomeTask.group_id == group_uuid, Group.teacher_id == teacher_id)
            )
        )

        return count

    def add_reject_file(
        self, work_uuid: uuid.UUID, file_id: str, file_type: str
    ) -> None:
        file = RejectedFile(id=file_id, work_uuid=work_uuid, type=file_type)
        self.session.add(file)
