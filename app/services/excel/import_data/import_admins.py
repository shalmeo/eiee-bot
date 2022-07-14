import dataclass_factory
import openpyxl

from typing import BinaryIO

from app.misc.exceptions import ExcelCellValidateError
from app.misc.models import AdminModel
from app.services.excel.parsers import parse_date, parse_full_name, parse_tel


def import_admins_excel(downloaded: BinaryIO) -> tuple[int, list[AdminModel]]:
    workbook = openpyxl.load_workbook(downloaded)
    worksheet = workbook.active
    factory = dataclass_factory.Factory()

    list_of_admins = []
    for row in worksheet.iter_rows(min_row=2, min_col=2, max_col=11):
        admin_info = []
        for cell in row:
            admin_info.append(cell.value)
        try:
            admin = _get_admin_model(admin_info)
        except (ExcelCellValidateError, ValueError, AttributeError):
            continue
        serialized = factory.dump(admin)
        list_of_admins.append(serialized)

    return len(list_of_admins), list_of_admins


def _get_admin_model(admin_info: list[str]) -> AdminModel:
    unique_id_col = 0
    access_dates_col = 1
    timezone_col = 2
    full_name_col = 3
    email_col = 4
    user_name_col = 5
    tg_id_col = 6
    tel_col = 7
    level_col = 8
    description_col = 9

    unuque_id = int(admin_info[unique_id_col])
    access_start, access_end = parse_date(admin_info[access_dates_col])
    timezone = admin_info[timezone_col]
    last_name, first_name, patronymic = parse_full_name(admin_info[full_name_col])
    email = admin_info[email_col]
    user_name = admin_info[user_name_col]
    tg_id = int(admin_info[tg_id_col])
    tel = parse_tel(admin_info[tel_col])
    level = admin_info[level_col] or ""
    description = admin_info[description_col] or ""

    if not all((access_start, access_end, timezone, email, user_name, tg_id, tel)):
        raise ExcelCellValidateError()

    return AdminModel(
        id=unuque_id,
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
    )
