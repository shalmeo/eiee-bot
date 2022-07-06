from aiogram import Router, types, F

from app.services.database.repositories.default import DefaultRepo

router = Router()


@router.message(F.contact)
async def on_input_phone(message: types.Message, repo: DefaultRepo):
    tel = message.contact.phone_number[2:]
    user = await repo.get_student_by_tel(tel)
    if not user:
        user = await repo.get_teacher_by_tel(tel)

        if not user:
            await message.answer("Не удалось найти вас, попробуйте зарегистрироваться")

            return

    user.telegram_id = message.from_user.id
    user.user_name = message.from_user.username

    await repo.session.commit()
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Профиль")]], resize_keyboard=True
    )
    await message.answer(
        "Отлично, вы можете продолжить пользоваться ботом", reply_markup=markup
    )
