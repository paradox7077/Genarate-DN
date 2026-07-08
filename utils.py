from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

THAI_ZONE = ZoneInfo("Asia/Bangkok")


def thai_now():
    return datetime.now(THAI_ZONE)


def thai_date_folder():
    now = thai_now()
    return now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")


def build_date_folder(base_dir: str):
    year, month, day = thai_date_folder()
    folder = Path(base_dir) / year / month / day
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def generate_prefix(file_prefix="EG"):
    now = thai_now()
    return f"{file_prefix}{now.strftime('%y%m%d%H%M')}"
