from enum import Enum

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class Registry(Enum):
    ADMINISTRATORS = "admins"
    TEACHERS = "teachers"
    STUDENTS = "students"
    GROUPS = "groups"
    HOME_TASKS = "home tasks"


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
        # [
        #     InlineKeyboardButton(
        #         text='Реестр домашних заданий',
        #         callback_data=ProfileCallbackFactory(registry=Registry.HOME_TASKS).pack()
        #     )
        # ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
