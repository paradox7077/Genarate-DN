import streamlit as st
import fitz
import tempfile
import json
from pathlib import Path

st.set_page_config(page_title="DN Header Replacer", layout="centered")

ADMIN_PASSWORD = "7077"

CONFIG_PATH = Path("config.json")
TEMPLATE_PATH = Path("ShippingForm.pdf")


def load_config():
    default_config = {
        "header_height_cm": 4.5,
        "erase_height_cm": 8.0,
        "header_y_cm": 0.0
    }

    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return default_config


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def convert_pdf(uploaded_pdf, config):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_pdf.read())
        input_pdf_path = temp_file.name

    cm_to_point = 28.3465

    header_height = config["header_height_cm"] * cm_to_point
    erase_height = config["erase_height_cm"] * cm_to_point
    header_y = config["header_y_cm"] * cm_to_point

    customer_doc = fitz.open(input_pdf_path)
    template_doc = fitz.open(str(TEMPLATE_PATH))

    customer_page = customer_doc[0]
    template_page = template_doc[0]

    page_width = customer_page.rect.width

    erase_rect = fitz.Rect(0, 0, page_width, erase_height)
    customer_page.draw_rect(
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

    customer_page.show_pdf_page(
        target_rect,
        template_doc,
        0,
        clip=source_rect,
        overlay=True
    )

    output_path = "converted_dn.pdf"
    customer_doc.save(output_path)
    customer_doc.close()
    template_doc.close()

    return output_path


config = load_config()

st.title("Delivery Note Header Replacer")
st.write("Upload PDF แล้วระบบจะเปลี่ยนหัวบิลให้อัตโนมัติ")

if not TEMPLATE_PATH.exists():
    st.error("ไม่พบไฟล์ ShippingForm.pdf")
    st.stop()

uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_pdf:
    if st.button("Convert PDF", type="primary"):
        output_path = convert_pdf(uploaded_pdf, config)

        with open(output_path, "rb") as f:
            st.success("สร้าง PDF สำเร็จ")
            st.download_button(
                label="Download PDF",
                data=f,
                file_name="converted_dn.pdf",
                mime="application/pdf"
            )

st.divider()

with st.expander("⚙ Admin"):
    password = st.text_input("Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Admin mode")

        header_height_cm = st.slider(
            "ความสูงหัวบริษัทที่นำมาวาง",
            2.0,
            10.0,
            float(config["header_height_cm"]),
            0.1
        )

        erase_height_cm = st.slider(
            "ความสูงพื้นที่ลบหัวเดิม",
            2.0,
            15.0,
            float(config["erase_height_cm"]),
            0.1
        )

        header_y_cm = st.slider(
            "ขยับหัวบริษัทขึ้น/ลง",
            -3.0,
            3.0,
            float(config["header_y_cm"]),
            0.1
        )

        if st.button("Save Setting"):
            new_config = {
                "header_height_cm": header_height_cm,
                "erase_height_cm": erase_height_cm,
                "header_y_cm": header_y_cm
            }

            save_config(new_config)
            st.success("บันทึกค่าเรียบร้อย กรุณา Refresh หน้าเว็บ 1 ครั้ง")

    elif password:
        st.error("Password ไม่ถูกต้อง")