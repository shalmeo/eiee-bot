from aiogram import Router
from aiogram.types import Message

from app.keyboards.admin.default.menu import get_menu_kb


router = Router()


@router.message(state="*")
async def on_msg(message: Message):
    markup = get_menu_kb()
    await message.answer("Добро пожаловать", reply_markup=markup)
