from typing import Iterable

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.services.database.models import HomeTask
from app.keyboards.student.inline.current_tasks import (
    HomeTaskCallbackFactory,
    HomeTaskAction,
    GroupCallbackFactory,
    GroupAction,
)


def get_overdue_tasks_kb(
    tasks: Iterable[HomeTask], group_uuid: str
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for t in tasks:
        builder.button(
            text=t.number,
            callback_data=HomeTaskCallbackFactory(
                home_task_uuid=t.uuid, action=HomeTaskAction.INFO
            ),
        )

    builder.adjust(3)

    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=GroupCallbackFactory(
                group_uuid=group_uuid, action=GroupAction.CUR_TASKS
            ).pack(),
        )
    )

    return builder.as_markup()
