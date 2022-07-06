from contextlib import suppress

import dataclass_factory

from aiogram import Bot, F, Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, User
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_reader import Settings
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.misc.delete_message import delete_last_message
from app.misc.models import TeacherModel
from app.misc.text import get_teacher_info_text
from app.services.database.models import Teacher
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo
from app.services.excel.read_registryof_teachers import parse_registryof_teachers_excel
from app.keyboards.superadmin.inline.registryof_teachers import (
    CreateRecordofTeacher,
    TeacherCallbackFactory,
    TeacherPageController,
    WayCreateTeacher,
    get_load_from_excel_kb,
    get_read_excel_kb,
    get_registryof_teachers_kb,
    get_teacher_info_kb,
    TeacherAction,
)

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.registry == Registry.TEACHERS), state="*"
)
async def on_registryof_teachers(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    offset = (await state.get_data()).get("offset") or 0

    teachers, offset, limit = await superadmin_repo.get_registry(Teacher, offset)
    count = await repo.get_count(Teacher)
    markup = get_registryof_teachers_kb(
        teachers,
        config,
        call.message.message_id,
        count,
        offset,
        limit,
    )
    await call.message.edit_text("Реестр учителей", reply_markup=markup)
    await call.answer()

    await state.set_state(None)
    await state.update_data(offset=offset)


@router.callback_query(TeacherCallbackFactory.filter(F.action == TeacherAction.INFO))
async def on_teacher_info(
    call: CallbackQuery,
    callback_data: TeacherCallbackFactory,
    event_from_user: User,
    repo: DefaultRepo,
    config: Settings,
):
    teacher = await repo.get(Teacher, callback_data.teacher_id)
    with_creator = teacher.admin.telegram_id != event_from_user.id
    text = get_teacher_info_text(teacher, with_creator=with_creator)
    markup = get_teacher_info_kb(
        config, call.message.message_id, callback_data.teacher_id
    )
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(
    CreateRecordofTeacher.filter(F.way == WayCreateTeacher.FROM_EXCEL)
)
async def on_load_from_excel(call: CallbackQuery, state: FSMContext):
    markup = get_load_from_excel_kb()
    m = await call.message.edit_text(
        "Пришли сюда файл <code>*.excel</code>", reply_markup=markup
    )

    await state.set_state("input_teacher_excel_file")
    await state.update_data(mid=m.message_id)


@router.message(
    F.document.file_name.casefold().endswith(".xlsx"), state="input_teacher_excel_file"
)
async def read_excel_file(message: Message, bot: Bot, state: FSMContext):
    mid = (await state.get_data()).get("mid")
    await delete_last_message(bot, message.from_user.id, mid)

    downloaded = await bot.download(message.document.file_id)
    count, teachers = parse_registryof_teachers_excel(downloaded, message.from_user.id)
    markup = get_read_excel_kb()
    await message.answer(
        f"Обнаружено записей: <code>{count}</code>\n\n"
        "Если нет некоторых записей, пересмотрите файл, заполните недостающие ячейки "
        "и пришлите обратно отредактированный файл",
        reply_markup=markup,
    )

    await state.update_data(teachers=teachers)


@router.callback_query(text="load_teachers", state="input_teacher_excel_file")
async def on_load_teachers(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    session: AsyncSession,
):
    factory = dataclass_factory.Factory()
    teachers = (await state.get_data()).get("teachers")
    count = 0
    for t in teachers:
        teacher = factory.load(t, TeacherModel)
        get_teacher = await repo.get(Teacher, teacher.tg_id)
        if get_teacher:
            continue

        superadmin_repo.add_new_teacher(teacher)
        count += 1

    await session.commit()

    await call.message.delete()
    await call.message.answer(
        "Список учителей успешно добавлен\n\n"
        f"Всего добавлено записей: <code>{count}</code>\n\n"
        "Если число обнаруженных записей отличается от всего добавленных записей, "
        "проверьте что в файле нет записей которые есть в базе"
    )


@router.callback_query(TeacherPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: TeacherPageController,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    try:
        teachers, offset, limit = await superadmin_repo.get_registry(
            Teacher, offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return

    count = await repo.get_count(Teacher)

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
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()
