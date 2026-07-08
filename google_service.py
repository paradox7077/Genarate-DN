import json
import os
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

    if path.exists():
        return service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )

    json_text = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if json_text:
        service_account_info = json.loads(json_text)
        return service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )

    raise FileNotFoundError(
        "ไม่พบ Google credential ทั้ง 2 ช่องทาง: "
        "1) /etc/secrets/service_account.json "
        "หรือ 2) Environment Variable GOOGLE_SERVICE_ACCOUNT_JSON"
    )


def get_drive_service():
    return build("drive", "v3", credentials=get_credentials())


def get_sheets_service():
    return build("sheets", "v4", credentials=get_credentials())
