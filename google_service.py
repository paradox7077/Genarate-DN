import json
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_credentials():
    service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
    return service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )


def get_drive_service():
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)


def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)
