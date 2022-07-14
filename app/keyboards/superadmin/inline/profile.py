from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.superadmin.registry import Registry


class ProfileCallbackFactory(CallbackData, prefix="profile"):
    registry: Registry


def get_profile_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Реестр администраторов",
                callback_data=ProfileCallbackFactory(
                    registry=Registry.ADMINISTRATORS
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Реестр учителей",
                callback_data=ProfileCallbackFactory(registry=Registry.TEACHERS).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Реестр учеников",
                callback_data=ProfileCallbackFactory(registry=Registry.STUDENTS).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Реестр групп",
                callback_data=ProfileCallbackFactory(registry=Registry.GROUPS).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Неопределенные пользователи",
                callback_data=ProfileCallbackFactory(registry=Registry.UNREG).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
