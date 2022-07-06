from aiogram.types import User, Message, CallbackQuery
from aiogram.dispatcher.filters import BaseFilter

from app.services.database import UnRegisteredUser
from app.services.database.repositories.default import DefaultRepo


class DefaultGuestFilter(BaseFilter):
    async def __call__(
        self,
        event: Message | CallbackQuery,
        event_from_user: User,
        repo: DefaultRepo,
    ) -> bool:
        guest = await repo.get(UnRegisteredUser, event.from_user.id)
        if guest:
            if isinstance(event, CallbackQuery):
                event = event.message

            await event.answer(
                "Ваша заявка отправлена администратору на рассмотрение, дождитесь подтверждения"
            )
            return False

        return True
