from enum import Enum
from typing import Iterable

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config_reader import Settings
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.services.database.models import Student


class StudentCallbackFactory(CallbackData, prefix="student"):
    student_id: int


class StudentPageController(CallbackData, prefix="student_controller"):
    offset: int


class WayCreateStudent(Enum):
    FROM_EXCEL = "create record from excel"


class CreateRecordofStudent(CallbackData, prefix="create_student"):
    way: WayCreateStudent


class ParentCallbackFactory(CallbackData, prefix="parent"):
    student_id: int


def get_registryof_students_kb(
    students: Iterable[Student],
    config: Settings,
    msg_id: int,
    count: int,
    offset: int,
    limit: int,
    admin_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in students:
        builder.button(
            text=f"{s.last_name} {s.first_name}",
            callback_data=StudentCallbackFactory(student_id=s.id).pack(),
        )

    builder.adjust(3)
    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    builder.row(
        InlineKeyboardButton(
            text="⬅️", callback_data=StudentPageController(offset=offset - limit).pack()
        ),
        InlineKeyboardButton(text=f"{current_page}/{pages}", callback_data="none"),
        InlineKeyboardButton(
            text="➡️", callback_data=StudentPageController(offset=offset + limit).pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Создать запись",
            web_app=WebAppInfo(
                url=f"https://{config.webhook.host}/student/reg-form?{msg_id=}&{admin_id=}"
            ),
        ),
        InlineKeyboardButton(
            text="Загрузить из EXCEL",
            callback_data=CreateRecordofStudent(way=WayCreateStudent.FROM_EXCEL).pack(),
        ),
    )
    builder.row(InlineKeyboardButton(text="Назад", callback_data="to_profile"))

    return builder.as_markup()


def get_student_info_kb(
    config: Settings, mid: int, student_id: int
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Изменить запись",
                web_app=WebAppInfo(
                    url=f"https://{config.webhook.host}/student/change-info?mid={mid}&id={student_id}"
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Родители",
                callback_data=ParentCallbackFactory(student_id=student_id).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(registry=Registry.STUDENTS).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_load_from_excel_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(registry=Registry.STUDENTS).pack(),
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_read_excel_kb() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="Загрузить", callback_data="load_students")]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_parents_info_kb(sid: int, config: Settings, mid: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Изменить запись",
                web_app=WebAppInfo(
                    url=f"https://{config.webhook.host}/student/change-parents-info?mid={mid}&id={sid}"
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=StudentCallbackFactory(student_id=sid).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
