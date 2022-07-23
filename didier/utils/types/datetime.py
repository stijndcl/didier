import datetime
import zoneinfo

__all__ = ["LOCAL_TIMEZONE", "int_to_weekday", "str_to_date"]


LOCAL_TIMEZONE = zoneinfo.ZoneInfo("Europe/Brussels")


def int_to_weekday(number: int) -> str:  # pragma: no cover # it's useless to write a test for this
    """Get the Dutch name of a weekday from the number"""
    return ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"][number]


def str_to_date(date_str: str) -> datetime.date:
    """Turn a string into a DD/MM/YYYY date"""
    return datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
