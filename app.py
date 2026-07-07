import json
from pathlib import Path

import streamlit as st

from converter import convert_pdf_file, load_config
from database import get_next_job_no, create_job


st.set_page_config(
    page_title="EGGMall Document Converter",
    page_icon="📄",
    layout="centered"
)

# ซ่อนเมนู Streamlit มุมขวาบน + footer
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


CONFIG_PATH = Path("config.json")
TEMPLATE_PATH = Path("ShippingForm.pdf")
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

ADMIN_PASSWORD = "7077"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def main():
    config = load_config(CONFIG_PATH)

    st.title("EGGMall Document Converter")
    st.write("Upload PDF เพื่อเปลี่ยนหัวเอกสารอัตโนมัติ")

    if not TEMPLATE_PATH.exists():
        st.error("ไม่พบไฟล์ ShippingForm.pdf")
        st.stop()

    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_pdf:
        if st.button("Convert PDF", type="primary"):
            try:
                job_no = get_next_job_no()

                input_path = UPLOAD_DIR / f"{job_no}_Source.pdf"
                output_path = OUTPUT_DIR / f"{job_no}.pdf"

                with open(input_path, "wb") as f:
                    f.write(uploaded_pdf.read())

                convert_pdf_file(
                    input_pdf_path=input_path,
                    output_pdf_path=output_path,
                    config_path=CONFIG_PATH,
                    template_path=TEMPLATE_PATH
                )

                create_job(
                    job_no=job_no,
                    original_file_name=uploaded_pdf.name,
                    upload_path=str(input_path),
                    output_path=str(output_path),
                    status="Success"
                )

                with open(output_path, "rb") as f:
                    st.success(f"สร้างไฟล์สำเร็จ: {job_no}.pdf")
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=f"{job_no}.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")

    st.divider()

    with st.expander("Admin"):
        password = st.text_input("Password", type="password")

        if password == ADMIN_PASSWORD:
            st.success("Admin mode")

            header_height_cm = st.slider(
                "ความสูงหัวบริษัทที่นำมาวาง",
                2.0,
                10.0,
                float(config.get("header_height_cm", 4.5)),
                0.1
            )

            erase_height_cm = st.slider(
                "ความสูงพื้นที่ลบหัวเดิม",
                2.0,
                15.0,
                float(config.get("erase_height_cm", 8.0)),
                0.1
            )

            header_y_cm = st.slider(
                "ขยับหัวบริษัทขึ้น/ลง",
                -3.0,
                3.0,
                float(config.get("header_y_cm", 0.0)),
                0.1
            )

            apply_mode = st.radio(
                "ต้องการทับหัวบิลหน้าไหน",
                ["หน้าแรกเท่านั้น", "ทุกหน้า"],
                index=1 if config.get("apply_to_all_pages", False) else 0
            )

            if st.button("Save Setting"):
                new_config = {
                    "header_height_cm": header_height_cm,
                    "erase_height_cm": erase_height_cm,
                    "header_y_cm": header_y_cm,
                    "apply_to_all_pages": apply_mode == "ทุกหน้า"
                }

                save_config(new_config)
                st.success("บันทึกค่าเรียบร้อยแล้ว กรุณา Refresh หน้าเว็บ 1 ครั้ง")

        elif password:
            st.error("Password ไม่ถูกต้อง")


if __name__ == "__main__":
    main()
