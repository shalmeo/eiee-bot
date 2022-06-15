from contextlib import suppress

from aiogram import F, Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.exc import DBAPIError

from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.keyboards.superadmin.inline.registryof_groups import (
    GroupPageController,
    get_registryof_groups_kb,
)
from app.services.database.models import Group
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.registry == Registry.GROUPS), state="*"
)
async def on_registryof_groups(
    call: CallbackQuery,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
):
    offset = (await state.get_data()).get("offset") or 0

    groups, offset, limit = await superadmin_repo.get_groups(offset)
    count = await repo.get_count(Group)
    markup = get_registryof_groups_kb(
        groups,
        count,
        offset,
        limit,
    )
    await call.message.edit_text("Реестр групп", reply_markup=markup)
    await call.answer()

    await state.set_state(None)
    await state.update_data(offset=offset)


@router.callback_query(GroupPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: GroupPageController,
    state: FSMContext,
    superadmin_repo: SuperAdminRepo,
    repo: DefaultRepo,
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
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()
