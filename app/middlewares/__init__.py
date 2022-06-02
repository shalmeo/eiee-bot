from typing import Iterable

from aiogram import Dispatcher, Router
from sqlalchemy.orm import sessionmaker

from app.middlewares.db_session import DbSessionMiddleware
from app.middlewares.default_repo import RepoMiddleware
from app.middlewares.superadmin_repo import SuperAdminRepoMiddleware


def setup(
    dp: Dispatcher,
    session_maker: sessionmaker,
    routers: Iterable[Router]
) -> None:
    dp.message.outer_middleware.register(DbSessionMiddleware(session_maker))
    dp.callback_query.outer_middleware.register(DbSessionMiddleware(session_maker))
    
    dp.message.outer_middleware.register(RepoMiddleware())
    dp.callback_query.outer_middleware.register(RepoMiddleware())
    
    dp.message.middleware.register(SuperAdminRepoMiddleware())
    dp.callback_query.middleware.register(SuperAdminRepoMiddleware())
    