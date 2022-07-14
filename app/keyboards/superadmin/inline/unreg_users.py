from enum import Enum
from typing import Literal, Iterable

from aiogram import types
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.services.database.models import UnRegisteredUser


class UnRegUserAction(Enum):
    INFO = "info"
    APPROVE = "approve"
    REJECT = "reject"


class UnRegisteredUserCallbackFactory(CallbackData, prefix="unreg"):
    telegram_id: int
    action: UnRegUserAction


class UnRegisteredUserPageController(CallbackData, prefix="controller"):
    offset: int


class SelectRoleCallbackFactory(CallbackData, prefix="select"):
    role: Literal["teacher", "student"]
    telegram_id: int


def get_unreg_users_kb(
    users: Iterable[UnRegisteredUser], count: int, offset: int, limit: int
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for u in users:
        builder.button(
            text=f"{u.last_name} {u.first_name}",
            callback_data=UnRegisteredUserCallbackFactory(
                telegram_id=u.telegram_id, action=UnRegUserAction.INFO
            ).pack(),
        )

    builder.adjust(3)

    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    builder.row(
        types.InlineKeyboardButton(
            text="⬅️",
            callback_data=UnRegisteredUserPageController(offset=offset - limit).pack(),
        ),
        types.InlineKeyboardButton(
            text=f"{current_page}/{pages}", callback_data="none"
        ),
        types.InlineKeyboardButton(
            text="➡️",
            callback_data=UnRegisteredUserPageController(offset=offset + limit).pack(),
        ),
    )

    builder.row(types.InlineKeyboardButton(text="Назад", callback_data="to_profile"))

    return builder.as_markup()


def get_select_role_kb(telegram_id: int) -> types.InlineKeyboardMarkup:
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="Учитель",
                callback_data=SelectRoleCallbackFactory(
                    role="teacher", telegram_id=telegram_id
                ).pack(),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Ученик",
                callback_data=SelectRoleCallbackFactory(
                    role="student", telegram_id=telegram_id
                ).pack(),
            ),
        ],
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_unreg_user_kb(telegram_id: int) -> types.InlineKeyboardMarkup:
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="Принять",
                callback_data=UnRegisteredUserCallbackFactory(
                    telegram_id=telegram_id,
                    action=UnRegUserAction.APPROVE,
                ).pack(),
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Отклонить",
                callback_data=UnRegisteredUserCallbackFactory(
                    telegram_id=telegram_id,
                    action=UnRegUserAction.REJECT,
                ).pack(),
            )
        ],
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
