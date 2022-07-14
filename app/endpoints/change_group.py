from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.services.database.models import Group
from app.services.database.repositories.default import DefaultRepo
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.models import GroupModel
from app.misc.parse import (
    parse_group_info_data,
)


# GET /group/change-info
async def change_group_info_view(_: Request):
    return FileResponse("html/change_group.html")


# POST /group
async def get_group(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]

    try:
        safe_parse_webapp_init_data(config.bot_token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        group = await repo.get_group(data["id"])

    if not group:
        return json_response({"ok": False, "error": "Not Found"}, status=404)

    if group.teacher_id:
        teacher = [
            group.teacher_id,
            f"{group.teacher.last_name} {group.teacher.first_name} {group.teacher.patronymic}",
        ]
    else:
        teacher = None

    return json_response(
        {
            "ok": True,
            "group": {
                "title": group.title,
                "description": group.description,
                "teacher": teacher,
            },
        }
    )


# POST /group/change-info
async def change_group_info(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]
    bot: Bot = request.app["bot"]

    try:
        init_data = safe_parse_webapp_init_data(
            config.bot_token, init_data=data["_auth"]
        )
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    try:
        group_model = parse_group_info_data(data)
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        group = await repo.get_group(data["id"])

        _update_group(group, group_model)
        await session.commit()

    await _send_info(bot, init_data.user.id, data["msgId"])

    return json_response({"ok": True})


async def _send_info(bot: Bot, chat_id: int, mid: int | str) -> None:
    await delete_last_message(bot, chat_id, mid)
    await bot.send_message(chat_id, "Данные успешно изменены")


def _update_group(group: Group, group_model: GroupModel) -> None:
    group.title = group_model.title
    group.description = group_model.description
    group.teacher_id = group_model.teacher_id
