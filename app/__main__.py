import asyncio
import logging

from aiohttp import web
from aiogram import Bot
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from arq import create_pool
from arq.connections import RedisSettings

from app import endpoints, handlers, middlewares
from app.config_reader import config
from app.misc.tasks import Tasks
from app.misc.configure import (
    configure_dispatcher,
    configure_logging,
    configure_postgres,
)
from app.misc.routers import (
    create_admin_router,
    create_student_router,
    create_superadmin_router,
    create_teacher_router,
    create_guest_router,
)
from app.misc.webhook import create_app, setup_app_runner, setup_webhook
from app.services.database.misc import add_initial_admin

logger = logging.getLogger(__name__)


async def main():
    # Creating
    storage = RedisStorage.from_url(url=config.redis.url)
    bot = Bot(token=config.bot_token, parse_mode="HTML")
    dispatcher = configure_dispatcher(storage)
    session_factory = configure_postgres()
    redis = await create_pool(
        RedisSettings(host=config.redis.host, port=config.redis.port)
    )
    app = create_app(dispatcher, bot, config)

    # setup
    superadmin_router = create_superadmin_router(dispatcher)
    admin_router = create_admin_router(dispatcher)
    teacher_router = create_teacher_router(dispatcher)
    student_router = create_student_router(dispatcher)
    guest_router = create_guest_router(dispatcher)

    dispatcher["config"] = config
    dispatcher["redis"] = redis
    dispatcher["tasks"] = Tasks(redis)

    app["bot"] = bot
    app["session_factory"] = session_factory
    app["config"] = config
    app["storage"] = storage

    middlewares.setup(
        dispatcher,
        session_factory,
        (superadmin_router, admin_router, teacher_router, student_router),
    )
    handlers.setup(
        (superadmin_router, admin_router, teacher_router, student_router, guest_router)
    )
    endpoints.setup(app)

    await add_initial_admin(session_factory, config.bot_admin)

    configure_logging()

    try:
        logger.info("Starting bot")
        await setup_webhook(bot, config)
        runner = await setup_app_runner(app)
        site = web.TCPSite(runner, host="0.0.0.0", port=5500)
        await site.start()
        logger.info(f"Running on: http://{site._host}:{site._port}")
        await asyncio.Event().wait()
    finally:
        await storage.close()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logger.error("Bot stopped!")
