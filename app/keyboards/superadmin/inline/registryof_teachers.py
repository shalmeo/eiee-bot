from enum import Enum
from typing import Iterable

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config_reader import Settings
from app.keyboards.superadmin.excel import ExcelCallbackFactory, ExcelAction
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.services.database.models import Teacher


class TeacherAction(Enum):
    INFO = "info"
    CHANGE = "change"
    DELETE = "delete"


class TeacherCallbackFactory(CallbackData, prefix="teacher"):
    teacher_id: int
    action: TeacherAction


class TeacherPageController(CallbackData, prefix="teacher_controller"):
    offset: int


class WayCreateTeacher(Enum):
    FROM_EXCEL = "from excel"


class CreateRecordofTeacher(CallbackData, prefix="create_teacher"):
    way: WayCreateTeacher


def get_registryof_teachers_kb(
    teachers: Iterable[Teacher],
    config: Settings,
    msg_id: int,
    count: int,
    offset: int,
    limit: int,
    admin_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for teacher in teachers:
        builder.button(
            text=f"{teacher.last_name} {teacher.first_name}",
            callback_data=TeacherCallbackFactory(
                teacher_id=teacher.id, action=TeacherAction.INFO
            ).pack(),
        )

    builder.adjust(3)
    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    builder.row(
        InlineKeyboardButton(
            text="⬅️", callback_data=TeacherPageController(offset=offset - limit).pack()
        ),
        InlineKeyboardButton(text=f"{current_page}/{pages}", callback_data="none"),
        InlineKeyboardButton(
            text="➡️", callback_data=TeacherPageController(offset=offset + limit).pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Создать запись",
            web_app=WebAppInfo(
                url=f"https://{config.webhook.host}/teacher/reg-form?msg_id={msg_id}&admin_id={admin_id}"
            ),
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="Экспорт EXCEL",
            callback_data=ExcelCallbackFactory(
                action=ExcelAction.EXPORT, registry=Registry.TEACHERS
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Загрузить из EXCEL",
            callback_data=ExcelCallbackFactory(
                action=ExcelAction.IMPORT, registry=Registry.TEACHERS
            ).pack(),
        ),
    )

    builder.row(InlineKeyboardButton(text="Назад", callback_data="to_profile"))

    return builder.as_markup()


def get_teacher_info_kb(
    config: Settings, mid: int, teacher_id: int, is_superadmin: bool = True
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(registry=Registry.TEACHERS).pack(),
            )
        ],
    ]

    if is_superadmin:
        keyboard = [
            [
                InlineKeyboardButton(
                    text="Изменить запись",
                    web_app=WebAppInfo(
                        url=f"https://{config.webhook.host}/teacher/change-info?mid={mid}&id={teacher_id}"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data=TeacherCallbackFactory(
                        action=TeacherAction.DELETE, teacher_id=teacher_id
                    ).pack(),
                ),
            ],
        ] + keyboard

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_load_from_excel_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(registry=Registry.TEACHERS).pack(),
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_read_excel_kb() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="Загрузить", callback_data="load_teachers")]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
