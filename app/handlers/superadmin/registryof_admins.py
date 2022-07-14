from contextlib import suppress
from operator import and_

import dataclass_factory
from aiogram import Bot, F, Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_reader import Settings
from app.keyboards.superadmin.excel import ExcelCallbackFactory, ExcelAction
from app.keyboards.superadmin.registry import Registry
from app.misc.delete_message import delete_last_message
from app.misc.models import AdminModel
from app.misc.text import get_admin_info_text
from app.services.database.models import Administrator
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo
from app.services.excel.export_data.export_admins import get_excel_admins
from app.services.excel.import_data.import_admins import import_admins_excel
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory
from app.keyboards.superadmin.inline.registryof_admins import (
    AdminCallbackFactory,
    AdminPageController,
    get_admin_info_kb,
    get_load_from_excel_kb,
    get_read_excel_kb,
    get_registryof_admins_kb,
    AdminAction,
)

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
    offset = (await state.get_data()).get("offset", 0)

    admins, limit = await superadmin_repo.get_admins(offset)
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


@router.callback_query(AdminCallbackFactory.filter(F.action == AdminAction.INFO))
async def on_admin_info(
    call: CallbackQuery,
    callback_data: AdminCallbackFactory,
    repo: DefaultRepo,
    config: Settings,
):
    admin = await repo.get(Administrator, callback_data.admin_id)
    text = get_admin_info_text(admin)
    markup = get_admin_info_kb(config, call.message.message_id, callback_data.admin_id)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(AdminCallbackFactory.filter(F.action == AdminAction.DELETE))
async def on_delete_admin(
    call: CallbackQuery,
    callback_data: AdminCallbackFactory,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
):
    admin = await repo.get_admin_by_id(callback_data.admin_id)
    superadmin_repo.add_unreg_user(admin)
    await superadmin_repo.delete_admin(admin)
    await superadmin_repo.session.commit()
    await call.message.delete()
    await call.message.answer("Администратор успешно удален")


@router.callback_query(
    ExcelCallbackFactory.filter(
        and_(F.action == ExcelAction.IMPORT, F.registry == Registry.ADMINISTRATORS)
    )
)
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
    count, admins = import_admins_excel(downloaded)
    markup = get_read_excel_kb()
    await message.answer(
        f"Обнаружено записей: <code>{count}</code>\n\n"
        "Если нехватает записей, пересмотрите файл, заполните недостающие ячейки "
        "и пришлите обратно отредактированный файл",
        reply_markup=markup,
    )

    await state.update_data(admins=admins)


@router.callback_query(text="load_admins", state="input_admin_excel_file")
async def on_load_admins(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
    session: AsyncSession,
):
    factory = dataclass_factory.Factory()
    admins = (await state.get_data()).get("admins")
    count = 0
    for a in admins:
        admin = factory.load(a, AdminModel)
        admin_exists = await repo.get_admin_by_id(admin.id)
        if admin_exists:
            continue

        superadmin_repo.add_new_admin(admin)
        count += 1

    await session.commit()

    await call.message.delete()
    await call.message.answer(
        "Список администраторов успешно добавлен\n\n"
        f"Всего добавлено записей: <code>{count}</code>\n\n"
        "Если число обнаруженных записей отличается от всего добавленных записей, "
        "проверьте что в файле нет записей которые есть в базе"
    )


@router.callback_query(
    ExcelCallbackFactory.filter(
        and_(F.action == ExcelAction.EXPORT, F.registry == Registry.ADMINISTRATORS)
    )
)
async def on_export_excel_admins(call: CallbackQuery, superadmin_repo: SuperAdminRepo):
    admins = await superadmin_repo.get_all_admins()
    output = get_excel_admins(admins)
    file = BufferedInputFile(file=output.read(), filename="Администраторы.xlsx")
    await call.message.answer_document(file)
    await call.answer()


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
