import dataclass_factory

from contextlib import suppress

from aiogram import Bot, F, Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_reader import Settings
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.keyboards.superadmin.inline.registryof_admins import (
    AdminCallbackFactory,
    AdminPageController,
    CreateRecordofAdmin,
    WayCreateAdmin,
    get_admin_info_kb,
    get_load_from_excel_kb,
    get_read_excel_kb,
    get_registryof_admins_kb,
)
from app.misc.delete_message import delete_last_message
from app.misc.models import AdminModel
from app.misc.text import get_admin_info_text
from app.services.database.models import Administrator
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo
from app.services.excel.read_registryof_admins import parse_registryof_admins_excel

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.registry == Registry.ADMINISTRATORS), state="*"
)
async def on_registryof_admins(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    offset = (await state.get_data()).get("offset") or 0

    admins, offset, limit = await superadmin_repo.get_registry(Administrator, offset)
    count = await repo.get_count(Administrator)
    markup = get_registryof_admins_kb(
        admins,
        config,
        call.message.message_id,
        count,
        offset,
        limit,
    )
    await call.message.edit_text("Реестр администраторов", reply_markup=markup)
    await call.answer()

    await state.set_state(None)
    await state.update_data(offset=offset)


@router.callback_query(AdminCallbackFactory.filter())
async def on_admin_info(
    call: CallbackQuery,
    superadmin_repo: SuperAdminRepo,
    callback_data: AdminCallbackFactory,
):
    admin = await superadmin_repo.get(Administrator, callback_data.admin_id)
    text = get_admin_info_text(admin)
    markup = get_admin_info_kb()
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(CreateRecordofAdmin.filter(F.way == WayCreateAdmin.FROM_EXCEL))
async def on_load_from_excel(call: CallbackQuery, state: FSMContext):
    markup = get_load_from_excel_kb()
    m = await call.message.edit_text(
        "Пришли сюда файл <code>*.excel</code>", reply_markup=markup
    )

    await state.set_state("input_admin_excel_file")
    await state.update_data(mid=m.message_id)


@router.message(
    F.document.file_name.casefold().endswith(".xlsx"), state="input_admin_excel_file"
)
async def read_excel_file(message: Message, bot: Bot, state: FSMContext):
    mid = (await state.get_data()).get("mid")
    await delete_last_message(bot, message.from_user.id, mid)

    downloaded = await bot.download(message.document.file_id)
    count, admins = parse_registryof_admins_excel(downloaded)
    markup = get_read_excel_kb()
    await message.answer(
        f"Обнаружено записей: <code>{count}</code>\n\n"
        "Если нет некоторых записей, пересмотрите файл, заполните недостающие ячейки "
        "и пришлите обратно отредактированный файл",
        reply_markup=markup,
    )

    await state.update_data(admins=admins)


@router.callback_query(text="load_admins", state="input_admin_excel_file")
async def on_load_admins(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    session: AsyncSession,
):
    factory = dataclass_factory.Factory()
    admins = (await state.get_data()).get("admins")
    count = 0
    for a in admins:
        admin = factory.load(a, AdminModel)
        admin_exists = await superadmin_repo.get(Administrator, admin.tg_id)
        if admin_exists:
            continue

        superadmin_repo.add_new_admin()
        count += 1

    await session.commit()

    await call.message.delete()
    await call.message.answer(
        "Список администраторов успешно добавлен\n\n"
        f"Всего добавлено записей: <code>{count}</code>\n\n"
        "Если число обнаруженных записей отличается от всего добавленных записей, "
        "проверьте что в файле нет записей которые есть в базе"
    )


@router.callback_query(AdminPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: AdminPageController,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    try:
        admins, offset, limit = await superadmin_repo.get_registry(
            Administrator, offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return

    count = await repo.get_count(Administrator)

    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    if 1 <= current_page <= pages:
        markup = get_registryof_admins_kb(
            admins,
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