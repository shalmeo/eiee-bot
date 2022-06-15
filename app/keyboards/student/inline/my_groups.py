from typing import Iterable

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.services.database.models import Group


class GroupCallbackDataFactory(CallbackData, prefix="group"):
    group_uuid: str


def get_my_groups_kb(groups: Iterable[Group]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for group in groups:
        builder.button(
            text=group.title,
            callback_data=GroupCallbackDataFactory(group_uuid=group.uuid),
        )

    builder.adjust(2)

    builder.button(text="Назад", callback_data="to_profile")

    return builder.as_markup()
