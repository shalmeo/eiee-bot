from aiogram import types


def get_work_files_kb() -> types.ReplyKeyboardMarkup:
    keyboard = [
        [
            types.KeyboardButton(
                text="Принять Д/З",
            ),
            types.KeyboardButton(
                text="В доработку",
            ),
        ],
        [types.KeyboardButton(text="Назад")],
    ]

    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
