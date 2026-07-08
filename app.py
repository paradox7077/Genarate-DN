import json
from pathlib import Path

import streamlit as st

from converter import load_config
from document_service import process_document


st.set_page_config(
    page_title="EGGMall Document Converter",
    page_icon="📄",
    layout="centered"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stDecoration"] {visibility: hidden;}
[data-testid="stStatusWidget"] {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


CONFIG_PATH = Path("config.json")
TEMPLATE_PATH = Path("ShippingForm.pdf")


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
                with st.status("กำลังดำเนินการ...", expanded=True) as status:
                    st.write("📥 กำลังรับไฟล์ต้นฉบับ...")
                    st.write("☁️ กำลังบันทึกไฟล์ต้นฉบับลง Google Drive...")
                    st.write("🧾 กำลังแปลงเอกสาร...")
                    st.write("☁️ กำลังบันทึกไฟล์ผลลัพธ์ลง Google Drive...")
                    st.write("📊 กำลังบันทึกข้อมูลลง Google Sheet...")

                    result = process_document(
                        uploaded_file=uploaded_pdf,
                        config_path=CONFIG_PATH,
                        template_path=TEMPLATE_PATH,
                        source="Web"
                    )

                    status.update(label="ดำเนินการสำเร็จ", state="complete")

                st.success(f"สร้างไฟล์สำเร็จ: {result['output_file_name']}")

                with open(result["output_path"], "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=result["output_file_name"],
                        mime="application/pdf"
                    )

                st.info(f"Google Drive Folder: {result['folder_link']}")

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")

    st.divider()

    with st.expander("Admin"):
        password = st.text_input("Password", type="password")

        if password == config.get("admin_password", "7077"):
            st.success("Admin mode")

            company_name = st.text_input(
                "Company Name",
                value=config.get("company_name", "EGGMall")
            )

            file_prefix = st.text_input(
                "File Prefix",
                value=config.get("file_prefix", "EG"),
                max_chars=5
            )

            admin_password = st.text_input(
                "Admin Password",
                value=config.get("admin_password", "7077"),
                type="password"
            )

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
                    **config,
                    "company_name": company_name,
                    "file_prefix": file_prefix.upper().strip() or "EG",
                    "admin_password": admin_password,
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
