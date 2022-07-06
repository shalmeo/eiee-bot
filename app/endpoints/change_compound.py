import json

from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.misc.delete_message import delete_last_message
from app.services.database.repositories.superadmin import SuperAdminRepo


# GET /group/change-compound
async def change_compound_view(request: Request):
    return FileResponse("html/change_compound.html")


# POST /group/students
async def get_students(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]

    try:
        safe_parse_webapp_init_data(config.bot_token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    async with session_factory() as session:
        repo = SuperAdminRepo(session, 0)

        students = await repo.get_students_in_group(data["group_uuid"])

    data = []
    for s in students:
        sid, lname, fname, mname = s
        data.append([sid, f"{lname} {fname} {mname}"])

    return json_response({"data": data})


# POST /group/change-compound
async def change_compound(request: Request):
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

    async with session_factory() as session:
        repo = SuperAdminRepo(session, init_data.user.id)
        await repo.delete_students_from_group(data["group_uuid"])

        students = json.loads(data["data"])
        for s in students:
            if isinstance(s, dict):
                sid = int(s["0"])
            elif isinstance(s, list):
                sid, _ = s
            else:
                continue

            repo.add_student_in_group(sid, data["group_uuid"])

        await session.commit()

    await _send_info(bot, init_data.user.id, data["mid"])

    return json_response({"ok": True})


async def _send_info(bot, user_id, mid) -> None:
    text = "Состав группы успешно изменен"
    await delete_last_message(bot, user_id, mid)
    await bot.send_message(user_id, text)
