from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.config import settings

DATETIME_DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S"


def display_timezone() -> ZoneInfo:
    try:
        return ZoneInfo(settings.display_timezone)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(display_timezone()).strftime(DATETIME_DISPLAY_FORMAT)
