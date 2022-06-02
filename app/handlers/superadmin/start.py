from aiogram import Router
from aiogram.types import Message

from app.keyboards.superadmin.default.menu import get_menu_kb


router = Router()


@router.message(content_types=['photo'])
async def echo_photo_file_id(message: Message):
    await message.answer(f'<code>{message.photo[-1].file_id}</code>')
    
    
@router.message()
@router.message(commands='start', state='*')
async def cmd_start(message: Message):
    markup = get_menu_kb()
    await message.answer('Hello superadmin', reply_markup=markup)
