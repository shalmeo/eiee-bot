from contextlib import suppress
from operator import and_

import dataclass_factory
from aiogram import F, Router, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, BufferedInputFile, Message
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_reader import Settings
from app.keyboards.superadmin.excel import ExcelCallbackFactory, ExcelAction
from app.keyboards.superadmin.registry import Registry
from app.misc.delete_message import delete_last_message
from app.misc.media import get_media_groups
from app.misc.models import GroupModel
from app.misc.text import (
    get_group_info_text,
    get_home_task_text,
    get_home_work_text,
)
from app.services.database.models import Group
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory
from app.keyboards.superadmin.inline.registryof_groups import (
    GroupPageController,
    get_registryof_groups_kb,
    GroupCallbackFactory,
    get_create_group_kb,
    GroupAction,
    get_select_home_tasks_kb,
    HomeTaskPageController,
    HomeTaskCallbackFactory,
    HomeTaskAction,
    get_home_task_info_kb,
    StudentCallbackFactory,
    get_home_works_kb,
    HomeWorkCallbackFactory,
    get_hw_info_kb,
    HomeWorkAction,
    get_import_groups_kb,
    get_read_excel_kb,
)
from app.services.excel.export_data.export_groups import get_excel_groups
from app.services.excel.import_data.import_groups import import_groups_excel

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.registry == Registry.GROUPS), state="*"
)
async def on_registryof_groups(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    offset = (await state.get_data()).get("offset") or 0

    groups, offset, limit = await superadmin_repo.get_groups(offset)
    count = await repo.get_count(Group)
    markup = get_registryof_groups_kb(
        groups, count, offset, limit, call.message.message_id, config
    )
    await call.message.edit_text("Реестр групп", reply_markup=markup)
    await call.answer()

    await state.set_state(None)
    await state.update_data(offset=offset)


@router.callback_query(GroupCallbackFactory.filter(F.action == GroupAction.INFO))
async def on_group_info(
    call: CallbackQuery,
    callback_data: GroupCallbackFactory,
    repo: DefaultRepo,
    config: Settings,
):
    group = await repo.get(Group, callback_data.group_uuid)
    text = get_group_info_text(group)
    markup = get_create_group_kb(group, config, call.message.message_id)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(
    GroupCallbackFactory.filter(F.action == GroupAction.ALL_HOME_TASK)
)
async def on_all_home_tasks(
    call: CallbackQuery,
    callback_data: GroupCallbackFactory,
    superadmin_repo: SuperAdminRepo,
):
    home_tasks, limit = await superadmin_repo.get_home_tasks(
        callback_data.group_uuid, 0
    )
    count = await superadmin_repo.get_count_home_tasks(callback_data.group_uuid)
    group = await superadmin_repo.get_group(callback_data.group_uuid)
    markup = get_select_home_tasks_kb(
        home_tasks, 0, limit, count, callback_data.group_uuid
    )
    text = get_group_info_text(group)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(HomeTaskCallbackFactory.filter(F.action == HomeTaskAction.INFO))
async def on_ht_info(
    call: CallbackQuery, callback_data: HomeTaskCallbackFactory, repo: DefaultRepo
):
    home_task = await repo.get_home_task(callback_data.task_uuid)
    text = (
        get_home_task_text(home_task, home_task.group.admin.timezone)
        + "\n\nВыберите ученика"
    )
    markup = get_home_task_info_kb(
        home_task.group.students, home_task.uuid, home_task.group_id
    )
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(
    HomeTaskCallbackFactory.filter(F.action == HomeTaskAction.ATTACHED_FILES)
)
async def on_attached_ht_files(
    call: CallbackQuery,
    callback_data: HomeTaskCallbackFactory,
    bot: Bot,
    repo: DefaultRepo,
):
    files = await repo.get_home_task_files(callback_data.task_uuid)
    photo_media_group, document_media_group, voices = get_media_groups(files)

    for media_group in (photo_media_group, document_media_group):
        if media_group:
            await bot.send_media_group(call.from_user.id, media_group)

    if voices:
        for v in voices:
            await call.message.answer_voice(v)

    await call.answer()


@router.callback_query(StudentCallbackFactory.filter())
async def on_student_hw(
    call: CallbackQuery,
    callback_data: StudentCallbackFactory,
    repo: DefaultRepo,
    superadmin_repo: SuperAdminRepo,
):
    student = await repo.get_student_by_id(callback_data.student_id)
    home_works = await superadmin_repo.get_student_home_works(
        callback_data.student_id, callback_data.task_uuid
    )
    markup = get_home_works_kb(home_works, callback_data.task_uuid)
    await call.message.edit_text(
        f"Ученик: {student.last_name} {student.first_name} \n\n" "Все итерации",
        reply_markup=markup,
    )
    await call.answer()


@router.callback_query(HomeWorkCallbackFactory.filter(F.action == HomeWorkAction.INFO))
async def on_wh_info(
    call: CallbackQuery,
    callback_data: HomeWorkCallbackFactory,
    repo: DefaultRepo,
):
    states = {
        "accepted": "Выполенено",
        "in_check": "В проверке",
        "rejected": "Отклонено",
    }

    hw = await repo.get_home_work(callback_data.work_uuid)
    text = (
        get_home_work_text(hw, hw.home_task.group.admin.timezone)
        + f"\nСтатус: {states[hw.state]}"
    )
    markup = get_hw_info_kb(hw.uuid, hw.student_id, hw.home_task_id)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(
    HomeWorkCallbackFactory.filter(F.action == HomeWorkAction.ATTACHED_FILES)
)
async def on_attached_files(
    call: CallbackQuery,
    callback_data: HomeWorkCallbackFactory,
    bot: Bot,
    repo: DefaultRepo,
):
    files = await repo.get_home_work_files(callback_data.work_uuid)
    photo_media_group, document_media_group, voices = get_media_groups(files)

    for media_group in (photo_media_group, document_media_group):
        if media_group:
            await bot.send_media_group(call.from_user.id, media_group)

    if voices:
        for v in voices:
            await call.message.answer_voice(v)

    await call.answer()


@router.callback_query(
    ExcelCallbackFactory.filter(
        and_(F.action == ExcelAction.EXPORT, F.registry == Registry.GROUPS)
    )
)
async def on_export_excel_groups(call: CallbackQuery, superadmin_repo: SuperAdminRepo):
    groups = await superadmin_repo.get_all_groups()
    output = get_excel_groups(groups)
    file = BufferedInputFile(file=output.read(), filename="Группы.xlsx")
    await call.message.answer_document(file)
    await call.answer()


@router.callback_query(
    ExcelCallbackFactory.filter(
        and_(F.action == ExcelAction.IMPORT, F.registry == Registry.GROUPS)
    )
)
async def on_import_groups(call: CallbackQuery, state: FSMContext):
    markup = get_import_groups_kb()
    m = await call.message.edit_text(
        "Пришли сюда файл <code>*.excel</code>", reply_markup=markup
    )

    await state.set_state("input_excel_groups")
    await state.update_data(mid=m.message_id)


@router.message(
    F.document.file_name.casefold().endswith(".xlsx"), state="input_excel_groups"
)
async def read_excel_file(message: Message, bot: Bot, state: FSMContext):
    mid = (await state.get_data()).get("mid")
    await delete_last_message(bot, message.from_user.id, mid)

    downloaded = await bot.download(message.document.file_id)
    count, groups = import_groups_excel(downloaded)
    markup = get_read_excel_kb()
    await message.answer(
        f"Обнаружено записей: <code>{count}</code>\n\n"
        "Если нехватает записей, пересмотрите файл, заполните недостающие ячейки "
        "и пришлите обратно отредактированный файл",
        reply_markup=markup,
    )

    await state.update_data(groups=groups)


@router.callback_query(text="load_groups", state="input_excel_groups")
async def on_load_teachers(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    session: AsyncSession,
):
    factory = dataclass_factory.Factory()
    groups = (await state.get_data()).get("groups")
    count = 0
    for g in groups:
        group, students = g
        group_model = factory.load(group, GroupModel)

        group = group_exists = await repo.get_group(group_model.uuid)
        if not group_exists:
            group = await superadmin_repo.add_new_group(group_model)

        for student in students:
            if not await repo.get_section(group.uuid, student):
                superadmin_repo.add_student_in_group(student, group.uuid)

        count += 1

    await session.commit()

    await call.message.delete()
    await call.message.answer(
        "Список групп успешно добавлен\n\n"
        f"Всего добавлено записей: <code>{count}</code>\n\n"
        "Если число обнаруженных записей отличается от всего добавленных записей, "
        "проверьте что в файле нет записей которые есть в базе"
    )


@router.callback_query(GroupPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: GroupPageController,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    try:
        groups, offset, limit = await superadmin_repo.get_groups(
            offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return

    count = await repo.get_count(Group)

    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    if 1 <= current_page <= pages:
        markup = get_registryof_groups_kb(
            groups,
            count,
            offset,
            limit,
            call.message.message_id,
            config,
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()


@router.callback_query(HomeTaskPageController.filter())
async def ht_page_controller(
    call: CallbackQuery,
    callback_data: HomeTaskPageController,
    superadmin_repo: SuperAdminRepo,
    state: FSMContext,
):
    try:
        home_tasks, limit = await superadmin_repo.get_home_tasks(
            callback_data.group_uuid, offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return

    pages = callback_data.count // limit + bool(callback_data.count % limit)
    current_page = callback_data.offset // limit + 1

    if 1 <= current_page <= pages:
        markup = get_select_home_tasks_kb(
            home_tasks,
            callback_data.offset,
            limit,
            callback_data.count,
            callback_data.group_uuid,
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()
