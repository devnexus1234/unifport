from datetime import datetime
import pytz

IST_TIMEZONE = pytz.timezone("Asia/Kolkata")

def get_ist_time() -> datetime:
    """
    Returns the current time in IST (Indian Standard Time).
    Returned datetime is timezone-aware.
    """
    return datetime.now(IST_TIMEZONE)

def get_ist_time_naive() -> datetime:
    """
    Returns the current time in IST as a naive datetime object.
    Useful for databases (like Oracle/SQLite) where naive datetimes 
    might be preferred or required by drivers.
    """
    return datetime.now(IST_TIMEZONE).replace(tzinfo=None)
