from aiogram import Router, F, types

from app.keyboards.student.inline.profile import ProfileCallbackFactory, ProfileAction
from app.services.database.repositories.student import StudentRepo

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.action == ProfileAction.IN_CHECK)
)
async def on_select_group(call: types.CallbackQuery, student_repo: StudentRepo):
    home_works = await student_repo.get_home_works_in_check()

    text = ["Работы в проверке\n\n", "<code>№ Д/З - группа - итераций</code>\n\n"]

    for i, hw in enumerate(home_works, 1):
        count = await student_repo.get_count_home_works(hw.home_task_id)
        text.append(
            f"{i}) № {hw.home_task.number} - {hw.home_task.group.title} - {count}\n"
        )

    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Назад", callback_data="to_profile")]
        ]
    )
    await call.message.edit_text("".join(text), reply_markup=markup)
    await call.answer()
