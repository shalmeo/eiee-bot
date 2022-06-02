from aiogram.types import User, Message, CallbackQuery
from aiogram.dispatcher.filters import BaseFilter

from app.services.database.repositories.default import DefaultRepo


class DefaultStudentFilter(BaseFilter):
    async def __call__(
        self,
        event: Message | CallbackQuery,
        event_from_user: User,
        repo: DefaultRepo,
    ) -> bool:
        return await repo.user_is_student(event_from_user.id)