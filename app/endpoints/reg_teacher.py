from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.keyboards.superadmin.inline.registryof_teachers import get_teacher_info_kb
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.parse import parse_teacher_register_data
from app.misc.text import get_teacher_info_text
from app.services.database.models import Teacher
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.superadmin import SuperAdminRepo


# GET /administrator/reg-form
async def teacher_register_view(request: Request):
    return FileResponse("html/reg_teacher.html")


# POST /teacher/register
async def teacher_register(request: Request):
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
        form = parse_teacher_register_data(data)
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        admin_repo = SuperAdminRepo(session, init_data.user.id)
        repo = DefaultRepo(session)
        if await repo.get_teacher(form.tg_id):
            return json_response(
                {"ok": False, "error": "User already exists"}, status=409
            )

        teacher = admin_repo.add_new_teacher(form)
        await session.commit()

    await _send_info(bot, init_data.user.id, teacher, form.msg_id, config)

    return json_response({"ok": True})


async def _send_info(
    bot: Bot, user_id: int, teacher: Teacher, msg_id: int, config: Settings
) -> None:
    text = get_teacher_info_text(teacher)
    markup = get_teacher_info_kb(config, msg_id, user_id)
    await delete_last_message(bot, user_id, msg_id)
    await bot.send_message(user_id, text, reply_markup=markup)
