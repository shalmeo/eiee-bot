import logging

from aiogram import Bot
from arq import run_worker
from arq.connections import RedisSettings

from app.config_reader import config
from app.misc.configure import configure_logging
from app.config_reader import config
from worker.storage.redis import ArqRedisStorage
from worker.tasks.media_group import handle_media_group_task
from worker.tasks.send_msg import send_message_task


logger = logging.getLogger(__name__)


async def startup(ctx: dict):
    ctx["bot"] = Bot(config.bot_token, parse_mode="HTML")
    ctx["storage"] = ArqRedisStorage(redis=ctx["redis"])


async def shutdown(ctx: dict):
    bot: Bot = ctx.pop("bot")
    await bot.session.close()


class WorkerSettings:
    on_startup = startup
    on_shutdown = shutdown
    functions = [handle_media_group_task, send_message_task]


def main():
    configure_logging()
    run_worker(WorkerSettings, redis_settings=RedisSettings(host=config.redis.host, port=config.redis.port, password=config.redis.password))


main()
