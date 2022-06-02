from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.dispatcher.fsm.context import FSMContext
from sqlalchemy.exc import DBAPIError

from app.config_reader import Settings
from app.keyboards.superadmin.inline.profile import ProfileCallbackFactory, Registry
from app.keyboards.superadmin.inline.registryof_admins import PageController, get_registryof_admins_kb
from app.services.database.repositories.superadmin import SuperAdminRepo


router = Router()


@router.callback_query(ProfileCallbackFactory.filter(F.registry == Registry.ADMINISTRATORS))
async def on_registryof_admins(
    call: CallbackQuery,
    superadmin_repo: SuperAdminRepo,
    config: Settings,
    state: FSMContext
):
    admins, offset, limit = await superadmin_repo.get_registryof_admins(offset=1)
    count = await superadmin_repo.get_count_admins()
    markup = get_registryof_admins_kb(
        admins,
        config,
        call.message.message_id,
        count,
        offset,
        limit,
    )
    await call.message.edit_text('Реестр администраторов', reply_markup=markup)
    await call.answer()
    
    await state.update_data(offset=0)
 
    
@router.callback_query(PageController.filter())
async def page_controller(
    call: CallbackQuery,
    superadmin_repo: SuperAdminRepo,
    config: Settings,
    state: FSMContext,
    callback_data: PageController
):
    try:
        admins, offset, limit = await superadmin_repo.get_registryof_admins(offset=callback_data.offset)
    except DBAPIError:
        await call.answer()
        return
    
    count = await superadmin_repo.get_count_admins()
    
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
        await call.message.edit_reply_markup(markup)
    
    await call.answer()
    
    await state.update_data(offset=callback_data.offset)