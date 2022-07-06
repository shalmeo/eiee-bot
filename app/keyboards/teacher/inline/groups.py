from enum import Enum
from typing import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.dispatcher.filters.callback_data import CallbackData
from app.config_reader import Settings

from app.keyboards.teacher.inline.profile import ProfileAction, ProfileCallbackFactory
from app.services.database.models import Group


class GroupAction(Enum):
    INFO = "group info"
    CREATE_HOME_TASK = "create home task"
    CHECK_HOME_WORK = "check home work"


class GroupCallbackFactory(CallbackData, prefix="group"):
    group_uuid: str
    action: GroupAction


class AttachFilesCallbackFactory(CallbackData, prefix="attach_files"):
    task_uuid: str


def get_groups_kb(groups: Iterable[Group], action: GroupAction) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for g in groups:
        builder.add(
            InlineKeyboardButton(
                text=g.title,
                callback_data=GroupCallbackFactory(
                    group_uuid=g.uuid, action=action
                ).pack(),
            )
        )

    builder.adjust(3)

    builder.row(InlineKeyboardButton(text="Назад", callback_data="to_profile"))

    return builder.as_markup()


def get_group_info_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(
                    action=ProfileAction.GROUPS
                ).pack(),
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_create_home_task_kb(
    group: Group, msg_id: int = None, config: Settings = None, with_webapp: bool = True
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(
                    action=ProfileAction.CREATE_HOMETASK
                ).pack(),
            )
        ],
    ]

    if with_webapp:
        url = f"https://{config.webhook.host}/teacher/create-home-task-form?group_uuid={group.uuid}&msg_id={msg_id}"

        keyboard.insert(
            0,
            [
                InlineKeyboardButton(
                    text="Создать Д/З",
                    web_app=WebAppInfo(url=url),
                )
            ],
        )
    else:
        keyboard.insert(
            0,
            [
                InlineKeyboardButton(
                    text="Прикрепить материалы для Д/З",
                    callback_data=AttachFilesCallbackFactory(
                        task_uuid=group.uuid
                    ).pack(),
                )
            ],
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
