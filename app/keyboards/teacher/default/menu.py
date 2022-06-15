from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_menu_kb() -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text="Профиль")]]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
