from typing import TypeVar

from app.misc.date_utils import date_format, datetime_format, utc_to_local
from app.misc.models import SignUpModel
from app.services.database.models import (
    Administrator,
    HomeTask,
    Student,
    Teacher,
    HomeWork,
    Group,
)

T = TypeVar("T", Student, Administrator, Teacher, SignUpModel)


def get_admin_info_text(admin: Administrator) -> str:
    text = [
        "<b>Администратор</b>\n\n",
        *_get_user_info_text(admin),
        *_get_employee_info_text(admin),
        f"<b>Запись активна с:</b> <code>{date_format(admin.access_start)}</code>\n"
        f"<b>Запись пассивна с:</b> <code>{date_format(admin.access_end)}</code>\n"
        f"<b>Часовой пояс:</b> <code>{admin.timezone}</code>",
    ]

    return "".join(text)


def get_teacher_info_text(teacher: Teacher, with_creator: bool = False) -> str:
    text = [
        "<b>Учитель</b>\n\n",
        *_get_user_info_text(teacher),
        *_get_employee_info_text(teacher),
        f"<b>Запись активна с:</b> <code>{date_format(teacher.access_start)}</code>\n"
        f"<b>Запись пассивна с:</b> <code>{date_format(teacher.access_end)}</code>\n"
        f"<b>Часовой пояс:</b> <code>{teacher.timezone}</code>\n\n",
    ]

    if with_creator:
        creator_full_name = f"{teacher.admin.last_name} {teacher.admin.first_name} {teacher.admin.patronymic}"
        text.append(
            f"<b>ФИО лица создавшего запись:</b>\n<code>{creator_full_name}</code>"
        )

    return "".join(text)


def get_student_info_text(student: Student) -> str:
    text = [
        "<b>Ученик</b>\n\n",
        *_get_user_info_text(student),
        f"<b>Запись активна с:</b> <code>{date_format(student.access_start)}</code>\n"
        f"<b>Запись пассивна с:</b> <code>{date_format(student.access_end)}</code>\n"
        f"<b>Часовой пояс:</b> <code>{student.timezone}</code>\n\n",
    ]

    return "".join(text)


def _get_user_info_text(user: T) -> list[str]:
    text = [
        f"<b>Фамилия:</b> <code>{user.last_name}</code>\n"
        f"<b>Имя:</b> <code>{user.first_name}</code>\n",
        f"<b>Отчество:</b> <code>{user.patronymic}</code>\n",
        f"<b>Телефон:</b> <code>+7{user.tel}</code>\n",
        f"<b>Почта:</b> <code>{user.email}</code>\n",
        f"<b>Телеграм ID:</b> <code>{user.telegram_id}</code>\n",
        f"<b>Имя пользователя:</b> <code>{user.user_name}</code>\n\n",
    ]

    return text


def _get_employee_info_text(employee: T) -> list[str]:
    text = [
        f"<b>Уровень подготовки:</b> <code>{employee.level}</code>\n"
        if employee.level
        else "",
        f"<b>Дополнительное описание:</b>\n" if employee.description else "",
        f"<code>{employee.description}</code>\n\n" if employee.description else "",
    ]

    return text


def get_home_task_text(
    home_task: HomeTask, timezone: str, extend_text: str = None
) -> str:
    text = [
        f"Домашнее задание № <code>{home_task.number}</code>\n\n",
        extend_text if extend_text else "",
        f"Дата проведенного урока: <code>{date_format(home_task.lesson_date)}</code>\n",
        f"Крайняя дата сдачи Д/З:\n<code>{datetime_format(utc_to_local(home_task.deadline, timezone))}</code>\n\n",
        "Описание по Д/З:\n" f"{home_task.description}",
    ]

    return "".join(text)


def get_home_work_text(home_work: HomeWork, timezone: str) -> str:
    text = [
        "Домашняя работа\n\n"
        f"Ученик: <code>{home_work.student.last_name} {home_work.student.first_name}</code>\n"
        f"Дата сдачи: <code>{datetime_format(utc_to_local(home_work.date, timezone))}</code>\n"
    ]

    return "".join(text)


def get_group_info_text(group: Group):
    text = [
        "Группа\n\n",
        f"Учитель: <code>{group.teacher.last_name} {group.teacher.first_name} {group.teacher.patronymic}</code>\n",
        f"Название: <code>{group.title}</code>\n\n",
        f"Описание:\n{group.description or 'Описание отсутсвует'}",
    ]

    return "".join(text)


def get_user_sign_up_text(user: SignUpModel) -> str:
    text = _get_user_info_text(user)

    return text
