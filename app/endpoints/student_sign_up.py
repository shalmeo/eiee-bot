from aiogram import Bot
from aiogram.dispatcher.fsm.storage.base import StorageKey
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.keyboards.superadmin.inline.unreg_users import get_unreg_user_kb
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.models import SignUpModel
from app.misc.parse import parse_user_sign_up_form
from app.misc.text import get_user_sign_up_text
from app.services.database.models import UnRegisteredUser


# GET /student/sign-up
async def student_sign_up_view(request: Request):
    return FileResponse("html/student_sign_up.html")


# POST /student/sign-up
async def student_sign_up(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    bot: Bot = request.app["bot"]
    session_factory: sessionmaker = request.app["session_factory"]
    storage: RedisStorage = request.app["storage"]

    try:
        init_data = safe_parse_webapp_init_data(
            config.bot_token, init_data=data["_auth"]
        )
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    try:
        student = parse_user_sign_up_form(data, init_data.user)
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        unregistered_student = UnRegisteredUser(
            telegram_id=init_data.user.id,
            first_name=student.first_name,
            last_name=student.last_name,
            patronymic=student.patronymic,
            email=student.email,
            user_name=student.user_name,
            tel=student.tel,
            timezone=student.timezone,
            role="student",
        )
        session.add(unregistered_student)
        await session.commit()

    key = StorageKey(bot.id, init_data.user.id, init_data.user.id)
    fsmdata = await storage.get_data(bot, key)

    await _send_info(bot, fsmdata["mid"], init_data.user.id)
    await _send_to_admin(bot, config, student)

    return json_response({"ok": True})


async def _send_info(bot: Bot, mid: int | str, chat_id: int):
    await delete_last_message(bot, chat_id, mid)
    await bot.send_sticker(
        chat_id,
        "CAACAgIAAxkBAAEQuAZixDH_PWwT-sPc5RQadANyE918OAACSAIAAladvQoc9XL43CkU0CkE",
    )
    await bot.send_message(
        chat_id,
        "Ваша заявка отправлена администратору на рассмотрение, дождитесь подтверждения",
    )


async def _send_to_admin(bot, config: Settings, student: SignUpModel):
    text = "Новый ученик\n\n" + "".join(get_user_sign_up_text(student))
    markup = get_unreg_user_kb(student.telegram_id)
    await bot.send_message(config.bot_admin, text, reply_markup=markup)
