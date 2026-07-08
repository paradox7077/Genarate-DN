from pathlib import Path
from tempfile import NamedTemporaryFile

from converter import convert_pdf_file, load_config
from google_drive import find_or_create_folder, upload_pdf
from google_sheet import append_log, get_existing_job_numbers
from utils import thai_now


def generate_job_no(config, existing_jobs):
    prefix = config.get("file_prefix", "EG")
    now = thai_now()
    base = f"{prefix}{now.strftime('%y%m%d%H%M')}"

    running = 1
    while f"{base}{running:03d}" in existing_jobs:
        running += 1

    return f"{base}{running:03d}"


def process_document(uploaded_file, config_path="config.json", template_path="ShippingForm.pdf", source="Web"):
    config = load_config(config_path)

    root_folder_id = config["google_drive_root_folder_id"]
    sheet_id = config["google_sheet_id"]

    existing_jobs = get_existing_job_numbers(sheet_id)
    job_no = generate_job_no(config, existing_jobs)

    now = thai_now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    jobs_folder = find_or_create_folder("Jobs", root_folder_id)
    year_folder = find_or_create_folder(year, jobs_folder["id"])
    month_folder = find_or_create_folder(month, year_folder["id"])
    job_folder = find_or_create_folder(job_no, month_folder["id"])

    original_file_name = uploaded_file.name
    source_file_name = "Source.pdf"
    output_file_name = f"{job_no}.pdf"

    with NamedTemporaryFile(delete=False, suffix=".pdf") as source_temp:
        source_temp.write(uploaded_file.read())
        source_temp_path = Path(source_temp.name)

    with NamedTemporaryFile(delete=False, suffix=".pdf") as output_temp:
        output_temp_path = Path(output_temp.name)

    source_drive_file = upload_pdf(
        file_path=source_temp_path,
        file_name=source_file_name,
        parent_id=job_folder["id"]
    )

    convert_pdf_file(
        input_pdf_path=source_temp_path,
        output_pdf_path=output_temp_path,
        config_path=config_path,
        template_path=template_path
    )

    output_drive_file = upload_pdf(
        file_path=output_temp_path,
        file_name=output_file_name,
        parent_id=job_folder["id"]
    )

    upload_time = now.strftime("%Y-%m-%d %H:%M:%S")
    convert_time = thai_now().strftime("%Y-%m-%d %H:%M:%S")

    append_log(sheet_id, [
        job_no,
        original_file_name,
        output_file_name,
        upload_time,
        convert_time,
        "",
        source,
        "Success",
        job_folder.get("webViewLink", ""),
        source_drive_file.get("webViewLink", ""),
        output_drive_file.get("webViewLink", "")
    ])

    return {
        "job_no": job_no,
        "output_file_name": output_file_name,
        "output_path": output_temp_path,
        "folder_link": job_folder.get("webViewLink", ""),
        "source_link": source_drive_file.get("webViewLink", ""),
        "output_link": output_drive_file.get("webViewLink", "")
    }
