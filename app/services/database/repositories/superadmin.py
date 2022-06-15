from typing import Iterable, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.misc.models import AdminModel, ParentModel, StudentModel, TeacherModel
from app.services.database.models import (
    Administrator,
    Family,
    Group,
    Parent,
    Student,
    Teacher,
)

T = TypeVar("T")


class SuperAdminRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, registry: T, id: int) -> T:
        return await self.session.get(registry, id)

    async def get_count(self, registry: T) -> int:
        return await self.session.scalar(select(func.count()).select_from(registry))

    async def get_registry(
        self, registry: T, offset: int = None, limit: int = 9
    ) -> Iterable[T]:
        if offset is None:
            result = await self.session.scalars(
                select(registry).order_by(registry.created_at.desc())
            )
        else:
            result = await self.session.scalars(
                select(registry)
                .order_by(registry.created_at.desc())
                .offset(offset)
                .limit(limit)
            )

        return result.all(), offset, limit

    def add_new_admin(self, form: AdminModel) -> Administrator:
        admin = Administrator(
            id=form.tg_id,
            first_name=form.first_name,
            last_name=form.last_name,
            patronymic=form.patronymic,
            email=form.email,
            user_name=form.user_name,
            tel=form.tel,
            level=form.level,
            description=form.description,
            timezone=form.timezone,
            access_start=form.access_start,
            access_end=form.access_end,
        )

        self.session.add(admin)
        return admin

    def add_new_teacher(self, form: TeacherModel) -> Teacher:
        teacher = Teacher(
            id=form.tg_id,
            first_name=form.first_name,
            last_name=form.last_name,
            patronymic=form.patronymic,
            email=form.email,
            user_name=form.user_name,
            tel=form.tel,
            level=form.level,
            description=form.description,
            timezone=form.timezone,
            access_start=form.access_start,
            access_end=form.access_end,
            admin_id=form.admin_id,
        )

        self.session.add(teacher)
        return teacher

    def add_new_student(self, form: StudentModel) -> Student:
        student = Student(
            id=form.tg_id,
            first_name=form.first_name,
            last_name=form.last_name,
            patronymic=form.patronymic,
            email=form.email,
            user_name=form.user_name,
            tel=form.tel,
            timezone=form.timezone,
            access_start=form.access_start,
            access_end=form.access_end,
            admin_id=form.admin_id,
        )

        self.session.add(student)
        return student

    def add_new_parent(self, form: ParentModel) -> Parent:
        parent = Parent(
            id=form.tg_id,
            first_name=form.first_name,
            last_name=form.last_name,
            patronymic=form.patronymic,
            tel=form.tel,
        )

        self.session.add(parent)
        return parent

    def add_new_family(self, student_id: int, parent_id: int) -> None:
        family = Family(student_id=student_id, parent_id=parent_id)

        self.session.add(family)

    async def get_groups(self, offset: int, limit: int = 9) -> Iterable[Group]:
        result = await self.session.scalars(
            select(Group)
            .order_by(Group.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(lazyload(Group.students))
        )

        return result.all(), offset, limit

    async def get_students(self, offset: int, limit: int = 9) -> Iterable[Student]:
        result = await self.session.scalars(
            select(Student)
            .order_by(Student.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(lazyload(Student.groups))
        )

        return result.all(), offset, limit
