import datetime
from dateutil import tz


def date_format(d: datetime.date) -> str:
    return d.strftime(r"%d.%m.%Y")


def datetime_format(dt: datetime.datetime) -> str:
    return dt.strftime(r"%d.%m.%Y %H:%M")


def utc_to_local(utc_dt: datetime.datetime, local: str) -> datetime.datetime:
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=tz.tzstr(local))


def local_to_utc(dt: datetime.datetime, local: str) -> datetime.datetime:
    return (
        dt.replace(tzinfo=tz.tzstr(local))
        .astimezone(tz=datetime.timezone.utc)
        .replace(tzinfo=None)
    )
