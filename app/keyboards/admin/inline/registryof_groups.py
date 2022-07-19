from typing import Iterable

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config_reader import Settings
from app.keyboards.admin.inline.profile import ProfileCallbackFactory, Registry
from app.services.database.models import Group


class GroupCallbackFactory(CallbackData, prefix="group"):
    group_uuid: str


class GroupPageController(CallbackData, prefix="group_controller"):
    offset: int


def get_registryof_groups_kb(
    groups: Iterable[Group],
    count: int,
    offset: int,
    limit: int,
    config: Settings,
    msg_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for g in groups:
        builder.button(
            text=g.title, callback_data=GroupCallbackFactory(group_uuid=g.uuid).pack()
        )

    builder.adjust(3)
    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    builder.row(
        InlineKeyboardButton(
            text="⬅️", callback_data=GroupPageController(offset=offset - limit).pack()
        ),
        InlineKeyboardButton(text=f"{current_page}/{pages}", callback_data="none"),
        InlineKeyboardButton(
            text="➡️", callback_data=GroupPageController(offset=offset + limit).pack()
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="Создать запись",
            web_app=WebAppInfo(
                url=f"https://{config.webhook.host}/group/create-form?{msg_id=}"
            ),
        ),
    )

    builder.row(InlineKeyboardButton(text="Назад", callback_data="to_profile"))

    return builder.as_markup()


def get_group_info_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(registry=Registry.GROUPS).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
