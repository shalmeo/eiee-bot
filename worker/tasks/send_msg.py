import logging

from aiogram import Bot

logger = logging.getLogger(__name__)


async def send_message_task(ctx, chat_id: int, text):
    bot: Bot = ctx["bot"]

    await bot.send_message(chat_id, text)
    logger.info(f"Message successfully sent: {chat_id=}")
