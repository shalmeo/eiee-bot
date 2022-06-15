from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_profile_kb() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="Мои группы", callback_data="my_groups")]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
