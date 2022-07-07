from contextlib import suppress

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import DBAPIError

from app.config_reader import Settings
from app.keyboards.superadmin.inline.registryof_groups import get_create_group_kb
from app.misc.text import get_group_info_text
from app.services.database.models import Group
from app.services.database.repositories.admin import AdminRepo
from app.keyboards.admin.inline.profile import ProfileCallbackFactory, Registry
from app.keyboards.admin.inline.registryof_groups import (
    GroupPageController,
    get_registryof_groups_kb,
    GroupCallbackFactory,
)
from app.services.database.repositories.default import DefaultRepo


router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.registry == Registry.GROUPS), state="*"
)
async def on_registryof_groups(
    call: CallbackQuery,
    event_from_user: User,
    state: FSMContext,
    admin_repo: AdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    offset = (await state.get_data()).get("offset") or 0

    groups, offset, limit = await admin_repo.get_registry(Group, offset)
    admin = await repo.get_admin(event_from_user.id)
    count = await repo.get_count(Group, Group.admin_id == admin.id)
    markup = get_registryof_groups_kb(
        groups, count, offset, limit, config, call.message.message_id
    )
    await call.message.edit_text("Реестр групп", reply_markup=markup)
    await call.answer()

    await state.set_state(None)
    await state.update_data(offset=offset, admin_id=admin.id)


@router.callback_query(GroupCallbackFactory.filter())
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


@router.callback_query(GroupPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: GroupPageController,
    state: FSMContext,
    superadmin_repo: AdminRepo,
    repo: DefaultRepo,
    config: Settings,
):
    try:
        groups, offset, limit = await superadmin_repo.get_registry(
            Group, offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return
    data = await state.get_data()
    count = await repo.get_count(Group, Group.admin_id == data["admin_id"])

    pages = count // limit + bool(count % limit)
    current_page = offset // limit + 1

    if 1 <= current_page <= pages:
        markup = get_registryof_groups_kb(
            groups, count, offset, limit, config, call.message.message_id
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()
