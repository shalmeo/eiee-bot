from enum import Enum
from typing import Iterable

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config_reader import Settings
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.services.database.models import Group


class WayCreateGroup(Enum):
    FROM_EXCEL = "from excel"


class GroupCallbackFactory(CallbackData, prefix="group"):
    group_uuid: str


class GroupPageController(CallbackData, prefix="group_controller"):
    offset: int


class CreateGroupCallbackFactory(CallbackData, prefix="create_group"):
    way: WayCreateGroup


def get_registryof_groups_kb(
    groups: Iterable[Group],
    count: int,
    offset: int,
    limit: int,
    msg_id: int,
    config: Settings,
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
                url=f"https://{config.webhook.host}/group/create-form?msg_id={msg_id}"
            ),
        ),
        InlineKeyboardButton(
            text="Загрузить из EXCEL",
            callback_data=CreateGroupCallbackFactory(
                way=WayCreateGroup.FROM_EXCEL
            ).pack(),
        ),
    )
    builder.row(InlineKeyboardButton(text="Назад", callback_data="to_profile"))

    return builder.as_markup()


def get_create_group_kb(
    group: Group, config: Settings, msg_id: int
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Изменить состав",
                web_app=WebAppInfo(
                    url=f"https://{config.webhook.host}/group/change-compound?msg_id={msg_id}&group_uuid={group.uuid}"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(registry=Registry.GROUPS).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
