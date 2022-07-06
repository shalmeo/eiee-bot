from enum import Enum
from typing import Iterable

from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.dispatcher.filters.callback_data import CallbackData

from app.keyboards.teacher.inline.groups import GroupAction, GroupCallbackFactory
from app.keyboards.teacher.inline.profile import ProfileAction, ProfileCallbackFactory
from app.services.database.models import HomeTask, HomeWork


class HomeTaskAction(Enum):
    INFO = "info"
    IN_CHECK = "in check"
    COMPLETED = "completed"
    NOT_DIRECT = "not direct"


class HomeWorkAction(Enum):
    INFO = "info"
    ATTACHED_FILES = "attached files"
    ACCEPT_HW = "accept hw"
    REJECT_HW = "reject hw"


class RejectHomeWorkAction(Enum):
    WITH_MSG = "with msg"
    WITHOUT_MSG = "without msg"


class HomeTaskCallbackFactory(CallbackData, prefix="ht"):
    task_uuid: str
    action: HomeTaskAction


class HomeTaskPageController(CallbackData, prefix="controller"):
    offset: int
    count: int
    group_uuid: str


class HomeWorkCallbackFactory(CallbackData, prefix="hw"):
    work_uuid: str
    action: HomeWorkAction


class RejectHomeWorkCallbackFactory(CallbackData, prefix="reject"):
    action: RejectHomeWorkAction
    work_uuid: str


def get_select_home_tasks_kb(
    home_tasks: Iterable[HomeTask], offset: int, limit: int, count: int, group_uuid: str
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for t in home_tasks:
        builder.button(
            text=str(t.number),
            callback_data=HomeTaskCallbackFactory(
                task_uuid=t.uuid, action=HomeTaskAction.INFO
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
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=ProfileCallbackFactory(
                action=ProfileAction.CHECK_HOMEWORKS
            ).pack(),
        )
    )

    return builder.as_markup()


def get_home_task_info_kb(
    task_uuid: str, group_uuid: str
) -> types.InlineKeyboardMarkup:
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="Выполненные",
                callback_data=HomeTaskCallbackFactory(
                    task_uuid=task_uuid, action=HomeTaskAction.COMPLETED
                ).pack(),
            )
        ],
        # [
        #     types.InlineKeyboardButton(
        #         text="Не направлены",
        #         callback_data=HomeTaskCallbackFactory(
        #             task_uuid=task_uuid, action=HomeTaskAction.NOT_DIRECT
        #         ).pack(),
        #     )
        # ],
        [
            types.InlineKeyboardButton(
                text="В проверке",
                callback_data=HomeTaskCallbackFactory(
                    task_uuid=task_uuid, action=HomeTaskAction.IN_CHECK
                ).pack(),
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=GroupCallbackFactory(
                    group_uuid=group_uuid, action=GroupAction.CHECK_HOME_WORK
                ).pack(),
            )
        ],
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_check_home_work_kb(
    task_uuid: str, home_works: Iterable[HomeWork]
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for hw in home_works:
        builder.button(
            text=f"{hw.student.last_name} {hw.student.first_name}",
            callback_data=HomeWorkCallbackFactory(
                work_uuid=hw.uuid, action=HomeWorkAction.INFO
            ).pack(),
        )

    builder.adjust(3)

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=HomeTaskCallbackFactory(
                task_uuid=task_uuid, action=HomeTaskAction.INFO
            ).pack(),
        )
    )

    return builder.as_markup()


def get_home_work_info_kb(work_uuid: str, task_uuid: str) -> types.InlineKeyboardMarkup:
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="Посмотреть прикрепленные файлы",
                callback_data=HomeWorkCallbackFactory(
                    work_uuid=work_uuid, action=HomeWorkAction.ATTACHED_FILES
                ).pack(),
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Принять Д/З",
                callback_data=HomeWorkCallbackFactory(
                    work_uuid=work_uuid, action=HomeWorkAction.ACCEPT_HW
                ).pack(),
            )
        ],
        [
            types.InlineKeyboardButton(
                text="В доработку",
                callback_data=HomeWorkCallbackFactory(
                    work_uuid=work_uuid, action=HomeWorkAction.REJECT_HW
                ).pack(),
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=HomeTaskCallbackFactory(
                    task_uuid=task_uuid, action=HomeTaskAction.IN_CHECK
                ).pack(),
            )
        ],
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_reject_home_work(work_uuid: str) -> types.InlineKeyboardMarkup:
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="Отклонить без комментария",
                callback_data=RejectHomeWorkCallbackFactory(
                    work_uuid=work_uuid, action=RejectHomeWorkAction.WITHOUT_MSG
                ).pack(),
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=HomeWorkCallbackFactory(
                    work_uuid=work_uuid, action=HomeWorkAction.INFO
                ).pack(),
            )
        ],
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_reject_msg_kb(work_uuid: str) -> types.InlineKeyboardMarkup:
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="Отправить",
                callback_data=RejectHomeWorkCallbackFactory(
                    work_uuid=work_uuid, action=RejectHomeWorkAction.WITH_MSG
                ).pack(),
            )
        ]
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
