from aiogram import F, Bot, Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    User,
    Message,
    PhotoSize,
)
from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_reader import Settings
from app.keyboards.student.inline.current_tasks import get_input_file_kb
from app.misc.delete_message import delete_last_message
from app.misc.file_info import get_file_info
from app.misc.tasks import Tasks
from app.services.database.models import Group
from app.services.database.repositories.teacher import TeacherRepo
from app.services.database.repositories.default import DefaultRepo
from app.keyboards.teacher.inline.profile import ProfileAction, ProfileCallbackFactory
from app.keyboards.teacher.inline.groups import (
    AttachFilesCallbackFactory,
    GroupAction,
    GroupCallbackFactory,
    get_create_home_task_kb,
    get_groups_kb,
)

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.action == ProfileAction.CREATE_HOMETASK)
)
async def on_select_group_to_create_home_task(
    call: CallbackQuery, event_from_user: User, repo: DefaultRepo
):
    teacher = await repo.get_teacher(event_from_user.id)
    markup = get_groups_kb(teacher.groups, action=GroupAction.CREATE_HOME_TASK)
    await call.message.edit_text(
        text="Выберите группу для создания Д/З", reply_markup=markup
    )
    await call.answer()


@router.callback_query(
    GroupCallbackFactory.filter(F.action == GroupAction.CREATE_HOME_TASK)
)
async def on_create_home_task(
    call: CallbackQuery,
    callback_data: GroupCallbackFactory,
    config: Settings,
    repo: DefaultRepo,
):
    group = await repo.get(Group, callback_data.group_uuid)
    markup = get_create_home_task_kb(
        group=group, config=config, msg_id=call.message.message_id
    )
    await call.message.edit_text(
        "Создание домашенего задания\n\n" "Нажмите на кнопку чтобы создать Д/З",
        reply_markup=markup,
    )
    await call.answer()


@router.callback_query(AttachFilesCallbackFactory.filter())
async def on_attach_files(
    call: CallbackQuery, callback_data: AttachFilesCallbackFactory, state: FSMContext
):
    msg = await call.message.edit_text(
        "Пришлите сюда файлы или голосовые сообщения, которые хотите прикрепить к домашенему заданию"
    )
    await call.answer()

    await state.set_state("input_files_for_home_task")
    await state.update_data(
        task_uuid=callback_data.task_uuid, mid=msg.message_id, files=[]
    )


@router.message(
    F.photo[-1].as_("photo"),
    F.media_group_id.as_("media_group_id"),
    state="input_files_for_home_task",
)
async def input_home_task_files(
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
        callback="attach_home_task_files",
    )


@router.message(
    F.media_group_id.as_("media_group_id"),
    content_types=["document"],
    state="input_files_for_home_task",
)
async def input_home_task_files(
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
        callback="attach_home_task_files",
    )


@router.message(
    content_types=["document", "voice", "photo"],
    state="input_files_for_home_task",
)
async def on_input_file(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await delete_last_message(bot, message.from_user.id, data.get("mid"))

    files: list = data.get("files")
    file_id = get_file_info(message)
    files.append((file_id, message.content_type))

    markup = get_input_file_kb(callback="attach_home_task_files")
    msg = await message.answer(
        f"Отправлено файлов: <code>{len(files)}</code>\n\n"
        "Если количество файлов не соответствует отправленным, попробуйте отправить еще раз по одному файлу",
        reply_markup=markup,
    )

    await state.update_data(mid=msg.message_id, files=files)


@router.callback_query(text="attach_home_task_files", state="input_files_for_home_task")
async def on_attach_files(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    session: AsyncSession,
    teacher_repo: TeacherRepo,
):
    data = await state.get_data()
    home_task_id = data.get("home_task_id")
    for file in data.get("files"):
        file_id, file_type = file
        teacher_repo.attach_file(home_task_id, file_id, file_type)

    await session.commit()
    await delete_last_message(bot, call.from_user.id, call.message.message_id)
    await call.message.answer("Файлы успешно прикреплены!")
