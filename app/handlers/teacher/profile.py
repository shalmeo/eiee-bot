from aiogram import Router
from aiogram.types import Message

from app.keyboards.teacher.inline.profile import get_profile_kb

router = Router()


@router.message(text="Профиль")
async def on_profile(message: Message):
    markup = get_profile_kb()
    await message.answer("Профиль учителя", reply_markup=markup)
