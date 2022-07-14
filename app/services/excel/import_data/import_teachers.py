import dataclass_factory
import openpyxl

from typing import BinaryIO

from app.misc.exceptions import ExcelCellValidateError
from app.misc.models import TeacherModel
from app.services.excel.parsers import (
    parse_tel,
    parse_date,
    parse_full_name,
)


def import_teachers_excel(downloaded: BinaryIO) -> tuple[int, list[TeacherModel]]:
    workbook = openpyxl.load_workbook(downloaded).active
    factory = dataclass_factory.Factory()

    list_of_teachers = []
    for row in workbook.iter_rows(min_row=2, min_col=2, max_col=12):
        teacher_info = []
        for cell in row:
            teacher_info.append(cell.value)
        try:
            teacher = _get_teacher_model(teacher_info)
            serialized = factory.dump(teacher)
            list_of_teachers.append(serialized)
        except (ExcelCellValidateError, ValueError, AttributeError) as e:
            continue
    return len(list_of_teachers), list_of_teachers


def _get_teacher_model(teacher_info: list[str]) -> TeacherModel:
    unique_id_col = 0
    access_dates_col = 1
    creator_id_col = 2
    timezone_col = 3
    full_name_col = 4
    email_col = 5
    user_name_col = 6
    tg_id_col = 7
    tel_col = 8
    level_col = 9
    description_col = 10

    unique_id = int(teacher_info[unique_id_col])
    creator_id = int(teacher_info[creator_id_col])
    access_start, access_end = parse_date(teacher_info[access_dates_col])
    timezone = teacher_info[timezone_col]
    last_name, first_name, patronymic = parse_full_name(teacher_info[full_name_col])
    email = teacher_info[email_col]
    user_name = teacher_info[user_name_col]
    tg_id = int(teacher_info[tg_id_col])
    tel = parse_tel(teacher_info[tel_col])
    level = teacher_info[level_col] or ""
    description = teacher_info[description_col] or ""

    if not all((access_start, access_end, timezone, email, user_name, tg_id, tel)):
        raise ExcelCellValidateError()

    return TeacherModel(
        id=unique_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        tel=tel,
        email=email,
        tg_id=tg_id,
        user_name=user_name,
        level=level,
        description=description,
        access_start=access_start,
        access_end=access_end,
        timezone=timezone,
        admin_id=creator_id,
    )
