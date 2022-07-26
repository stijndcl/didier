import datetime
import zoneinfo

__all__ = ["LOCAL_TIMEZONE", "today_only_date"]

LOCAL_TIMEZONE = zoneinfo.ZoneInfo("Europe/Brussels")


def today_only_date() -> datetime.datetime:
    """Mongo can't handle datetime.date, so we need datetime

    We do, however, only care about the date, so remove all the rest
    """
    return datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
