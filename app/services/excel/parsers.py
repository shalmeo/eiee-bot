from datetime import datetime, date

from app.misc.models import ParentModel


def parse_date(dates: str) -> tuple[date, date]:
    access_start_str, access_end_str = dates.split("/")
    access_start = datetime.strptime(access_start_str, r"%d.%m.%Y")
    access_end = datetime.strptime(access_end_str, r"%d.%m.%Y")

    return access_start.date(), access_end.date()


def parse_full_name(full_name: str) -> list[str, str, str]:
    return full_name.split()


def parse_tel(tel: int | str) -> int:
    tel = str(tel)
    if len(tel) == 10 and tel.isdigit():
        return int(tel)

    if len(tel) == 11 and tel.isdigit():
        return int(tel[1:])

    if len(tel) == 12:
        return int(tel[2:])


def parse_parent(full_name: str, tg_id: int, tel: int) -> ParentModel | None:
    try:
        last_name, first_name, patronymic = parse_full_name(full_name)
        tel = parse_tel(tel)
    except AttributeError:
        return

    return ParentModel(
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        tg_id=tg_id,
        tel=tel,
    )
