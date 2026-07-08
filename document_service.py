import base64
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests

from converter import convert_pdf_file, load_config
from utils import thai_now


def generate_base_job_no(config):
    prefix = config.get("file_prefix", "EG")
    now = thai_now()
    return f"{prefix}{now.strftime('%y%m%d%H%M')}"


def file_to_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def process_document(uploaded_file, config_path="config.json", template_path="ShippingForm.pdf", source="Web"):
    config = load_config(config_path)

    apps_script_url = config["apps_script_url"]
    base_job_no = generate_base_job_no(config)

    now = thai_now()
    upload_time = now.strftime("%Y-%m-%d %H:%M:%S")

    original_file_name = uploaded_file.name

    with NamedTemporaryFile(delete=False, suffix=".pdf") as source_temp:
        source_temp.write(uploaded_file.read())
        source_temp_path = Path(source_temp.name)

    with NamedTemporaryFile(delete=False, suffix=".pdf") as output_temp:
        output_temp_path = Path(output_temp.name)

    convert_pdf_file(
        input_pdf_path=source_temp_path,
        output_pdf_path=output_temp_path,
        config_path=config_path,
        template_path=template_path
    )

    convert_time = thai_now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "base_job_no": base_job_no,
        "original_file_name": original_file_name,
        "upload_time": upload_time,
        "convert_time": convert_time,
        "source": source,
        "source_pdf_base64": file_to_base64(source_temp_path),
        "output_pdf_base64": file_to_base64(output_temp_path),
    }

    response = requests.post(apps_script_url, json=payload, timeout=120)

    try:
        result = response.json()
    except Exception:
        raise Exception(f"Apps Script ไม่ได้ตอบกลับเป็น JSON: {response.text}")

    if result.get("status") != "success":
        raise Exception(f"Apps Script Error: {result}")

    return {
        "job_no": result.get("job_no", ""),
        "output_file_name": result.get("output_file_name", ""),
        "output_path": output_temp_path,
        "folder_link": result.get("folder_link", ""),
        "source_link": result.get("source_link", ""),
        "output_link": result.get("output_link", "")
    }
