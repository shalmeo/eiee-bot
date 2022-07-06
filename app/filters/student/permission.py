import datetime
from typing import Sequence

from aiogram import types
from aiogram.dispatcher.filters import BaseFilter

from app.keyboards.student.inline.current_tasks import HomeTaskCallbackFactory
from app.services.database import HomeWork
from app.services.database.repositories.default import DefaultRepo


class PermissionToAttachFilter(BaseFilter):
    async def __call__(
        self,
        call: types.CallbackQuery,
        callback_data: HomeTaskCallbackFactory,
        event_from_user: types.User,
        repo: DefaultRepo,
    ) -> bool:
        student = await repo.get_student(event_from_user.id)

        home_works: Sequence[HomeWork] = tuple(
            filter(
                lambda home_work: home_work.home_task_id
                == callback_data.home_task_uuid,
                student.home_works,
            )
        )
        if len(home_works) == 3:
            await call.answer(
                "Недоступно!\n\n" "У вас уже есть 3 загруженных Д/З", show_alert=True
            )
            return False

        for hw in home_works:
            if hw.state == "accepted":
                await call.answer(
                    "Недоступно!\n\n" "Ваша работа была одобрена", show_alert=True
                )
                return False

            if hw.state == "in_check":
                await call.answer(
                    "Недоступно!\n\n" "Ваша работа в проверке", show_alert=True
                )
                return False

        home_task = await repo.get_home_task(callback_data.home_task_uuid)
        if datetime.datetime.utcnow() - home_task.deadline > datetime.timedelta(days=1):
            await call.answer(
                "Недоступно!\n\n"
                "С момента крайней даты сдачи Д/З прошло более одного дня",
                show_alert=True,
            )
            return False

        return True
