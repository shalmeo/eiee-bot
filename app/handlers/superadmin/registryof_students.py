from contextlib import suppress

import dataclass_factory

from aiogram import Bot, F, Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_reader import Settings
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.keyboards.superadmin.inline.registryof_students import (
    CreateRecordofStudent,
    StudentCallbackFactory,
    StudentPageController,
    WayCreateStudent,
    get_load_from_excel_kb,
    get_read_excel_kb,
    get_registryof_students_kb,
    get_student_info_kb,
    ParentCallbackFactory,
    get_parents_info_kb,
)
from app.misc.delete_message import delete_last_message
from app.misc.models import StudentModel
from app.misc.text import get_student_info_text, get_parent_info_text
from app.services.database.models import Parent, Student
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo
from app.services.excel.registryof_students import parse_registryof_students_excel

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.registry == Registry.STUDENTS), state="*"
)
async def on_registryof_students(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    offset = (await state.get_data()).get("offset") or 0

    students, offset, limit = await superadmin_repo.get_students(offset)
    count = await repo.get_count(Student)
    admin = await repo.get_admin(call.from_user.id)
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
    callback_data: StudentCallbackFactory,
    repo: DefaultRepo,
    config: Settings,
):
    student = await repo.get(Student, callback_data.student_id)
    text = get_student_info_text(student)
    markup = get_student_info_kb(
        config, call.message.message_id, callback_data.student_id
    )
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(
    CreateRecordofStudent.filter(F.way == WayCreateStudent.FROM_EXCEL)
)
async def on_load_from_excel(call: CallbackQuery, state: FSMContext):
    markup = get_load_from_excel_kb()
    m = await call.message.edit_text(
        "Пришли сюда файл <code>*.excel</code>", reply_markup=markup
    )

    await state.set_state("input_student_excel_file")
    await state.update_data(mid=m.message_id)


@router.message(
    F.document.file_name.casefold().endswith(".xlsx"), state="input_student_excel_file"
)
async def read_excel_file(message: Message, bot: Bot, state: FSMContext):
    mid = (await state.get_data()).get("mid")
    await delete_last_message(bot, message.from_user.id, mid)

    downloaded = await bot.download(message.document.file_id)
    count, students = parse_registryof_students_excel(downloaded, message.from_user.id)

    markup = get_read_excel_kb()
    await message.answer(
        f"Обнаружено записей: <code>{count}</code>\n\n"
        "Если нет некоторых записей, пересмотрите файл, заполните недостающие ячейки "
        "и пришлите обратно отредактированный файл",
        reply_markup=markup,
    )

    await state.update_data(students=students)


@router.callback_query(text="load_students", state="input_student_excel_file")
async def on_load_students(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    session: AsyncSession,
):
    factory = dataclass_factory.Factory()
    students = (await state.get_data()).get("students")
    count = 0
    for s in students:
        student = factory.load(s, StudentModel)
        student_exists = await repo.get(Student, student.tg_id)
        if student_exists:
            continue
        superadmin_repo.add_new_student(student)
        for p in student.parents:
            if not await repo.get(Parent, p.tg_id):
                superadmin_repo.add_new_parent(p)

            superadmin_repo.add_new_family(student.tg_id, p.tg_id)

        count += 1

    await session.commit()

    await call.message.delete()
    await call.message.answer(
        "Список учеников успешно добавлен\n\n"
        f"Всего добавлено записей: <code>{count}</code>\n\n"
        "Если число обнаруженных записей отличается от всего добавленных записей, "
        "проверьте что в файле нет записей которые есть в базе"
    )


@router.callback_query(ParentCallbackFactory.filter())
async def on_parents_info(
    call: CallbackQuery,
    callback_data: ParentCallbackFactory,
    superadmin_repo: SuperAdminRepo,
    config: Settings,
):
    parents = await superadmin_repo.get_parents_by_id(callback_data.student_id)

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
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    try:
        students, offset, limit = await superadmin_repo.get_students(
            offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return
    data = await state.get_data()
    count = await repo.get_count(Student)

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
