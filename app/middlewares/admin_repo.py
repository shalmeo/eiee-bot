from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from app.services.database.repositories.admin import AdminRepo


class AdminRepoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        session = data["session"]
        data["admin_repo"] = AdminRepo(session)
        return await handler(event, data)
