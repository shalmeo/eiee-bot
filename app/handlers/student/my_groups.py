from aiogram import Router
from aiogram.types import CallbackQuery, User
from app.keyboards.student.inline.my_groups import GroupCallbackDataFactory, get_my_groups_kb

from app.services.database.models import Student
from app.services.database.repositories.default import DefaultRepo


router = Router()


@router.callback_query(text='my_groups')
async def on_my_groups(
    call: CallbackQuery,
    event_from_user: User,
    repo: DefaultRepo
):
    student = await repo.get(Student, event_from_user.id)
    markup = get_my_groups_kb(student.groups)
    await call.message.edit_text('Ваши группы', reply_markup=markup)
    await call.answer()
    

@router.callback_query(GroupCallbackDataFactory.filter())
async def on_group_info(
    call: CallbackQuery,
    event_from_user: User
):
    pass