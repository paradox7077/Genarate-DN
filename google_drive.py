from googleapiclient.http import MediaFileUpload
from google_service import get_drive_service

def find_or_create_folder(name, parent_id):
    service = get_drive_service()

    query = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed=false"
    )

    result = service.files().list(
        q=query,
        fields="files(id, name, webViewLink)",
        supportsAllDrives=True
    ).execute()

    files = result.get("files", [])
    if files:
        return files[0]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }

    folder = service.files().create(
        body=metadata,
        fields="id, name, webViewLink",
        supportsAllDrives=True
    ).execute()

    return folder

def upload_pdf(file_path, file_name, parent_id):
    service = get_drive_service()

    metadata = {
        "name": file_name,
        "parents": [parent_id]
    }

    media = MediaFileUpload(str(file_path), mimetype="application/pdf")

    file = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name, webViewLink",
        supportsAllDrives=True
    ).execute()

    return file
