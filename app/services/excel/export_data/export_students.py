import io
from typing import Sequence

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from app.misc.date_utils import date_format
from app.services.database.models import Student, Parent
from app.services.excel.format import format_row


def get_excel_students(students: list[tuple[Student, Sequence[Parent]]]) -> io.BytesIO:
    output = io.BytesIO()
    workbook = openpyxl.load_workbook("./resources/excel/students.xlsx")
    worksheet = workbook.active
    _fill_data(worksheet, students)
    workbook.save(output)
    output.seek(0)
    return output


def _fill_data(
    worksheet: Worksheet, students: list[tuple[Student, Sequence[Parent]]]
) -> None:
    for i, s in enumerate(students, 1):
        student, parents = s

        parent1, parent2 = _get_parents_info(parents)

        worksheet.append(
            (
                i,
                student.id,
                f"{date_format(student.access_start)}/{date_format(student.access_end)}",
                student.admin_id,
                student.timezone,
                f"{student.last_name} {student.first_name} {student.patronymic}",
                student.email,
                student.user_name,
                student.telegram_id,
                student.tel,
                *parent1,
                *parent2,
            )
        )

        format_row(worksheet, i + 1, max_col=16)


def _get_parents_info(parents):
    if len(parents) == 2:
        parent1 = (
            f"{parents[0].last_name} {parents[0].first_name} {parents[0].patronymic}",
            parents[0].id,
            parents[0].tel,
        )
        parent2 = (
            f"{parents[1].last_name} {parents[1].first_name} {parents[1].patronymic}",
            parents[1].id,
            parents[1].tel,
        )
    elif len(parents) == 1:
        parent1 = (
            f"{parents[0].last_name} {parents[0].first_name} {parents[0].patronymic}",
            parents[0].id,
            parents[0].tel,
        )
        parent2 = (None, None, None)
    else:
        parent1 = (None, None, None)
        parent2 = (None, None, None)

    return parent1, parent2
