from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.fsm.context import FSMContext

from app.keyboards.superadmin.inline.profile import get_profile_kb


router = Router()


@router.message(text='Профиль', state='*')
@router.callback_query(text='to_profile', state='*')
async def on_profile(event: Message | CallbackQuery, state: FSMContext):
    markup = get_profile_kb()
    text = 'Профиль супер-администратора'
    if isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.message.edit_text(text, reply_markup=markup)
        await event.answer()
        
    await state.clear()