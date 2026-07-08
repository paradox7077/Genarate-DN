from google_service import get_sheets_service
from utils import thai_now

def append_log(sheet_id, row):
    service = get_sheets_service()

    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="A:K",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]}
    ).execute()

def get_existing_job_numbers(sheet_id):
    service = get_sheets_service()

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="A:A"
    ).execute()

    values = result.get("values", [])
    return [row[0] for row in values[1:] if row]
