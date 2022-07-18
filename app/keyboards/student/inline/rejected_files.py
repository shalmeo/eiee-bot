import uuid

from aiogram import types
from aiogram.dispatcher.filters.callback_data import CallbackData


class RejectedFilesCallbackFactory(CallbackData, prefix="rej_files"):
    work_uuid: uuid.UUID


def get_rejected_files_kb(work_uuid: uuid.UUID) -> types.InlineKeyboardMarkup:
    keyboard = [
        [
            types.InlineKeyboardButton(
                text="Посмотреть прикрепленные файлы",
                callback_data=RejectedFilesCallbackFactory(work_uuid=work_uuid).pack(),
            )
        ]
    ]

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
