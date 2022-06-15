import re

import dataclass_factory
import openpyxl

from datetime import datetime
from typing import BinaryIO

from app.misc.exceptions import ExcelCellValidateError
from app.misc.models import AdminModel


def parse_registryof_admins_excel(downloaded: BinaryIO) -> tuple[int, list[AdminModel]]:
    workbook = openpyxl.load_workbook(downloaded).active
    factory = dataclass_factory.Factory()

    list_of_admins = []
    for row in workbook.iter_rows(min_row=2, min_col=3, max_col=12):
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
    access_dates_col = 0
    timezone_col = 2
    full_name_col = 3
    email_col = 4
    user_name_col = 5
    tg_id_col = 6
    tel_col = 7
    level_col = 8
    description_col = 9

    access_start, access_end = _parse_date(admin_info[access_dates_col])
    timezone = _parse_timezone(admin_info[timezone_col])
    last_name, first_name, patronymic = _parse_full_name(admin_info[full_name_col])
    email = admin_info[email_col]
    user_name = admin_info[user_name_col]
    tg_id = int(admin_info[tg_id_col])
    tel = _parse_tel(admin_info[tel_col])
    level = admin_info[level_col] or ""
    description = admin_info[description_col] or ""

    if not all((access_start, access_end, timezone, email, user_name, tg_id, tel)):
        raise ExcelCellValidateError()

    return AdminModel(
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


def _parse_date(dates: str) -> list[datetime, datetime]:
    make_to_digits = lambda str_date: re.sub(r"\D+", "", str_date)
    make_to_datetime = lambda int_date: datetime.strptime(
        make_to_digits(int_date), r"%d%m%Y%H%M"
    )
    access_start, access_end = map(make_to_datetime, dates.split("/"))

    return access_start, access_end


def _parse_timezone(timezone: str) -> str:
    utc, deviation, *_ = timezone.split()
    return utc + deviation


def _parse_full_name(full_name: str) -> tuple[str, str, str]:
    return full_name.split()


def _parse_tel(tel: int | str) -> int:
    tel = str(tel)
    if len(tel) == 10 and tel.isdigit():
        return int(tel)

    if len(tel) == 11 and tel.isdigit():
        return int(tel[1:])

    if len(tel) == 12:
        return int(tel[2:])
