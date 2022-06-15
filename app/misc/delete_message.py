from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest


async def delete_last_message(bot: Bot, chat_id: int, mid: int) -> None:
    with suppress(TelegramBadRequest):
        await bot.delete_message(chat_id, mid)
