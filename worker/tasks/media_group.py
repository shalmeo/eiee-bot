import logging

from aiogram import Bot
from aiogram.dispatcher.fsm.storage.redis import StorageKey
from arq import ArqRedis
from app.keyboards.student.inline.current_tasks import get_input_file_kb

from app.misc.delete_message import delete_last_message
from worker.storage.redis import ArqRedisStorage

logger = logging.getLogger(__name__)


async def handle_media_group_task(
    ctx, chat_id: int, media_group_id: str, callback: str
):
    bot: Bot = ctx["bot"]
    redis: ArqRedis = ctx["redis"]
    storage: ArqRedisStorage = ctx["storage"]

    media_group = await redis.zrangebyscore(
        f"media_group:{media_group_id}",
    )

    key = StorageKey(bot.id, chat_id, chat_id)

    data = await storage.get_data(bot, key)
    files = data["files"]

    for m in media_group:
        file_id, file_type = m.split(":")
        files.append((file_id, file_type))

    await delete_last_message(bot, chat_id, data["mid"])
    markup = get_input_file_kb(callback=callback)
    m = await bot.send_message(
        chat_id,
        f"Отправлено файлов: <code>{len(files)}</code>\n\n"
        "Если количество файлов не соответствует отправленным, попробуйте отправить еще раз по одному файлу",
        reply_markup=markup,
    )

    await storage.update_data(bot, key, {"files": files, "mid": m.message_id})
