import io
from typing import Iterable

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from app.misc.date_utils import date_format
from app.services.database.models import Administrator
from app.services.excel.format import format_row


def get_excel_admins(admins: Iterable[Administrator]) -> io.BytesIO:
    output = io.BytesIO()
    workbook = openpyxl.load_workbook("./resources/excel/admins.xlsx")
    worksheet = workbook.active
    _fill_data(worksheet, admins)
    workbook.save(output)
    output.seek(0)
    return output


def _fill_data(worksheet: Worksheet, admins: Iterable[Administrator]) -> None:
    for i, a in enumerate(admins, 1):
        worksheet.append(
            (
                i,
                a.id,
                f"{date_format(a.access_start)}/{date_format(a.access_end)}",
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

        format_row(worksheet, i + 1, max_col=11)
