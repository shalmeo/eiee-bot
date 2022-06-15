from typing import TypeVar

from app.misc.date_formatter import date_format
from app.services.database.models import Administrator, Student, Teacher

T = TypeVar("T", Student, Administrator, Teacher)


def get_admin_info_text(admin: Administrator) -> str:
    text = [
        "<b>Администратор</b>\n\n",
        *_get_user_info_text(admin),
        *_get_employee_info_text(admin),
        f"<b>Запись активна с:</b> <code>{date_format(admin.access_start)}</code>\n"
        f"<b>Запись пассивна с:</b> <code>{date_format(admin.access_start)}</code>\n"
        f"<b>Часовой пояс:</b> <code>{admin.timezone}</code>",
    ]

    return "".join(text)


def get_teacher_info_text(teacher: Teacher, with_creator: bool = False) -> str:
    text = [
        "<b>Учитель</b>\n\n",
        *_get_user_info_text(teacher),
        *_get_employee_info_text(teacher),
        f"<b>Запись активна с:</b> <code>{date_format(teacher.access_start)}</code>\n"
        f"<b>Запись пассивна с:</b> <code>{date_format(teacher.access_start)}</code>\n"
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
        f"<b>Запись пассивна с:</b> <code>{date_format(student.access_start)}</code>\n"
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
        f"<b>Телеграм ID:</b> <code>{user.id}</code>\n",
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
