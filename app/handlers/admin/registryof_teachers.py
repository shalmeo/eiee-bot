from contextlib import suppress

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import DBAPIError

from app.config_reader import Settings
from app.misc.text import get_teacher_info_text
from app.services.database.models import Teacher
from app.services.database.repositories.admin import AdminRepo
from app.services.database.repositories.default import DefaultRepo
from app.keyboards.admin.inline.profile import ProfileCallbackFactory, Registry
from app.keyboards.admin.inline.registryof_teachers import (
    TeacherCallbackFactory,
    TeacherPageController,
    get_registryof_teachers_kb,
    get_teacher_info_kb,
)


router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.registry == Registry.TEACHERS), state="*"
)
async def on_registryof_teachers(
    call: CallbackQuery,
    event_from_user: User,
    state: FSMContext,
    admin_repo: AdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    offset = (await state.get_data()).get("offset") or 0

    teachers, offset, limit = await admin_repo.get_registry(Teacher, offset)
    admin = await repo.get_admin(event_from_user.id)
    count = await repo.get_count(Teacher, Teacher.admin_id == admin.id)
    markup = get_registryof_teachers_kb(
        teachers, config, call.message.message_id, count, offset, limit, admin.id
    )
    await call.message.edit_text("Реестр учителей", reply_markup=markup)
    await call.answer()


@router.callback_query(TeacherCallbackFactory.filter())
async def on_teacher_info(
    call: CallbackQuery,
    repo: DefaultRepo,
    callback_data: TeacherCallbackFactory,
):
    teacher = await repo.get(Teacher, callback_data.teacher_id)
    text = get_teacher_info_text(teacher)
    markup = get_teacher_info_kb()
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(TeacherPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: TeacherPageController,
    state: FSMContext,
    admin_repo: AdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    try:
        teachers, offset, limit = await admin_repo.get_registry(
            Teacher, offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return
    data = await state.get_data()
    count = await repo.get_count(Teacher, Teacher.admin_id == data["admin_id"])

    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    if 1 <= current_page <= pages:
        markup = get_registryof_teachers_kb(
            teachers,
            config,
            call.message.message_id,
            count,
            offset,
            limit,
            data["admin_id"],
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()
