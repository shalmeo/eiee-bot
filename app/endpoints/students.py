from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.services.database.repositories.superadmin import SuperAdminRepo


# POST /students
async def get_all_students(request: Request):
    data = await request.post()
    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]

    try:
        safe_parse_webapp_init_data(config.bot_token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    async with session_factory() as session:
        repo = SuperAdminRepo(session, 0)
        students = await repo.get_students_notin_group(data["group_uuid"])

    data = []
    for s in students:
        sid, lname, fname, mname = s
        data.append([sid, f"{lname} {fname} {mname}"])

    return json_response({"data": data})
