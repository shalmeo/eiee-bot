from aiogram import Bot
from aiogram.dispatcher.fsm.storage.base import StorageKey
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.keyboards.superadmin.inline.unreg_users import (
    get_unreg_user_kb,
)
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.models import SignUpModel
from app.misc.parse import parse_user_sign_up_form
from app.misc.text import get_user_sign_up_text
from app.services.database.models import UnRegisteredUser


# GET /user/sign-up
async def user_sign_up_view(_: Request):
    return FileResponse("html/user_sign_up.html")


# POST /user/sign-up
async def user_sign_up(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    bot: Bot = request.app["bot"]
    session_factory: sessionmaker = request.app["session_factory"]
    storage: RedisStorage = request.app["storage"]

    user_id = data.get("user_id")
    if user_id:
        user_id = int(user_id)
    else:
        return json_response(
            {"ok": False, "error": "Missing user id parameter"}, status=400
        )

    key = StorageKey(bot.id, user_id, user_id)
    fsm_data = await storage.get_data(bot, key)

    try:
        user = parse_user_sign_up_form(data, user_id, fsm_data["username"])
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        unregistered_user = UnRegisteredUser(
            telegram_id=user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            email=user.email,
            user_name=user.user_name,
            tel=user.tel,
            timezone=user.timezone,
        )
        session.add(unregistered_user)
        await session.commit()

    await _send_info(bot, fsm_data["mid"], user_id)
    await _send_to_admin(bot, config, user)

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


async def _send_to_admin(bot, config: Settings, user: SignUpModel):
    text = "Заявка на регистрацию\n\n" + get_user_sign_up_text(user)
    markup = get_unreg_user_kb(user.telegram_id)
    await bot.send_message(config.bot_admin, text, reply_markup=markup)
