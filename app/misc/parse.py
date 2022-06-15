import datetime

from multidict import MultiDictProxy

from app.misc.exceptions import RegisterFormValidateError
from app.misc.models import AdminModel, ParentModel, StudentModel, TeacherModel


def parse_admin_register_data(data: MultiDictProxy) -> AdminModel | None:
    first_name: str = data.get("firstName").strip()
    if not first_name.isalpha():
        raise RegisterFormValidateError()

    last_name: str = data.get("lastName").strip()
    if not last_name.isalpha():
        raise RegisterFormValidateError()

    patronymic: str = data.get("patronymic").strip()
    if not patronymic.isalpha():
        raise RegisterFormValidateError()

    access_start = datetime.date(*map(int, data.get("access_start").split("-")))
    access_end = datetime.date(*map(int, data.get("access_end").split("-")))
    if access_start > access_end:
        raise RegisterFormValidateError()

    tel: str = data.get("tel")
    if len(tel) != 10 or not tel.isdigit():
        raise RegisterFormValidateError()
    else:
        tel = int(tel)

    email: str = data.get("email").strip()
    tg_id: int = int(data.get("tgId"))
    user_name: str = data.get("userName").strip()
    level: str = data.get("level").strip()
    description: str = data.get("description").strip()
    timezone: str = data.get("timezone").strip()
    msg_id: int = int(data.get("msgId"))

    return AdminModel(
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


def parse_teacher_register_data(data: MultiDictProxy) -> TeacherModel | None:
    first_name: str = data.get("firstName").strip()
    if not first_name.isalpha():
        raise RegisterFormValidateError()

    last_name: str = data.get("lastName").strip()
    if not last_name.isalpha():
        raise RegisterFormValidateError()

    patronymic: str = data.get("patronymic").strip()
    if not patronymic.isalpha():
        raise RegisterFormValidateError()

    access_start = datetime.date(*map(int, data.get("access_start").split("-")))
    access_end = datetime.date(*map(int, data.get("access_end").split("-")))
    if access_start > access_end:
        raise RegisterFormValidateError()

    tel: str = data.get("tel")
    if len(tel) != 10 or not tel.isdigit():
        raise RegisterFormValidateError()
    else:
        tel = int(tel)

    email: str = data.get("email").strip()
    tg_id: int = int(data.get("tgId"))
    user_name: str = data.get("userName").strip()
    level: str = data.get("level").strip()
    description: str = data.get("description").strip()
    timezone: str = data.get("timezone").strip()
    msg_id: int = int(data.get("msgId"))
    admin_id: int = int(data.get("adminId"))

    return TeacherModel(
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


def parse_student_register_data(data: MultiDictProxy) -> StudentModel | None:
    print(data)

    first_name: str = data.get("firstName").strip()
    if not first_name.isalpha():
        raise RegisterFormValidateError()

    last_name: str = data.get("lastName").strip()
    if not last_name.isalpha():
        raise RegisterFormValidateError()

    patronymic: str = data.get("patronymic").strip()
    if not patronymic.isalpha():
        raise RegisterFormValidateError()

    access_start = datetime.date(*map(int, data.get("access_start").split("-")))
    access_end = datetime.date(*map(int, data.get("access_end").split("-")))
    if access_start > access_end:
        raise RegisterFormValidateError()

    tel: str = data.get("tel")
    if len(tel) != 10 or not tel.isdigit():
        raise RegisterFormValidateError()
    else:
        tel = int(tel)

    email: str = data.get("email").strip()
    tg_id: int = int(data.get("tgId"))
    user_name: str = data.get("userName").strip()
    timezone: str = data.get("timezone").strip()
    msg_id: int = int(data.get("msgId"))
    admin_id: int = int(data.get("adminId"))

    try:
        parent1 = _parse_parent(data.get("parent1"))
        parent2 = _parse_parent(data.get("parent2"))
    except ValueError:
        raise RegisterFormValidateError()

    return StudentModel(
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


def _parse_parent(parent: str) -> ParentModel:
    full_name, tg_id, tel = parent.split("&")

    last_name, first_name, patronymic = full_name.split()

    return ParentModel(
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        tel=int(tel),
        tg_id=int(tg_id),
    )
