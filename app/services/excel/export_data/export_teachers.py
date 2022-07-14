import io
from typing import Iterable

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from app.misc.date_utils import date_format
from app.services.database.models import Teacher
from app.services.excel.format import format_row


def get_excel_teachers(teachers: Iterable[Teacher]) -> io.BytesIO:
    output = io.BytesIO()
    workbook = openpyxl.load_workbook("./resources/excel/teachers.xlsx")
    worksheet = workbook.active
    _fill_data(worksheet, teachers)
    workbook.save(output)
    output.seek(0)
    return output


def _fill_data(worksheet: Worksheet, teachers: Iterable[Teacher]) -> None:
    for i, a in enumerate(teachers, 1):
        worksheet.append(
            (
                i,
                a.id,
                f"{date_format(a.access_start)}/{date_format(a.access_end)}",
                a.admin_id,
                a.timezone,
                f"{a.last_name} {a.first_name} {a.patronymic}",
                a.email,
                a.user_name,
                a.telegram_id,
                a.tel,
                a.level,
                a.description,
            )
        )

        format_row(worksheet, i + 1, max_col=12)
