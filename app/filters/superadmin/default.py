from aiogram.types import User, Message, CallbackQuery
from aiogram.dispatcher.filters import BaseFilter

from app.config_reader import Settings


class DefaultSuperAdminFilter(BaseFilter):
    async def __call__(
        self,
        event: Message | CallbackQuery,
        event_from_user: User,
        config: Settings
    ) -> bool:
        return event_from_user.id == config.bot_admin