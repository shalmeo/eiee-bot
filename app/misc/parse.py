import datetime

from aiogram.utils.web_app import WebAppUser
from multidict import MultiDictProxy

from app.misc.exceptions import RegisterFormValidateError
from app.misc.models import (
    AdminModel,
    HomeTaskModel,
    ParentModel,
    StudentModel,
    TeacherModel,
    GroupModel,
    SignUpModel,
)
from app.services.database import UnRegisteredUser


def parse_admin_register_data(data: MultiDictProxy) -> AdminModel:
    last_name, first_name, patronymic = _parse_full_name(data)

    access_start = datetime.date(*map(int, data.get("access_start").split("-")))
    access_end = datetime.date(*map(int, data.get("access_end").split("-")))
    if access_start > access_end:
        raise RegisterFormValidateError()

    tel = data.get("tel")
    if len(tel) != 10 or not tel.isdigit():
        raise RegisterFormValidateError()
    else:
        tel = int(tel)

    admin_id = int(data.get("id"))
    email: str = data.get("email", "").strip()
    tg_id: int = int(data.get("tgId"))
    user_name: str = data.get("userName", "").strip()
    level: str = data.get("level", "").strip()
    description: str = data.get("description", "").strip()
    timezone: str = data.get("timezone", "").strip()
    msg_id = int(data.get("msgId"))

    return AdminModel(
        id=admin_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        tel=tel,
        email=email,
        tg_id=tg_id,
        user_name=user_name,
        level=level,
        description=description,
        access_start=access_start,
        access_end=access_end,
        timezone=timezone,
        msg_id=msg_id,
    )


def parse_teacher_register_data(data: MultiDictProxy) -> TeacherModel:
    last_name, first_name, patronymic = _parse_full_name(data)

    access_start = datetime.date(*map(int, data.get("access_start").split("-")))
    access_end = datetime.date(*map(int, data.get("access_end").split("-")))
    if access_start > access_end:
        raise RegisterFormValidateError()

    tel = data.get("tel")
    if len(tel) != 10 or not tel.isdigit():
        raise RegisterFormValidateError()
    else:
        tel = int(tel)

    teacher_id = int(data.get("id"))
    email: str = data.get("email", "").strip()
    tg_id: int = int(data.get("tgId"))
    user_name: str = data.get("userName", "").strip()
    level: str = data.get("level", "").strip()
    description: str = data.get("description", "").strip()
    timezone: str = data.get("timezone", "").strip()
    msg_id: int = int(data.get("msgId"))
    admin_id: int = int(data.get("adminId"))

    return TeacherModel(
        id=teacher_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        tel=tel,
        email=email,
        tg_id=tg_id,
        user_name=user_name,
        level=level,
        description=description,
        access_start=access_start,
        access_end=access_end,
        timezone=timezone,
        admin_id=admin_id,
        msg_id=msg_id,
    )


def parse_student_register_data(data: MultiDictProxy) -> StudentModel:
    last_name, first_name, patronymic = _parse_full_name(data)

    access_start = datetime.date(*map(int, data.get("access_start").split("-")))
    access_end = datetime.date(*map(int, data.get("access_end").split("-")))
    if access_start > access_end:
        raise RegisterFormValidateError()

    tel = data.get("tel")
    if len(tel) != 10 or not tel.isdigit():
        raise RegisterFormValidateError()
    else:
        tel = int(tel)

    student_id = int(data.get("id"))
    email: str = data.get("email", "").strip()
    tg_id: int = int(data.get("tgId"))
    user_name: str = data.get("userName", "").strip()
    timezone: str = data.get("timezone", "").strip()
    msg_id: int = int(data.get("msgId"))
    admin_id: int = int(data.get("adminId"))

    parent1 = _parse_parent(data.get("parent1", ""))
    parent2 = _parse_parent(data.get("parent2", ""))

    return StudentModel(
        id=student_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        tel=tel,
        email=email,
        tg_id=tg_id,
        user_name=user_name,
        access_start=access_start,
        access_end=access_end,
        timezone=timezone,
        admin_id=admin_id,
        msg_id=msg_id,
        parents=[parent1, parent2],
    )


