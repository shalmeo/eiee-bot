from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_menu_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text='Профиль')
        ]
    ]
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)