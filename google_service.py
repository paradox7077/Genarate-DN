from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = "/etc/secrets/service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_credentials():
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )


def get_drive_service():
    return build("drive", "v3", credentials=get_credentials())


def get_sheets_service():
    return build("sheets", "v4", credentials=get_credentials())
