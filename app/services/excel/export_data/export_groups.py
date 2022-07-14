import io
from typing import Sequence

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from app.services.database.models import Group, Student
from app.services.excel.format import format_row


def get_excel_groups(groups: list[tuple[Group, Sequence[Student]]]) -> io.BytesIO:
    output = io.BytesIO()
    workbook = openpyxl.load_workbook("./resources/excel/groups.xlsx")
    worksheet = workbook.active
    _fill_data(worksheet, groups)
    workbook.save(output)
    output.seek(0)
    return output


def _fill_data(
    worksheet: Worksheet, groups: list[tuple[Group, Sequence[Student]]]
) -> None:
    for i, g in enumerate(groups, 1):
        group, students = g
        worksheet.append(
            (
                i,
                group.uuid,
                group.admin_id,
                group.title,
                group.description,
                group.teacher_id,
                *students,
            )
        )

        format_row(worksheet, i + 1, max_col=16)
