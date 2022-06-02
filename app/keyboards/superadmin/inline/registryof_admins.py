from enum import Enum
from typing import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp, WebAppInfo
from aiogram.dispatcher.filters.callback_data import CallbackData

from app.config_reader import Settings
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.services.database.models import Administrator


class WayCreateAdmin(Enum):
    MANUALLY = 'create admin manually'
    FROM_EXCEL = 'create admin from excel'


class ReadAdminCallbackFactory(CallbackData, prefix='admin'):
    admin_id: int
    

class CreateRecordofAdmin(CallbackData, prefix='create_record'):
    way: WayCreateAdmin
    

class PageController(CallbackData, prefix='controller'):
    offset: int


def get_registryof_admins_kb(
    admins: Iterable[Administrator], 
    config: Settings,
    msg_id: int,
    count: int,
    offset: int,
    limit: int
) -> InlineKeyboardMarkup:
    keyboard = []
    
    row = []
    for admin in admins:        
        surname, name, _ = admin.full_name.split()
        row.append(
            InlineKeyboardButton(
                text=f'{surname} {name}',
                callback_data=ReadAdminCallbackFactory(admin_id=admin.id).pack()
                )
            )
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row: keyboard.append(row)
    
    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1
    
    keyboard.append([
        InlineKeyboardButton(
            text='⬅️', 
            callback_data=PageController(offset=offset - limit).pack()
        ),
        InlineKeyboardButton(
            text=f'{current_page}/{pages}',
            callback_data='none'
        ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=PageController(offset=offset + limit).pack()
        )
    ])
        
    keyboard.append([
        MenuButtonWebApp(
            text='Создать запись',
            web_app=WebAppInfo(url=f'https://{config.webhook.host}/administrator/reg-form?msg_id={msg_id}')
        ),
        InlineKeyboardButton(
            text='Загрузить из EXCEL',
            callback_data=CreateRecordofAdmin(way=WayCreateAdmin.FROM_EXCEL).pack()
        ),
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text='Назад',
            callback_data='to_profile'
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_info_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=ProfileCallbackFactory(registry=Registry.ADMINISTRATORS)
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)