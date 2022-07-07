from typing import Iterable

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from app.services.database.base import AccessMixin, Base, TimeStampMixin


class Administrator(Base, TimeStampMixin, AccessMixin):
    __tablename__ = "administrators"

    id = Column(BigInteger, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    email = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    tel = Column(BigInteger, unique=True)
    telegram_id = Column(BigInteger, unique=True)
    level = Column(String)
    description = Column(String)
    timezone = Column(String)

    teachers: Iterable["Teacher"] = relationship(
        "Teacher", lazy="selectin", uselist=True, back_populates="admin"
    )
    students: Iterable["Student"] = relationship(
        "Student", lazy="selectin", uselist=True, back_populates="admin"
    )
    groups: Iterable["Group"] = relationship(
        "Group", lazy="selectin", uselist=True, back_populates="admin"
    )


class Teacher(Base, TimeStampMixin, AccessMixin):
    __tablename__ = "teachers"

    id = Column(BigInteger, primary_key=True)
    admin_id = Column(
        BigInteger, ForeignKey("administrators.id", ondelete="SET DEFAULT"), default=0
    )
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    email = Column(String, nullable=False)
    user_name = Column(String)
    tel = Column(BigInteger, unique=True)
    telegram_id = Column(BigInteger, unique=True)
    level = Column(String)
    description = Column(String)
    timezone = Column(String)

    admin: "Administrator" = relationship(
        "Administrator", lazy="selectin", uselist=False, back_populates="teachers"
    )
    groups: Iterable["Group"] = relationship(
        "Group", lazy="selectin", uselist=True, back_populates="teacher"
    )


class Student(Base, TimeStampMixin, AccessMixin):
    __tablename__ = "students"

    id = Column(BigInteger, primary_key=True)
    admin_id = Column(
        BigInteger, ForeignKey("administrators.id", ondelete="SET DEFAULT"), default=0
    )
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    email = Column(String, nullable=False)
    user_name = Column(String)
    tel = Column(BigInteger, unique=True)
    telegram_id = Column(BigInteger, unique=True)
    timezone = Column(String)

    admin: "Administrator" = relationship(
        "Administrator", lazy="selectin", uselist=False, back_populates="students"
    )
    relatives: Iterable["Family"] = relationship(
        "Family", lazy="selectin", uselist=True, back_populates="student"
    )
    groups: Iterable["Group"] = relationship(
        "Group", lazy="joined", uselist=True, secondary="sections", viewonly=True
    )
    home_works: Iterable["Section"] = relationship(
        "HomeWork", lazy="selectin", uselist=True, back_populates="student"
    )


class Parent(Base, TimeStampMixin):
    __tablename__ = "parents"

    id = Column(BigInteger, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    tel = Column(BigInteger, unique=True)

    childrens: Iterable["Family"] = relationship(
        "Family", lazy="selectin", uselist=True, back_populates="parent"
    )


class Family(Base, TimeStampMixin):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(
        BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    parent_id = Column(
        BigInteger, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False
    )

    student = relationship(
        "Student", lazy="selectin", uselist=False, back_populates="relatives"
    )
    parent = relationship(
        "Parent", lazy="selectin", uselist=False, back_populates="childrens"
    )


class Group(Base, TimeStampMixin):
    __tablename__ = "groups"

    uuid = Column(UUID, primary_key=True)
    admin_id = Column(
        BigInteger,
        ForeignKey("administrators.id", ondelete="SET DEFAULT"),
        default=0,
    )
    teacher_id = Column(
        BigInteger, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String)
    description = Column(String)

    admin: "Administrator" = relationship(
        "Administrator", lazy="selectin", uselist=False, back_populates="groups"
    )
    teacher: "Teacher" = relationship(
        "Teacher", lazy="selectin", uselist=False, back_populates="groups"
    )
    students: Iterable["Student"] = relationship(
        "Student",
        lazy="joined",
        uselist=True,
        secondary="sections",
        viewonly=True,
        order_by="Student.last_name",
    )
    home_tasks: Iterable["HomeTask"] = relationship(
        "HomeTask", lazy="selectin", uselist=True, back_populates="group"
    )


class Section(Base, TimeStampMixin):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(UUID, ForeignKey("groups.uuid", ondelete="CASCADE"))
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"))

    group: "Group" = relationship("Group", lazy="joined", uselist=False, viewonly=True)
    student: "Student" = relationship(
        "Student", lazy="joined", uselist=False, viewonly=True
    )


class HomeTask(Base, TimeStampMixin):
    __tablename__ = "home_tasks"

    uuid = Column(UUID, primary_key=True)
    group_id = Column(UUID, ForeignKey("groups.uuid", ondelete="CASCADE"))
    number = Column(String, nullable=False)
    lesson_title = Column(String)
    lesson_date = Column(Date)
    deadline = Column(DateTime)
    description = Column(String)

    group: "Group" = relationship(
        "Group", lazy="selectin", uselist=False, back_populates="home_tasks"
    )
    home_works: Iterable["HomeWork"] = relationship(
        "HomeWork", lazy="selectin", uselist=True, back_populates="home_task"
    )
    home_task_files: Iterable["HomeTaskFile"] = relationship(
        "HomeTaskFile", lazy="selectin", uselist=True, back_populates="home_task"
    )


class HomeWork(Base, TimeStampMixin):
    __tablename__ = "home_works"

    uuid = Column(UUID, primary_key=True)
    home_task_id = Column(UUID, ForeignKey("home_tasks.uuid", ondelete="CASCADE"))
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"))
    date = Column(DateTime)
    state = Column(String, default="in_check")  # accepted, in_check, rejected

    home_task: "HomeTask" = relationship(
        "HomeTask", lazy="selectin", uselist=False, back_populates="home_works"
    )
    student: "Student" = relationship(
        "Student", lazy="selectin", uselist=False, back_populates="home_works"
    )
    home_work_files: Iterable["HomeWorkFile"] = relationship(
        "HomeWorkFile", lazy="selectin", uselist=True, back_populates="home_work"
    )


class HomeTaskFile(Base, TimeStampMixin):
    __tablename__ = "home_task_files"

    id = Column(String, primary_key=True)
    home_task_id = Column(UUID, ForeignKey("home_tasks.uuid", ondelete="CASCADE"))
    type = Column(String)

    home_task: "HomeTask" = relationship(
        "HomeTask", lazy="selectin", uselist=False, back_populates="home_task_files"
    )


class HomeWorkFile(Base, TimeStampMixin):
    __tablename__ = "home_work_files"

    id = Column(String, primary_key=True)
    home_work_id = Column(UUID, ForeignKey("home_works.uuid", ondelete="CASCADE"))
    type = Column(String)

    home_work: "HomeWork" = relationship(
        "HomeWork", lazy="selectin", uselist=False, back_populates="home_work_files"
    )


class UnRegisteredUser(Base, TimeStampMixin):
    __tablename__ = "unregistered_users"

    telegram_id = Column(BigInteger, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    email = Column(String, nullable=False)
    user_name = Column(String)
    tel = Column(BigInteger, unique=True)
    timezone = Column(String)
    role = Column(String, nullable=False)
