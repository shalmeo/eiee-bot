from enum import Enum
from typing import Iterable

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.student.inline.profile import ProfileAction, ProfileCallbackFactory
from app.services.database.models import HomeTask


class HomeTaskAction(Enum):
    INFO = "info"
    ATTACH_HOME_WORK = "attach work"
    ATTACHED_FILES = "attached files"


class GroupAction(Enum):
    CUR_TASKS = "cur tasks"
    IN_CHECK = "in check"


class HomeTaskCallbackFactory(CallbackData, prefix="home_task"):
    home_task_uuid: str
    action: HomeTaskAction


class GroupCallbackFactory(CallbackData, prefix="group"):
    group_uuid: str
    action: GroupAction


class HomeTaskPageController(CallbackData, prefix="controller"):
    offset: int
    count: int
    group_uuid: str


def get_current_tasks_kb(
    tasks: Iterable[HomeTask], offset: int, limit: int, count: int, group_uuid: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for t in tasks:
        builder.button(
            text=t.number,
            callback_data=HomeTaskCallbackFactory(
                action=HomeTaskAction.INFO, home_task_uuid=t.uuid
            ).pack(),
        )

    builder.adjust(3)

    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    builder.row(
        InlineKeyboardButton(
            text="⬅️",
            callback_data=HomeTaskPageController(
                offset=offset - limit, count=count, group_uuid=group_uuid
            ).pack(),
        ),
        InlineKeyboardButton(text=f"{current_page}/{pages}", callback_data="none"),
        InlineKeyboardButton(
            text="➡️",
            callback_data=HomeTaskPageController(
                offset=offset + limit, count=count, group_uuid=group_uuid
            ).pack(),
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=ProfileCallbackFactory(
                action=ProfileAction.CURRENT_TASKS
            ).pack(),
        )
    )

    return builder.as_markup()


def get_home_task_info_kb(home_task_uuid: str, group_uuid: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Посмотреть прикрепленные файлы",
                callback_data=HomeTaskCallbackFactory(
                    action=HomeTaskAction.ATTACHED_FILES,
                    home_task_uuid=home_task_uuid,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Прикрепить Д/З",
                callback_data=HomeTaskCallbackFactory(
                    action=HomeTaskAction.ATTACH_HOME_WORK,
                    home_task_uuid=home_task_uuid,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=GroupCallbackFactory(
                    group_uuid=group_uuid, action=GroupAction.CUR_TASKS
                ).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_input_file_kb(callback: str) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="Прикрепить", callback_data=callback)]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_select_group_kb(groups: Iterable[tuple], action: GroupAction):
    builder = InlineKeyboardBuilder()

    for uuid, title in groups:
        builder.button(
            text=title,
            callback_data=GroupCallbackFactory(
                group_uuid=str(uuid), action=action
            ).pack(),
        )

    builder.adjust(3)

    builder.row(InlineKeyboardButton(text="Назад", callback_data="to_profile"))

    return builder.as_markup()
