from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.misc.delete_message import delete_last_message
from app.misc.models import ParentModel
from app.misc.parse import parse_parent
from app.services.database.models import Parent
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo


# GET /student/change-parents-info
async def change_student_parents_info_view(_: Request):
    return FileResponse("html/change_student_parents.html")


# POST /student/parents
async def get_student_parents(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]

    # try:
    #     safe_parse_webapp_init_data(config.bot_token, init_data=data["_auth"])
    # except ValueError:
    #     return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        parents = await repo.get_parents_by_id(int(data["id"]))

    parents_list = []

    for p in parents:
        parents_list.append(
            {
                "first_name": p.first_name,
                "last_name": p.last_name,
                "patronymic": p.patronymic,
                "tel": p.tel,
                "telegram_id": p.id,
            }
        )

    return json_response({"ok": True, "parents": parents_list})


# POST /student/change-parents-info
async def change_student_parents_info(request: Request):
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

    parent1 = parse_parent(data.get("parent1", ""))
    parent2 = parse_parent(data.get("parent2", ""))

    async with session_factory() as session:
        admin_repo = SuperAdminRepo(session, init_data.user.id)
        repo = DefaultRepo(session)

        for p in (parent1, parent2):
            if not p:
                continue
            parent = await repo.get(Parent, p.tg_id)
            if not parent:
                admin_repo.add_new_parent(p)
            else:
                _update_parent(parent, p)

            if not await repo.get_family(int(data["id"]), p.tg_id):
                admin_repo.add_new_family(int(data["id"]), p.tg_id)

        await session.commit()

    await _send_info(bot, init_data.user.id, data["msgId"])

    return json_response({"ok": True})


async def _send_info(bot: Bot, chat_id: int, mid: int | str) -> None:
    await delete_last_message(bot, chat_id, mid)
    await bot.send_message(chat_id, "Данные успешно изменены")


def _update_parent(parent: Parent, parent_model: ParentModel) -> None:
    parent.first_name = parent_model.first_name
    parent.last_name = parent_model.last_name
    parent.patronymic = parent_model.patronymic
    parent.id = parent_model.tg_id
    parent.tel = parent_model.tel
