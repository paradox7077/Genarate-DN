from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = "/etc/secrets/service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_credentials():
    path = Path(SERVICE_ACCOUNT_FILE)

    if not path.exists():
        raise FileNotFoundError(
            "ไม่พบไฟล์ service_account.json ที่ /etc/secrets/service_account.json "
            "กรุณาตรวจสอบ Render > Environment > Secret Files ว่ามีไฟล์ชื่อ service_account.json "
            "และกด Save, rebuild, and deploy แล้ว"
        )

    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )


def get_drive_service():
    return build("drive", "v3", credentials=get_credentials())


def get_sheets_service():
    return build("sheets", "v4", credentials=get_credentials())
