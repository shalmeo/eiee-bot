from aiogram import Router, types

router = Router()


@router.message(commands="start")
async def on_cmd_start(message: types.Message):
    text = "Добро пожаловать, вы уже зарегестрированы в нашей школе?"
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Да, проверить номер", request_contact=True),
            ],
            [types.KeyboardButton(text="Зарегистрироваться")],
        ],
        resize_keyboard=True,
    )

    await message.answer(text, reply_markup=markup)
