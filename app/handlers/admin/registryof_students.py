from contextlib import suppress

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import DBAPIError

from app.config_reader import Settings
from app.misc.text import get_student_info_text, get_parent_info_text
from app.services.database.models import Student
from app.services.database.repositories.admin import AdminRepo
from app.services.database.repositories.default import DefaultRepo
from app.keyboards.admin.inline.profile import ProfileCallbackFactory, Registry
from app.keyboards.admin.inline.registryof_students import (
    StudentCallbackFactory,
    StudentPageController,
    get_registryof_students_kb,
    get_student_info_kb,
)
from app.keyboards.superadmin.inline.registryof_students import (
    ParentCallbackFactory,
    get_parents_info_kb,
)

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.registry == Registry.STUDENTS), state="*"
)
async def on_registryof_students(
    call: CallbackQuery,
    state: FSMContext,
    event_from_user: User,
    admin_repo: AdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    offset = (await state.get_data()).get("offset") or 0

    students, offset, limit = await admin_repo.get_registry(Student, offset)
    admin = await repo.get_admin(event_from_user.id)
    count = await repo.get_count(Student, Student.admin_id == admin.id)
    markup = get_registryof_students_kb(
        students, config, call.message.message_id, count, offset, limit, admin.id
    )
    await call.message.edit_text("Реестр учеников", reply_markup=markup)
    await call.answer()

    await state.set_state(None)
    await state.update_data(offset=offset, admin_id=admin.id)


@router.callback_query(StudentCallbackFactory.filter())
async def on_student_info(
    call: CallbackQuery,
    repo: DefaultRepo,
    callback_data: StudentCallbackFactory,
    config: Settings,
):
    student = await repo.get(Student, callback_data.student_id)
    text = get_student_info_text(student)
    markup = get_student_info_kb()
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(ParentCallbackFactory.filter())
async def on_parents_info(
    call: CallbackQuery,
    callback_data: ParentCallbackFactory,
    admin_repo: AdminRepo,
    config: Settings,
):
    parents = await admin_repo.get_parents_by_id(callback_data.student_id)

    text = "Родители\n\n" + "\n\n".join([get_parent_info_text(p) for p in parents])
    markup = get_parents_info_kb(
        callback_data.student_id, config, call.message.message_id
    )

    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(StudentPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: StudentPageController,
    state: FSMContext,
    admin_repo: AdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    try:
        students, offset, limit = await admin_repo.get_registry(
            Student, offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return
    data = await state.get_data()
    count = await repo.get_count(Student, Student.admin_id == data["admin_id"])

    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    if 1 <= current_page <= pages:
        markup = get_registryof_students_kb(
            students,
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
