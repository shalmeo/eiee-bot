from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext

from app.config_reader import Settings

router = Router()


@router.message(text="Зарегистрироваться")
async def on_register(message: types.Message, state: FSMContext, config: Settings):
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Ученик",
                    web_app=types.WebAppInfo(
                        url=f"https://{config.webhook.host}/student/sign-up"
                    ),
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="Учитель",
                    web_app=types.WebAppInfo(
                        url=f"https://{config.webhook.host}/teacher/sign-up"
                    ),
                ),
            ],
        ]
    )
    await message.answer_sticker(
        "CAACAgIAAxkBAAEQt91ixCseV5ZFiNtQJUJBvaBM1fJ7fwACAQEAAladvQoivp8OuMLmNCkE",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    m = await message.answer(
        "Вы регистрируетесь как:\n(ученик, учитель)", reply_markup=markup
    )
    await state.update_data(mid=m.message_id)