def _parse_parent(parent: str) -> ParentModel | None:
    try:
        full_name, tg_id, tel = parent.split("&")

        last_name, first_name, patronymic = full_name.split()
        return ParentModel(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            tel=int(tel),
            tg_id=int(tg_id),
        )
    except ValueError:
        return


def parse_home_task_data(data: MultiDictProxy) -> HomeTaskModel | None:
    group_uuid = data.get("groupUuid")

    home_task_number = data.get("homeTaskNumber").strip()
    if not home_task_number:
        raise RegisterFormValidateError()

    try:
        lesson_date_lst = map(int, data.get("lessonDate").split("-"))
        lesson_date = datetime.date(*lesson_date_lst)

        deadline_str = data.get("deadLine")
        deadline = datetime.datetime.strptime(deadline_str, r"%Y-%m-%dT%H:%M")
    except ValueError:
        raise RegisterFormValidateError()

    description = data.get("description")

    return HomeTaskModel(
        group_uuid=group_uuid,
        home_task_number=home_task_number,
        lesson_date=lesson_date,
        deadline=deadline,
        description=description,
    )


def _parse_full_name(data: MultiDictProxy) -> tuple[str, str, str]:
    first_name: str = data.get("firstName", "").strip()
    if not first_name.isalpha():
        raise RegisterFormValidateError()

    last_name: str = data.get("lastName", "").strip()
    if not last_name.isalpha():
        raise RegisterFormValidateError()

    patronymic: str = data.get("patronymic", "").strip()
    if not patronymic.isalpha():
        raise RegisterFormValidateError()

    return last_name, first_name, patronymic


def parse_group_info_data(data: MultiDictProxy) -> GroupModel:
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    teacher_id, _ = data.get("teacher", "").split(" | ")

    return GroupModel(title=title, description=description, teacher_id=int(teacher_id))


def parse_user_sign_up_form(data: MultiDictProxy, user: WebAppUser) -> SignUpModel:
    last_name, first_name, patronymic = _parse_full_name(data)

    tel = data.get("tel", "")
    if len(tel) != 10 or not tel.isdigit():
        raise RegisterFormValidateError()
    else:
        tel = int(tel)

    email: str = data.get("email", "").strip()
    timezone: str = data.get("timezone", "").strip()

    return SignUpModel(
        telegram_id=user.id,
        user_name=user.username,
        last_name=last_name,
        first_name=first_name,
        patronymic=patronymic,
        tel=tel,
        email=email,
        timezone=timezone,
    )


def get_student_model(
    unreg_user: UnRegisteredUser,
    user_id: int,
    admin_id: int,
    access_start: datetime.date,
    access_end: datetime.date,
) -> StudentModel:
    return StudentModel(
        id=user_id,
        first_name=unreg_user.first_name,
        last_name=unreg_user.last_name,
        patronymic=unreg_user.patronymic,
        tel=unreg_user.tel,
        email=unreg_user.email,
        tg_id=unreg_user.telegram_id,
        user_name=unreg_user.user_name,
        access_start=access_start,
        access_end=access_end,
        timezone=unreg_user.timezone,
        admin_id=admin_id,
    )


def get_teacher_model(
    unreg_user: UnRegisteredUser,
    user_id: int,
    admin_id: int,
    access_start: datetime.date,
    access_end: datetime.date,
) -> TeacherModel:
    return TeacherModel(
        id=user_id,
        first_name=unreg_user.first_name,
        last_name=unreg_user.last_name,
        patronymic=unreg_user.patronymic,
        tel=unreg_user.tel,
        email=unreg_user.email,
        tg_id=unreg_user.telegram_id,
        user_name=unreg_user.user_name,
        access_start=access_start,
        access_end=access_end,
        timezone=unreg_user.timezone,
        admin_id=admin_id,
        level="",
        description="",
    )
