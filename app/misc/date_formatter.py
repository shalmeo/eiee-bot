import datetime


def date_format(date: datetime.date) -> str:
    return date.strftime(r"%d.%m.%Y")
