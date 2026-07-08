from datetime import datetime
from zoneinfo import ZoneInfo

THAI_ZONE = ZoneInfo("Asia/Bangkok")


def thai_now():
    return datetime.now(THAI_ZONE)


def thai_date_folder():
    now = thai_now()
    return (
        now.strftime("%Y"),
        now.strftime("%m"),
        now.strftime("%d")
    )


def generate_prefix():
    now = thai_now()
    return now.strftime("EG%y%m%d%H%M")
