from typing import Iterable

from aiogram import Dispatcher, Router
from sqlalchemy.orm import sessionmaker

from app.middlewares.db_session import DbSessionMiddleware
from app.middlewares.album_handler import AlbumMiddleware
from app.middlewares.loggerm import LoggerMiddleware
from app.middlewares.repo import (
    RepoMiddleware,
    SuperAdminRepoMiddleware,
    AdminRepoMiddleware,
    StudentRepoMiddleware,
    TeacherRepoMiddleware,
)


def setup(
    dp: Dispatcher, session_maker: sessionmaker, routers: Iterable[Router]
) -> None:
    superadmin_router, admin_router, teacher_router, student_router = routers
    
    # dp.message.outer_middleware.register(LoggerMiddleware())
    # dp.callback_query.outer_middleware.register(LoggerMiddleware())
    
    
    dp.message.outer_middleware.register(DbSessionMiddleware(session_maker))
    dp.callback_query.outer_middleware.register(DbSessionMiddleware(session_maker))

    dp.message.outer_middleware.register(RepoMiddleware())
    dp.callback_query.outer_middleware.register(RepoMiddleware())
    
    # dp.message.middleware.register(AlbumMiddleware())

    superadmin_router.message.middleware.register(SuperAdminRepoMiddleware())
    superadmin_router.callback_query.middleware.register(SuperAdminRepoMiddleware())

    admin_router.callback_query.middleware.register(AdminRepoMiddleware())
    admin_router.message.middleware.register(AdminRepoMiddleware())

    teacher_router.callback_query.middleware.register(TeacherRepoMiddleware())
    teacher_router.message.middleware.register(TeacherRepoMiddleware())

    student_router.callback_query.middleware.register(StudentRepoMiddleware())
    student_router.message.middleware.register(StudentRepoMiddleware())
