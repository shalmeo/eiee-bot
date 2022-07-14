from enum import Enum
from typing import Iterable

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config_reader import Settings
from app.keyboards.superadmin.excel import ExcelCallbackFactory, ExcelAction
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.services.database.models import Group, HomeTask, Student, HomeWork


class WayCreateGroup(Enum):
    FROM_EXCEL = "from excel"


class GroupAction(Enum):
    INFO = "info"
    ALL_HOME_TASK = "all_ht"


class GroupCallbackFactory(CallbackData, prefix="group"):
    group_uuid: str
    action: GroupAction


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
            text=g.title,
            callback_data=GroupCallbackFactory(
                group_uuid=g.uuid, action=GroupAction.INFO
            ).pack(),
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
    )
    builder.row(
        InlineKeyboardButton(
            text="Экспорт EXCEL",
            callback_data=ExcelCallbackFactory(
                action=ExcelAction.EXPORT, registry=Registry.GROUPS
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Загрузить из EXCEL",
            callback_data=ExcelCallbackFactory(
                action=ExcelAction.IMPORT, registry=Registry.GROUPS
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
                text="Изменить запись",
                web_app=WebAppInfo(
                    url=f"https://{config.webhook.host}/group/change-info?{msg_id=}&id={group.uuid}"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить состав",
                web_app=WebAppInfo(
                    url=f"https://{config.webhook.host}/group/change-compound?{msg_id=}&group_uuid={group.uuid}"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                text="Реестр Д/З",
                callback_data=GroupCallbackFactory(
                    group_uuid=group.uuid, action=GroupAction.ALL_HOME_TASK
                ).pack(),
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


class HomeTaskAction(Enum):
    INFO = "info"
    ATTACHED_FILES = "attached_files"


class HomeTaskCallbackFactory(CallbackData, prefix="ht"):
    task_uuid: str
    action: HomeTaskAction


class HomeTaskPageController(CallbackData, prefix="controller"):
    offset: int
    count: int
    group_uuid: str


class StudentCallbackFactory(CallbackData, prefix="student"):
    student_id: int
    task_uuid: str


def get_select_home_tasks_kb(
    home_tasks: Iterable[HomeTask], offset: int, limit: int, count: int, group_uuid: str
) -> InlineKeyboardMarkup:
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
        InlineKeyboardButton(
            text="Назад",
            callback_data=GroupCallbackFactory(
                action=GroupAction.INFO, group_uuid=group_uuid
            ).pack(),
        )
    )

    return builder.as_markup()


def get_home_task_info_kb(
    students: Iterable[Student], task_uuid: str, group_uuid: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for s in students:
        builder.button(
            text=f"{s.last_name} {s.first_name}",
            callback_data=StudentCallbackFactory(
                student_id=s.id, task_uuid=task_uuid
            ).pack(),
        )

    builder.adjust(4)
    builder.row(
        InlineKeyboardButton(
            text="Прикрепленные файлы",
            callback_data=HomeTaskCallbackFactory(
                task_uuid=task_uuid, action=HomeTaskAction.ATTACHED_FILES
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=GroupCallbackFactory(
                action=GroupAction.ALL_HOME_TASK, group_uuid=group_uuid
            ).pack(),
        )
    )

    return builder.as_markup()


class HomeWorkAction(Enum):
    INFO = "info"
    ATTACHED_FILES = "attached_files"


class HomeWorkCallbackFactory(CallbackData, prefix="hw"):
    work_uuid: str
    action: HomeWorkAction


def get_home_works_kb(
    home_works: Iterable[HomeWork], task_uuid: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for i, hw in enumerate(home_works, 1):
        builder.button(
            text=str(i),
            callback_data=HomeWorkCallbackFactory(
                work_uuid=hw.uuid, action=HomeWorkAction.INFO
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=HomeTaskCallbackFactory(
                action=HomeTaskAction.INFO, task_uuid=task_uuid
            ).pack(),
        )
    )

    return builder.as_markup()


def get_hw_info_kb(hw_id: str, student_id: int, task_uuid: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Прикрепленные файлы",
                callback_data=HomeWorkCallbackFactory(
                    work_uuid=hw_id, action=HomeWorkAction.ATTACHED_FILES
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=StudentCallbackFactory(
                    student_id=student_id, task_uuid=task_uuid
                ).pack(),
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_import_groups_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ProfileCallbackFactory(registry=Registry.TEACHERS).pack(),
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_read_excel_kb() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="Загрузить", callback_data="load_groups")]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
