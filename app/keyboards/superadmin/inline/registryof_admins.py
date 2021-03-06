from enum import Enum
from typing import Iterable

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config_reader import Settings
from app.keyboards.superadmin.excel import ExcelCallbackFactory, ExcelAction
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory
from app.keyboards.superadmin.registry import Registry
from app.services.database.models import Administrator


class AdminAction(Enum):
    INFO = "info"
    DELETE = "delete"


class AdminCallbackFactory(CallbackData, prefix="admin"):
    admin_id: int
    action: AdminAction


class AdminPageController(CallbackData, prefix="admin_controller"):
    offset: int


def get_registryof_admins_kb(
    admins: Iterable[Administrator],
    config: Settings,
    msg_id: int,
    count: int,
    offset: int,
    limit: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for a in admins:
        builder.button(
            text=f"{a.last_name} {a.first_name}",
            callback_data=AdminCallbackFactory(
                admin_id=a.id, action=AdminAction.INFO
            ).pack(),
        )

    builder.adjust(3)
    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    builder.row(
        InlineKeyboardButton(
            text="⬅️", callback_data=AdminPageController(offset=offset - limit).pack()
        ),
        InlineKeyboardButton(text=f"{current_page}/{pages}", callback_data="none"),
        InlineKeyboardButton(
            text="➡️", callback_data=AdminPageController(offset=offset + limit).pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Создать запись",
            web_app=WebAppInfo(
                url=f"https://{config.webhook.host}/administrator/reg-form?msg_id={msg_id}"
            ),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Экспорт EXCEL",
            callback_data=ExcelCallbackFactory(
                action=ExcelAction.EXPORT, registry=Registry.ADMINISTRATORS
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Загрузить из EXCEL",
            callback_data=ExcelCallbackFactory(
                action=ExcelAction.IMPORT, registry=Registry.ADMINISTRATORS
            ).pack(),
        ),
    )

    builder.row(InlineKeyboardButton(text="Назад", callback_data="to_profile"))

    return builder.as_markup()


def get_admin_info_kb(
    config: Settings, mid: int, admin_id: int
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Изменить запись",
                web_app=WebAppInfo(
                    url=f"https://{config.webhook.host}/administrator/change-info?mid={mid}&id={admin_id}"
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Удалить",
                callback_data=AdminCallbackFactory(
                    admin_id=admin_id, action=AdminAction.DELETE
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(
                    registry=Registry.ADMINISTRATORS
                ).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_load_from_excel_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(
                    registry=Registry.ADMINISTRATORS
                ).pack(),
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_read_excel_kb() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="Загрузить", callback_data="load_admins")]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
