from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.keyboards.superadmin.inline.registryof_groups import get_create_group_kb
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.parse import parse_group_info_data
from app.misc.text import get_group_info_text
from app.services.database.models import Group
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo


# GET /group/create-form
async def create_group_form(request: Request):
    return FileResponse("html/create_group.html")


# POST /group/create
async def new_group(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    bot: Bot = request.app["bot"]
    session_factory: sessionmaker = request.app["session_factory"]

    try:
        init_data = safe_parse_webapp_init_data(
            config.bot_token, init_data=data["_auth"]
        )
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    try:
        group = parse_group_info_data(data)
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        repo = SuperAdminRepo(session, init_data.user.id)
        group = await repo.add_new_group(group)
        await session.commit()

    async with session_factory() as session:
        repo = DefaultRepo(session)
        group = await repo.get(Group, group.uuid)

    await _send_info(bot, init_data.user.id, group, data["msgId"], config)

    return json_response({"ok": True})


async def _send_info(
    bot: Bot, user_id: int, group: Group, msg_id: int | str, config: Settings
) -> None:
    text = get_group_info_text(group)
    markup = get_create_group_kb(group, config, msg_id)
    await delete_last_message(bot, user_id, msg_id)
    await bot.send_message(user_id, text, reply_markup=markup)
