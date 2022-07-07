from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from app.services.database.repositories.admin import AdminRepo
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.student import StudentRepo
from app.services.database.repositories.superadmin import SuperAdminRepo
from app.services.database.repositories.teacher import TeacherRepo


class RepoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        session = data["session"]
        data["repo"] = DefaultRepo(session)
        return await handler(event, data)


class SuperAdminRepoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        session = data["session"]
        data["superadmin_repo"] = SuperAdminRepo(session, event.from_user.id)
        return await handler(event, data)


class AdminRepoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        session = data["session"]
        data["admin_repo"] = AdminRepo(session, event.from_user.id)
        return await handler(event, data)


class StudentRepoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        session = data["session"]
        data["student_repo"] = StudentRepo(session, event.from_user.id)
        return await handler(event, data)


class TeacherRepoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        session = data["session"]
        data["teacher_repo"] = TeacherRepo(session, event.from_user.id)
        return await handler(event, data)
