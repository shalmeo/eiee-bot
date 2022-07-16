from aiogram import Router, types, F

from app.keyboards.student.inline.current_tasks import GroupCallbackFactory, GroupAction
from app.keyboards.student.inline.overdue_tasks import get_overdue_tasks_kb
from app.services.database.repositories.student import StudentRepo

router = Router()


@router.callback_query(
    GroupCallbackFactory.filter(F.action == GroupAction.OVERDUE_HOMETASK)
)
async def on_overdue_tasks(
    call: types.CallbackQuery,
    callback_data: GroupCallbackFactory,
    student_repo: StudentRepo,
):
    tasks = await student_repo.get_overdue_tasks(callback_data.group_uuid)
    markup = get_overdue_tasks_kb(tasks, callback_data.group_uuid)
    await call.message.edit_text(
        "Просроченное домашнeе задание (последние 3)", reply_markup=markup
    )
    await call.answer()
