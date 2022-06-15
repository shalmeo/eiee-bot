from typing import Iterable

from aiogram import Dispatcher, Router
from sqlalchemy.orm import sessionmaker

from app.middlewares.db_session import DbSessionMiddleware
from app.middlewares.default_repo import RepoMiddleware
from app.middlewares.superadmin_repo import SuperAdminRepoMiddleware
from app.middlewares.admin_repo import AdminRepoMiddleware
from app.middlewares.student_repo import StudentRepoMiddleware


def setup(
    dp: Dispatcher,
    session_maker: sessionmaker,
    routers: Iterable[Router]
) -> None:
    superadmin_router, admin_router, teacher_router, student_router = routers
    
    dp.message.outer_middleware.register(DbSessionMiddleware(session_maker))
    dp.callback_query.outer_middleware.register(DbSessionMiddleware(session_maker))
    
    dp.message.outer_middleware.register(RepoMiddleware())
    dp.callback_query.outer_middleware.register(RepoMiddleware())
    
    superadmin_router.message.middleware.register(SuperAdminRepoMiddleware())
    superadmin_router.callback_query.middleware.register(SuperAdminRepoMiddleware())
    
    admin_router.callback_query.middleware.register(AdminRepoMiddleware())
    admin_router.message.middleware.register(AdminRepoMiddleware())
    
    student_router.callback_query.middleware.register(StudentRepoMiddleware())
    student_router.message.middleware.register(StudentRepoMiddleware())
