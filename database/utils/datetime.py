import datetime
import zoneinfo

__all__ = ["LOCAL_TIMEZONE", "today_only_date"]

LOCAL_TIMEZONE = zoneinfo.ZoneInfo("Europe/Brussels")


def today_only_date() -> datetime.datetime:
    """Mongo can't handle datetime.date, so we need a datetime instance

    We do, however, only care about the date, so remove all the rest
    """
    today = datetime.date.today()
    return datetime.datetime(year=today.year, month=today.month, day=today.day)
