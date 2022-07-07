from aiogram import Router
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()


@router.message(state="*")
async def on_msg(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="Профиль")

    await message.answer(
        "Добро пожаловать", reply_markup=builder.as_markup(resize_keyboard=True)
    )
