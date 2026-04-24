from datetime import datetime
import pytz
from app.core.config import settings


def get_timezone():
    """Get configured timezone"""
    return pytz.timezone(settings.TIMEZONE)


def get_current_time():
    """Get current time in configured timezone"""
    tz = get_timezone()
    return datetime.now(tz)


def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt is None:
        return None
    tz = get_timezone()
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(tz)


def local_to_utc(local_dt):
    """Convert local datetime to UTC"""
    if local_dt is None:
        return None
    tz = get_timezone()
    if local_dt.tzinfo is None:
        local_dt = tz.localize(local_dt)
    return local_dt.astimezone(pytz.utc)
