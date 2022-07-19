import uuid
from typing import Iterable, TypeVar, Sequence
from uuid import uuid4

from sqlalchemy import select, or_, and_, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.misc.models import (
    AdminModel,
    ParentModel,
    StudentModel,
    TeacherModel,
    GroupModel,
)
from app.services.database.models import (
    Administrator,
    Family,
    Group,
    Parent,
    Student,
    Teacher,
    Section,
    UnRegisteredUser,
    HomeTask,
    HomeWork,
)

T = TypeVar("T")


class SuperAdminRepo:
    def __init__(self, session: AsyncSession, telegram_id: int) -> None:
        self.session = session
        self.telegram_id = telegram_id

    async def get_id(self):
        stmt = select(Administrator.id).where(
            Administrator.telegram_id == self.telegram_id
        )

        return await self.session.scalar(stmt)

    async def get_registry(
        self, registry: T, offset: int, limit: int = 9
    ) -> Iterable[T]:
        result = await self.session.scalars(
            select(registry)
            .order_by(registry.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.all(), offset, limit

    def add_new_admin(self, form: AdminModel) -> Administrator:
        admin = Administrator(
            id=form.id,
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
            telegram_id=form.tg_id,
        )

        self.session.add(admin)
        return admin

    def add_new_teacher(self, form: TeacherModel) -> Teacher:
        teacher = Teacher(
            id=form.id,
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
            telegram_id=form.tg_id,
        )

        self.session.add(teacher)
        return teacher

    def add_new_student(self, form: StudentModel) -> Student:
        student = Student(
            id=form.id,
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
            telegram_id=form.tg_id,
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

    async def get_admins(self, offset: int, limit: int = 9) -> Iterable[Administrator]:
        result = await self.session.scalars(
            select(Administrator)
            .where(Administrator.telegram_id != self.telegram_id)
            .order_by(Administrator.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.all(), limit

    async def add_new_group(self, group: GroupModel) -> Group:
        admin_id = await self.get_id()
        group = Group(
            uuid=str(uuid4()),
            title=group.title,
            description=group.description,
            admin_id=admin_id,
            teacher_id=group.teacher_id,
        )

        self.session.add(group)

        return group

    async def get_teachers(self) -> Iterable[Teacher]:
        result = await self.session.scalars(select(Teacher))

        return result.all()

    async def get_students_in_group(
        self, group_uuid: str
    ) -> Iterable[tuple[int, str, str, str]]:
        result = await self.session.execute(
            select(
                Student.id, Student.last_name, Student.first_name, Student.patronymic
            )
            .join(Section)
            .where(Section.group_id == group_uuid)
            .order_by(Student.last_name)
        )

        return result.all()

    async def get_students_notin_group(
        self, group_uuid: str
    ) -> Iterable[tuple[int, str, str, str]]:
        subq = select(Student.id).join(Section).where(Section.group_id == group_uuid)
        result = await self.session.execute(
            select(
                Student.id, Student.last_name, Student.first_name, Student.patronymic
            )
            .join(Section, isouter=True)
            .where(
                and_(
                    or_(Section.group_id != group_uuid, Section.group_id.is_(None)),
                    Student.id.notin_(subq),
                )
            )
            .order_by(Student.last_name)
            .distinct()
        )

        return result.all()

    async def delete_students_from_group(self, group_uuid: str) -> None:
        await self.session.execute(
            delete(Section).where(Section.group_id == group_uuid)
        )

    def add_student_in_group(self, student_id: int, group_uuid: str) -> None:
        sec = Section(student_id=student_id, group_id=group_uuid)
        self.session.add(sec)

    async def delete_unreg_user(self, telegram_id: int) -> None:
        await self.session.execute(
            delete(UnRegisteredUser).where(UnRegisteredUser.telegram_id == telegram_id)
        )

    async def get_parents_by_id(self, student_id: int) -> Iterable[Parent]:
        result = await self.session.scalars(
            select(Parent).join(Family).where(Family.student_id == student_id)
        )

        return result.all()

    async def get_student_telegram_id(self, sid: int) -> int:
        return await self.session.scalar(
            select(Student.telegram_id).where(Student.id == sid).options(lazyload("*"))
        )

    async def delete_teacher(self, teacher: Teacher) -> None:
        await self.session.delete(teacher)

    async def delete_student(self, student: Student) -> None:
        await self.session.delete(student)

    async def delete_admin(self, admin: Administrator) -> None:
        await self.session.delete(admin)

    async def get_home_tasks(
        self, group_uuid: str, offset: int, limit: int = 5
    ) -> tuple[Iterable[HomeTask], int]:
        tasks = await self.session.scalars(
            select(HomeTask)
            .join(Group)
            .where(HomeTask.group_id == group_uuid)
            .order_by(HomeTask.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return tasks.all(), limit

    async def get_count_home_tasks(self, group_uuid: str) -> int:
        count = await self.session.scalar(
            select(func.count())
            .select_from(HomeTask)
            .join(Group)
            .where(HomeTask.group_id == group_uuid)
        )

        return count

    async def get_group(self, group_uuid: str) -> Group:
        stmt = select(Group).where(Group.uuid == group_uuid)

        return await self.session.scalar(stmt)

    async def get_student_home_works(
        self, student_id: int, task_uuid: str
    ) -> Iterable[HomeWork]:
        result = await self.session.scalars(
            select(HomeWork).where(
                and_(
                    HomeWork.home_task_id == task_uuid,
                    HomeWork.student_id == student_id,
                )
            )
        )

        return result.all()

    async def get_unreg_users(
        self, offset: int, limit: int = 9
    ) -> Iterable[UnRegisteredUser]:
        result = await self.session.scalars(
            select(UnRegisteredUser)
            .order_by(UnRegisteredUser.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.all(), limit

    async def get_count_unreg_users(self) -> int:
        return await self.session.scalar(
            select(func.count()).select_from(UnRegisteredUser)
        )

    def add_unreg_user(
        self, user: Teacher | Student | Administrator
    ) -> UnRegisteredUser:
        unreg_user = UnRegisteredUser(
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            email=user.email,
            user_name=user.user_name,
            tel=int(user.tel),
            timezone=user.timezone,
        )
        self.session.add(unreg_user)

        return unreg_user

    async def get_all_admins(self) -> Iterable[Administrator]:
        result = await self.session.scalars(
            select(Administrator)
            .where(Administrator.telegram_id != self.telegram_id)
            .options(lazyload("*"))
        )
        return result.all()

    async def get_all_teachers(self) -> Iterable[Teacher]:
        result = await self.session.scalars(select(Teacher).options(lazyload("*")))
        return result.all()

    async def get_all_students(self) -> list[tuple[Student, Sequence[Parent]]]:
        students = await self.session.scalars(select(Student).options(lazyload("*")))
        result = []
        for s in students:
            parents = await self.session.scalars(
                select(Parent).join(Family).where(Family.student_id == s.id)
            )
            result.append((s, parents.all()))

        return result

    async def get_all_groups(self) -> list[tuple[Group, Sequence[Student]]]:
        groups = await self.session.scalars(select(Group).options(lazyload("*")))
        result = []
        for g in groups:
            students = await self.session.scalars(
                select(Student.id).join(Section).where(Section.group_id == g.uuid)
            )
            result.append((g, students.all()))

        return result

    async def delete_group(self, group_uuid: str) -> None:
        await self.session.execute(delete(Group).where(Group.uuid == group_uuid))
