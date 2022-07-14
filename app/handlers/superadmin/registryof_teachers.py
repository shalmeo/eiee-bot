from contextlib import suppress
from operator import and_

import dataclass_factory

from aiogram import Bot, F, Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, User, BufferedInputFile
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_reader import Settings
from app.keyboards.superadmin.excel import ExcelCallbackFactory, ExcelAction
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.misc.delete_message import delete_last_message
from app.misc.models import TeacherModel
from app.misc.text import get_teacher_info_text
from app.services.database.models import Teacher
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo
from app.services.excel.import_data.import_teachers import import_teachers_excel
from app.services.excel.export_data.export_teachers import get_excel_teachers
from app.keyboards.superadmin.inline.registryof_teachers import (
    TeacherCallbackFactory,
    TeacherPageController,
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
    admin = await repo.get_admin(call.from_user.id)
    markup = get_registryof_teachers_kb(
        teachers, config, call.message.message_id, count, offset, limit, admin.id
    )
    await call.message.edit_text("Реестр учителей", reply_markup=markup)
    await call.answer()

    await state.set_state(None)
    await state.update_data(offset=offset, admin_id=admin.id)


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
        config,
        call.message.message_id,
        callback_data.teacher_id,
    )
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(TeacherCallbackFactory.filter(F.action == TeacherAction.DELETE))
async def on_delete_teacher(
    call: CallbackQuery,
    callback_data: TeacherCallbackFactory,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
):
    teacher = await repo.get_teacher_by_id(callback_data.teacher_id)
    superadmin_repo.add_unreg_user(teacher)
    await superadmin_repo.delete_teacher(teacher)
    await superadmin_repo.session.commit()
    await call.message.delete()
    await call.message.answer("Учитель успешно удален")


@router.callback_query(
    ExcelCallbackFactory.filter(
        and_(F.action == ExcelAction.IMPORT, F.registry == Registry.TEACHERS)
    )
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
    count, teachers = import_teachers_excel(downloaded)
    markup = get_read_excel_kb()
    await message.answer(
        f"Обнаружено записей: <code>{count}</code>\n\n"
        "Если нехватает записей, пересмотрите файл, заполните недостающие ячейки "
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
        get_teacher = await repo.get_teacher_by_id(teacher.id)
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


@router.callback_query(
    ExcelCallbackFactory.filter(
        and_(F.action == ExcelAction.EXPORT, F.registry == Registry.TEACHERS)
    )
)
async def on_export_excel_teachers(
    call: CallbackQuery, superadmin_repo: SuperAdminRepo
):
    teachers = await superadmin_repo.get_all_teachers()
    output = get_excel_teachers(teachers)
    file = BufferedInputFile(file=output.read(), filename="Учителя.xlsx")
    await call.message.answer_document(file)
    await call.answer()


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
    data = await state.get_data()
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
            data["admin_id"],
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()
