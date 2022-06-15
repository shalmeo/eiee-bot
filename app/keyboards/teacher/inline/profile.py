from enum import Enum

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class ProfileAction(Enum):
    GROUPS = "groups"
    CREATE_HOMETASK = "create home task"
    CHECK_HOMETASK = "check home task"


class ProfileCallbackFactory(CallbackData, prefix="profile"):
    action: ProfileAction


def get_profile_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Ознакомится с перечнем и составом групп",
                callback_data=ProfileCallbackFactory(
                    action=ProfileAction.GROUPS
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Создать домашнее задание",
                callback_data=ProfileCallbackFactory(
                    action=ProfileAction.CREATE_HOMETASK
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Проверить выполненное Д/З",
                callback_data=ProfileCallbackFactory(
                    action=ProfileAction.CHECK_HOMETASK
                ).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
