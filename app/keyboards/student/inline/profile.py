from enum import Enum

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.callback_data import CallbackData


class ProfileAction(Enum):
    CURRENT_TASKS = "current tasks"
    IN_CHECK = "in check"
    ACCEPTED = "accepted"


class ProfileCallbackFactory(CallbackData, prefix="profile"):
    action: ProfileAction


def get_profile_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Домашние задания",
                callback_data=ProfileCallbackFactory(
                    action=ProfileAction.CURRENT_TASKS
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="В проверке",
                callback_data=ProfileCallbackFactory(
                    action=ProfileAction.IN_CHECK
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Выполненные",
                callback_data=ProfileCallbackFactory(
                    action=ProfileAction.ACCEPTED
                ).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
