from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext

from app.config_reader import Settings

router = Router()


@router.message(commands="start")
async def on_cmd_start(message: types.Message, config: Settings, state: FSMContext):
    text = "Добро пожаловать, вы уже зарегестрированы в нашей школе?"
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Да, проверить номер", request_contact=True),
            ],
            [
                types.KeyboardButton(
                    text="Зарегистрироваться",
                    web_app=types.WebAppInfo(
                        url=f"https://{config.webhook.host}/user/sign-up?user_id={message.from_user.id}"
                    ),
                )
            ],
        ],
        resize_keyboard=True,
    )

    m = await message.answer(text, reply_markup=markup)
    await state.update_data(
        user_id=message.from_user.id,
        username=message.from_user.username,
        mid=m.message_id,
    )
