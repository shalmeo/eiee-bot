import datetime

from aiogram import Router, F, types, Bot
from aiogram.dispatcher.fsm.context import FSMContext

from app.misc.delete_message import delete_last_message
from app.misc.parse import get_student_model, get_teacher_model
from app.services.database.models import UnRegisteredUser
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo
from app.keyboards.superadmin.inline.unreg_users import (
    UnRegisteredUserCallbackFactory,
    UnRegUserAction,
)

router = Router()


@router.callback_query(
    UnRegisteredUserCallbackFactory.filter(F.action == UnRegUserAction.APPROVE)
)
async def on_approve_user(
    call: types.CallbackQuery,
    callback_data: UnRegisteredUserCallbackFactory,
    state: FSMContext,
):
    await call.message.edit_text(
        "Введите уникальный идентификатор и даты действия записи в формате:\n\n"
        "<code>id, dd.mm.yyyy, dd.mm.yyyy</code>\n\n"
        "Пример:\n"
        "<code>501404, 13.10.2022, 13.10.2024</code>"
    )
    await state.update_data(telegram_id=callback_data.telegram_id)
    await state.set_state("input_id")


@router.message(state="input_id")
async def on_input_id(
    message: types.Message,
    state: FSMContext,
    bot: Bot,
    repo: DefaultRepo,
    superadmin_repo: SuperAdminRepo,
):
    try:
        user_id, access_start, access_end = _parse_text(message.text)
    except ValueError:
        await message.answer(
            "Проверьте правильность ввода полей\n\n"
            "Пример:\n"
            "<code>501404, 13.10.2022, 13.10.2024</code>"
        )
        return

    data = await state.get_data()
    unreg_user = await repo.get(UnRegisteredUser, data["telegram_id"])
    if unreg_user.role == "teacher":
        model = get_teacher_model(
            unreg_user, user_id, message.from_user.id, access_start, access_end
        )
        superadmin_repo.add_new_teacher(model)
    else:
        model = get_student_model(
            unreg_user, user_id, message.from_user.id, access_start, access_end
        )
        superadmin_repo.add_new_student(model)
    await superadmin_repo.delete_unreg_user(unreg_user.telegram_id)
    await superadmin_repo.session.commit()
    await message.answer("Запись успешно добавлена")

    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Профиль")]], resize_keyboard=True
    )
    await bot.send_message(
        unreg_user.telegram_id, "Ваша заявка была одобрена", reply_markup=markup
    )
    await state.clear()


@router.callback_query(
    UnRegisteredUserCallbackFactory.filter(F.action == UnRegUserAction.REJECT)
)
async def on_reject_user(
    call: types.CallbackQuery,
    callback_data: UnRegisteredUserCallbackFactory,
    bot: Bot,
    superadmin_repo: SuperAdminRepo,
):
    await superadmin_repo.delete_unreg_user(callback_data.telegram_id)
    await superadmin_repo.session.commit()

    await delete_last_message(bot, call.from_user.id, call.message.message_id)
    await call.message.answer("Заявка успешно отклонена")

    await bot.send_message(callback_data.telegram_id, "Ваша заявка была отклонена")


def _parse_text(text: str) -> tuple[int, datetime.date, datetime.date]:
    user_id_str, access_start_str, access_end_str = map(str.strip, text.split(","))

    access_start = datetime.datetime.strptime(access_start_str, r"%d.%m.%Y")
    access_end = datetime.datetime.strptime(access_end_str, r"%d.%m.%Y")

    return int(user_id_str), access_start.date(), access_end.date()
