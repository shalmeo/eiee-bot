import dataclass_factory
import openpyxl

from typing import BinaryIO


from app.misc.exceptions import ExcelCellValidateError
from app.misc.models import StudentModel
from app.services.excel.parsers import (
    parse_full_name,
    parse_date,
    parse_tel,
    parse_parent,
)


def import_students_excel(downloaded: BinaryIO) -> tuple[int, list[StudentModel]]:
    workbook = openpyxl.load_workbook(downloaded).active
    factory = dataclass_factory.Factory()

    list_of_students = []
    for row in workbook.iter_rows(min_row=2, min_col=2, max_col=16):
        student_info = []
        for cell in row:
            student_info.append(cell.value)

        try:
            student = _get_student_model(student_info)
            serialized = factory.dump(student)
            list_of_students.append(serialized)
        except (ExcelCellValidateError, ValueError, AttributeError):
            continue

    return len(list_of_students), list_of_students


def _get_student_model(student_info: list) -> StudentModel:
    unique_id_col = 0
    access_dates_col = 1
    creator_id = 2
    timezone_col = 3
    full_name_col = 4
    email_col = 5
    user_name_col = 6
    tg_id_col = 7
    tel_col = 8

    full_name_p1_col = 9
    full_name_p2_col = 12

    uninque_id = int(student_info[unique_id_col])
    creator_id = int(student_info[creator_id])
    access_start, access_end = parse_date(student_info[access_dates_col])
    timezone = student_info[timezone_col]
    last_name, first_name, patronymic = parse_full_name(student_info[full_name_col])
    email = student_info[email_col]
    user_name = student_info[user_name_col]
    tg_id = int(student_info[tg_id_col])
    tel = parse_tel(student_info[tel_col])

    parents = []
    parent1 = parse_parent(*student_info[full_name_p1_col:full_name_p2_col])
    parent2 = parse_parent(*student_info[full_name_p2_col:])
    for parent in (parent1, parent2):
        if parent:
            parents.append(parent)

    if not all((access_start, access_end, timezone, email, user_name, tg_id, tel)):
        print("TUT")
        raise ExcelCellValidateError()

    return StudentModel(
        id=uninque_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        tel=tel,
        email=email,
        tg_id=tg_id,
        user_name=user_name,
        access_start=access_start,
        access_end=access_end,
        timezone=timezone,
        admin_id=creator_id,
        parents=parents,
    )
