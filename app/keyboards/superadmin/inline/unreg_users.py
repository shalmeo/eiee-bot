from enum import Enum

from aiogram import types
from aiogram.dispatcher.filters.callback_data import CallbackData


class UnRegUserAction(Enum):
    APPROVE = "approve"
    REJECT = "reject"


class UnRegisteredUserCallbackFactory(CallbackData, prefix="unreg"):
    telegram_id: int
    action: UnRegUserAction


def get_unreg_user_kb(telegram_id: int) -> types.InlineKeyboardMarkup:
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="Принять",
                callback_data=UnRegisteredUserCallbackFactory(
                    telegram_id=telegram_id, action=UnRegUserAction.APPROVE
                ).pack(),
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Отклонить",
                callback_data=UnRegisteredUserCallbackFactory(
                    telegram_id=telegram_id, action=UnRegUserAction.REJECT
                ).pack(),
            )
        ],
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
