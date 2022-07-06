import datetime

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserMixin:
    id: int
    first_name: str
    last_name: str
    patronymic: str
    tel: int
    tg_id: int
    email: str
    user_name: str
    access_start: datetime.date
    access_end: datetime.date
    timezone: str


@dataclass
class EmployeeMixin:
    level: str
    description: str


@dataclass
class AdminModel(UserMixin, EmployeeMixin):
    msg_id: Optional[int] = None


@dataclass
class TeacherModel(UserMixin, EmployeeMixin):
    admin_id: int
    msg_id: Optional[int] = None


@dataclass
class ParentModel:
    first_name: str
    last_name: str
    patronymic: str
    tg_id: int
    tel: int


@dataclass
class StudentModel(UserMixin):
    admin_id: int
    parents: Optional[list[ParentModel]] = None
    msg_id: Optional[int] = None


@dataclass
class HomeTaskModel:
    group_uuid: str
    home_task_number: str
    lesson_date: datetime.date
    deadline: datetime.datetime
    description: str


@dataclass
class GroupModel:
    title: str
    description: str
    teacher_id: int


@dataclass
class SignUpModel:
    telegram_id: int
    user_name: str
    first_name: str
    last_name: str
    patronymic: str
    tel: int
    email: str
    timezone: str
