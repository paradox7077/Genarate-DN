import json
from pathlib import Path
import fitz


def load_config(config_path="config.json"):
    default_config = {
        "company_name": "EGGMall",
        "file_prefix": "EG",
        "admin_password": "7077",
        "header_height_cm": 4.5,
        "erase_height_cm": 8.0,
        "header_y_cm": 0.0,
        "apply_to_all_pages": False
    }

    path = Path(config_path)

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

        for key, value in default_config.items():
            config.setdefault(key, value)

        return config

    return default_config


def apply_header_to_page(page, template_doc, header_height, erase_height, header_y):
    template_page = template_doc[0]
    page_width = page.rect.width

    erase_rect = fitz.Rect(0, 0, page_width, erase_height)

    page.draw_rect(
        erase_rect,
        color=(1, 1, 1),
        fill=(1, 1, 1),
        overlay=True
    )

    target_rect = fitz.Rect(
        0,
        header_y,
        page_width,
        header_y + header_height
    )

    source_rect = fitz.Rect(
        0,
        0,
        template_page.rect.width,
        header_height
    )

    page.show_pdf_page(
        target_rect,
        template_doc,
        0,
        clip=source_rect,
        overlay=True
    )


def convert_pdf_file(
    input_pdf_path,
    output_pdf_path,
    config_path="config.json",
    template_path="ShippingForm.pdf"
):
    config = load_config(config_path)

    cm_to_point = 28.3465

    header_height = config["header_height_cm"] * cm_to_point
    erase_height = config["erase_height_cm"] * cm_to_point
    header_y = config["header_y_cm"] * cm_to_point
    apply_to_all_pages = config.get("apply_to_all_pages", False)

    customer_doc = fitz.open(str(input_pdf_path))
    template_doc = fitz.open(str(template_path))

    if apply_to_all_pages:
        for page in customer_doc:
            apply_header_to_page(
                page,
                template_doc,
                header_height,
                erase_height,
                header_y
            )
    else:
        apply_header_to_page(
            customer_doc[0],
            template_doc,
            header_height,
            erase_height,
            header_y
        )

    customer_doc.save(str(output_pdf_path))
    customer_doc.close()
    template_doc.close()

    return str(output_pdf_path)
