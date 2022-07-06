from contextlib import suppress

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import DBAPIError

from app.config_reader import Settings
from app.misc.text import get_student_info_text
from app.services.database.models import Student
from app.services.database.repositories.admin import AdminRepo
from app.services.database.repositories.default import DefaultRepo
from app.keyboards.admin.inline.profile import ProfileCallbackFactory, Registry
from app.keyboards.admin.inline.registryof_students import (
    StudentCallbackFactory,
    StudentPageController,
    get_registryof_students_kb,
    get_student_info_kb
)


router = Router()


@router.callback_query(ProfileCallbackFactory.filter(F.registry == Registry.STUDENTS), state='*')
async def on_registryof_students(
    call: CallbackQuery,
    state: FSMContext,
    event_from_user: User,
    admin_repo: AdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    offset = (await state.get_data()).get('offset') or 0
    
    students, offset, limit = await admin_repo.get_registry(Student, event_from_user.id, offset)
    count = await repo.get_count(Student, Student.admin_id == event_from_user.id)
    markup = get_registryof_students_kb(
        students,
        config,
        call.message.message_id,
        count,
        offset,
        limit,
    )
    await call.message.edit_text('Реестр учеников', reply_markup=markup)
    await call.answer()
    
    await state.set_state(None)
    await state.update_data(offset=offset)


@router.callback_query(StudentCallbackFactory.filter())
async def on_student_info(
    call: CallbackQuery,
    repo: DefaultRepo,
    callback_data: StudentCallbackFactory,
):
    student = await repo.get(Student, callback_data.student_id)
    text = get_student_info_text(student)
    markup = get_student_info_kb()
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()
    

@router.callback_query(StudentPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: StudentPageController,
    event_from_user: User,
    state: FSMContext,
    admin_repo: AdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    try:
        students, offset, limit = await admin_repo.get_registry(
            Student,
            event_from_user.id,
            offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return
    
    count = await repo.get_count(Student, Student.admin_id == event_from_user.id)
    
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
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)
        
        await state.update_data(offset=callback_data.offset)
    
    await call.answer()