from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.models import AdminModel
from app.misc.parse import parse_admin_register_data
from app.services.database.models import Administrator
from app.services.database.repositories.default import DefaultRepo


# GET /administrator/change-info
async def change_admin_info_view(_: Request):
    return FileResponse("html/change_admin.html")


# POST /administrator
async def get_admin(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]

    try:
        safe_parse_webapp_init_data(config.bot_token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        admin = await repo.get_admin_by_id(int(data["id"]))

    if not admin:
        return json_response({"ok": False, "error": "Not Found"}, status=404)

    return json_response(
        {
            "ok": True,
            "admin": {
                "id": admin.id,
                "first_name": admin.first_name,
                "last_name": admin.last_name,
                "patronymic": admin.patronymic,
                "email": admin.email,
                "user_name": admin.user_name,
                "tel": admin.tel,
                "level": admin.level,
                "description": admin.description,
                "timezone": admin.timezone,
                "telegram_id": admin.telegram_id,
                "access_start": admin.access_start.strftime(r"%Y-%m-%d"),
                "access_end": admin.access_end.strftime(r"%Y-%m-%d"),
            },
        }
    )


# POST /administrator/change-info
async def change_admin_info(request: Request):
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
        admin_model = parse_admin_register_data(data)
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        admin = await repo.get_admin_by_id(int(data["id"]))

        _update_admin(admin, admin_model)
        await session.commit()

    await _send_info(bot, init_data.user.id, data["msgId"])

    return json_response({"ok": True})


async def _send_info(bot: Bot, chat_id: int, mid: int | str) -> None:
    await delete_last_message(bot, chat_id, mid)
    await bot.send_message(chat_id, "Данные успешно изменены")


def _update_admin(admin: Administrator, admin_model: AdminModel) -> None:
    admin.id = admin_model.id
    admin.last_name = admin_model.last_name
    admin.first_name = admin_model.first_name
    admin.patronymic = admin_model.patronymic
    admin.email = admin_model.email
    admin.user_name = admin_model.user_name
    admin.tel = admin_model.tel
    admin.telegram_id = admin_model.tg_id
    admin.level = admin_model.level
    admin.description = admin_model.description
    admin.timezone = admin_model.timezone
    admin.access_end = admin_model.access_end
    admin.access_start = admin_model.access_start
