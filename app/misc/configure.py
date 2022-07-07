import logging

import pytz

from aiogram import Bot, Dispatcher, F
from aiogram.dispatcher.fsm.storage.base import BaseStorage
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config_reader import config


def configure_dispatcher(storage: BaseStorage) -> Dispatcher:
    dispatcher = Dispatcher(storage=storage)
    dispatcher.message.filter(F.chat.type == "private")
    dispatcher.callback_query.filter(F.message.chat.type == "private")

    return dispatcher


def configure_postgres() -> sessionmaker:
    engine = create_async_engine(
        config.postgres.url,
        future=True,
    )

    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# def configure_scheduler(bot: Bot, session_factory: sessionmaker) -> AsyncIOScheduler:
#     scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone=pytz.utc))
#     scheduler.add_jobstore(
#         jobstore="redis",
#         jobs_key="dispatched_trips_jobs",
#         run_times_key="dispatched_trips_running",
#         host=config.redis.host,
#         port=config.redis.port,
#         # password=config.redis.password
#     )
#     scheduler.ctx.add_instance(bot, Bot)
#     scheduler.ctx.add_instance(session_factory, sessionmaker)

#     return scheduler


def configure_logging() -> None:
    logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
