from typing import Iterable

from aiogram import F, Router
from aiogram.types import CallbackQuery, User

from app.misc.text import get_group_info_text, get_students_list_text
from app.services.database.models import Student, Group
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.teacher import TeacherRepo
from app.keyboards.teacher.inline.profile import ProfileAction, ProfileCallbackFactory
from app.keyboards.teacher.inline.groups import (
    GroupAction,
    GroupCallbackFactory,
    get_group_info_kb,
    get_groups_kb,
)

router = Router()


@router.callback_query(ProfileCallbackFactory.filter(F.action == ProfileAction.GROUPS))
async def on_list_groups(call: CallbackQuery, event_from_user: User, repo: DefaultRepo):
    teacher = await repo.get_teacher(event_from_user.id)
    markup = get_groups_kb(teacher.groups, action=GroupAction.INFO)
    await call.message.edit_text(
        "Перечень групп\n\n"
        "Здесь находится перечень групп, в которых вы состоите\n"
        "Выберите группу, чтобы посмотреть список учеников",
        reply_markup=markup,
    )
    await call.answer()


@router.callback_query(GroupCallbackFactory.filter(F.action == GroupAction.INFO))
async def on_group_info(
    call: CallbackQuery,
    callback_data: GroupCallbackFactory,
    repo: DefaultRepo,
):
    group = await repo.get_group(callback_data.group_uuid)
    text = get_group_info_text(group) + "\n\n" + get_students_list_text(group.students)
    markup = get_group_info_kb()
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()
