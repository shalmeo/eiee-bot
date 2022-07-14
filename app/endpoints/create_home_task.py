import datetime
from typing import Iterable

from aiogram import Bot
from aiogram.dispatcher.fsm.storage.base import StorageKey
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_request import Request
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.keyboards.teacher.inline.groups import get_create_home_task_kb
from app.misc.date_utils import utc_to_local, local_to_utc
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.parse import parse_home_task_data
from app.misc.tasks import Tasks
from app.misc.text import get_home_task_text
from app.services.database.models import HomeTask, Student
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.teacher import TeacherRepo


# GET /teacher/create-home-task-form
async def create_home_task_view(_: Request):
    return FileResponse("html/create_home_task.html")


# POST /teacher/create-home-task
async def create_home_task(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    bot: Bot = request.app["bot"]
    session_factory: sessionmaker = request.app["session_factory"]
    storage: RedisStorage = request.app["storage"]
    tasks: Tasks = request.app["tasks"]

    try:
        init_data = safe_parse_webapp_init_data(
            config.bot_token, init_data=data["_auth"]
        )
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    try:
        form = parse_home_task_data(data)
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        teacher_repo = TeacherRepo(session)

        teacher = await repo.get_teacher(init_data.user.id)
        task = teacher_repo.add_new_home_task(form, teacher.timezone)
        await session.commit()

    async with session_factory() as session:
        repo = DefaultRepo(session)
        home_task = await repo.get(HomeTask, task.uuid)
        students = await repo.get_students_in_group(home_task.group_id)

    await _send_info(bot, init_data.user.id, home_task, data["msgId"], teacher.timezone)

    key = StorageKey(bot.id, init_data.user.id, init_data.user.id)
    await storage.update_data(bot, key, {"home_task_id": home_task.uuid})

    await _shedule_distribution(students, home_task, tasks)
    return json_response({"ok": True})


async def _send_info(
    bot: Bot,
    user_id: int,
    home_task: HomeTask,
    msg_id: int | str,
    timezone: str,
) -> None:
    text = get_home_task_text(home_task, timezone)
    markup = get_create_home_task_kb(home_task.group, with_webapp=False)
    await delete_last_message(bot, user_id, msg_id)
    await bot.send_message(user_id, text, reply_markup=markup)


async def _shedule_distribution(
    students: Iterable[Student], home_task: HomeTask, tasks: Tasks
) -> None:
    for s in students:
        text = "Напоминание. Приближается время сдачи Д/З\n\n" + get_home_task_text(
            home_task, s.timezone
        )
        local_dt = utc_to_local(home_task.deadline, s.timezone)

        reminder_dt = local_dt - datetime.timedelta(hours=4)

        if datetime.time(10, 0, 0) <= reminder_dt.time():
            reminder_dt = reminder_dt.replace(hour=0, minute=0) + datetime.timedelta(
                hours=18
            )

        elif reminder_dt.time() <= datetime.time(9, 0, 0):
            reminder_dt = (
                reminder_dt.replace(hour=0, minute=0)
                - datetime.timedelta(days=1)
                + datetime.timedelta(hours=18)
            )

        await tasks.send_message(
            s.telegram_id,
            text,
            local_to_utc(reminder_dt, s.timezone, with_replace=False),
        )
