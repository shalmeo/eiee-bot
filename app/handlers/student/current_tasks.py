from contextlib import suppress

from aiogram import F, Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, User, Message, PhotoSize
from aiogram.dispatcher.fsm.context import FSMContext
from arq import ArqRedis
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.filters.student.permission import PermissionToAttachFilter
from app.misc.delete_message import delete_last_message
from app.misc.media import get_media_groups
from app.misc.tasks import Tasks
from app.misc.text import get_home_task_text
from app.misc.file_info import get_file_info
from app.services.database.repositories.student import StudentRepo
from app.services.database.repositories.default import DefaultRepo
from app.keyboards.student.inline.profile import ProfileAction, ProfileCallbackFactory
from app.keyboards.student.inline.current_tasks import (
    HomeTaskAction,
    HomeTaskCallbackFactory,
    get_current_tasks_kb,
    get_home_task_info_kb,
    get_input_file_kb,
    get_select_group_kb,
    GroupCallbackFactory,
    GroupAction,
    HomeTaskPageController,
)

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.action == ProfileAction.CURRENT_TASKS)
)
async def on_select_group(call: CallbackQuery, student_repo: StudentRepo):
    groups = await student_repo.get_groups()
    markup = get_select_group_kb(groups, action=GroupAction.CUR_TASKS)
    await call.message.edit_text("Выберите группу", reply_markup=markup)
    await call.answer()


@router.callback_query(GroupCallbackFactory.filter(F.action == GroupAction.CUR_TASKS))
async def on_current_tasks(
    call: CallbackQuery,
    callback_data: GroupCallbackFactory,
    student_repo: StudentRepo,
    state: FSMContext,
):
    offset = 0
    current_home_tasks, limit = await student_repo.get_home_tasks(
        callback_data.group_uuid, offset
    )
    count = await student_repo.get_count_home_tasks(callback_data.group_uuid)
    markup = get_current_tasks_kb(
        current_home_tasks, offset, limit, count, callback_data.group_uuid
    )
    await call.message.edit_text("Текущее домашнeе задание", reply_markup=markup)
    await call.answer()

    await state.update_data(offset=offset)


@router.callback_query(HomeTaskCallbackFactory.filter(F.action == HomeTaskAction.INFO))
async def on_home_task_info(
    call: CallbackQuery,
    callback_data: HomeTaskCallbackFactory,
    event_from_user: User,
    repo: DefaultRepo,
):
    home_task = await repo.get_home_task(callback_data.home_task_uuid)
    student = await repo.get_student(event_from_user.id)
    extend_text = [
        f"Учитель: <code>{home_task.group.teacher.last_name} {home_task.group.teacher.first_name}</code>\n"
        f"Группа: <code>{home_task.group.title}</code>\n\n"
    ]
    text = get_home_task_text(home_task, student.timezone, "".join(extend_text))

    markup = get_home_task_info_kb(home_task.uuid, home_task.group.uuid)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(
    HomeTaskCallbackFactory.filter(F.action == HomeTaskAction.ATTACH_HOME_WORK),
    PermissionToAttachFilter(),
)
async def on_attach_home_work(
    call: CallbackQuery,
    callback_data: HomeTaskCallbackFactory,
    state: FSMContext,
):
    m = await call.message.edit_text(
        "Пришлите сюда файлы или голосовые сообщения, которые хотите прикрепить к домашенему заданию"
    )
    await call.answer()

    await state.set_state("input_home_work_files")
    await state.update_data(
        mid=m.message_id, files=[], home_task_uuid=callback_data.home_task_uuid
    )


@router.message(
    F.photo[-1].as_("photo"),
    F.media_group_id.as_("media_group_id"),
    state="input_home_work_files",
)
async def input_home_work_files(
    message: Message,
    photo: PhotoSize,
    media_group_id: str,
    redis: ArqRedis,
    tasks: Tasks,
):
    await redis.zadd(
        f"media_group:{media_group_id}",
        member=f"{photo.file_id}:{message.content_type}",
        score=float(message.message_id),
    )
    await tasks.handle_media_group(
        chat_id=message.chat.id,
        media_group_id=media_group_id,
        callback="attach_home_work",
    )


@router.message(
    F.media_group_id.as_("media_group_id"),
    content_types=["document"],
    state="input_home_work_files",
)
async def input_home_work_files(
    message: Message, media_group_id: str, redis: ArqRedis, tasks: Tasks
):
    file_id = get_file_info(message)

    await redis.zadd(
        f"media_group:{media_group_id}",
        member=f"{file_id}:{message.content_type}",
        score=float(message.message_id),
    )
    await tasks.handle_media_group(
        chat_id=message.chat.id,
        media_group_id=media_group_id,
        callback="attach_home_work",
    )


@router.message(
    content_types=["voice", "document", "photo"], state="input_home_work_files"
)
async def input_home_work_files(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    data = await state.get_data()
    await delete_last_message(bot, message.chat.id, data["mid"])

    file_id = get_file_info(message)
    files: list = data["files"]
    files.append((file_id, message.content_type))

    markup = get_input_file_kb(callback="attach_home_work")
    m = await message.answer(
        f"Отправлено файлов: <code>{len(files)}</code>\n\n"
        "Если количество файлов не соответствует отправленным, попробуйте отправить еще раз по одному файлу",
        reply_markup=markup,
    )

    await state.update_data(mid=m.message_id, files=files)


@router.callback_query(text="attach_home_work", state="input_home_work_files")
async def on_attach_files(
    call: CallbackQuery,
    state: FSMContext,
    student_repo: StudentRepo,
    session: AsyncSession,
):
    data = await state.get_data()

    home_work = await student_repo.add_home_work(data["home_task_uuid"])

    for file in data["files"]:
        fid, ftype = file
        student_repo.attach_file(fid, ftype, home_work.uuid)

    await session.commit()

    await call.message.delete()
    await call.message.answer("Файлы успешно прикреплены!")
    await state.clear()


@router.callback_query(
    HomeTaskCallbackFactory.filter(F.action == HomeTaskAction.ATTACHED_FILES)
)
async def on_attached_files(
    call: CallbackQuery,
    callback_data: HomeTaskCallbackFactory,
    bot: Bot,
    student_repo: StudentRepo,
):
    files = await student_repo.get_home_task_files(callback_data.home_task_uuid)
    photo_media_group, document_media_group, voices = get_media_groups(files)

    for media_group in (photo_media_group, document_media_group):
        if media_group:
            await bot.send_media_group(call.from_user.id, media_group)

    if voices:
        for v in voices:
            await call.message.answer_voice(v)

    await call.answer()


@router.callback_query(HomeTaskPageController.filter())
async def page_controller(
    call: CallbackQuery,
    callback_data: HomeTaskPageController,
    state: FSMContext,
    student_repo: StudentRepo,
):
    try:
        home_tasks, limit = await student_repo.get_home_tasks(
            callback_data.group_uuid, offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return

    pages = callback_data.count // limit + bool(callback_data.count % limit)
    current_page = callback_data.offset // limit + 1

    if 1 <= current_page <= pages:
        markup = get_current_tasks_kb(
            home_tasks,
            callback_data.offset,
            limit,
            callback_data.count,
            callback_data.group_uuid,
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()
