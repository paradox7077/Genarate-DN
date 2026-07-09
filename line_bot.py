import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse

from linebot.v3.messaging import (
    MessagingApi,
    MessagingApiBlob,
    Configuration,
    ApiClient,
)
from linebot.v3.messaging.models import (
    TextMessage,
    ReplyMessageRequest,
    PushMessageRequest,
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FileMessageContent
from linebot.v3.exceptions import InvalidSignatureError

from document_service import process_document


app = FastAPI()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
BASE_URL = os.getenv("BASE_URL", "https://generate-dn-bot.onrender.com")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ให้ Bot ทำงานทีละไฟล์ ลดปัญหาไฟล์ชน / request ชน
executor = ThreadPoolExecutor(max_workers=1)


class LineUploadedFile:
    def __init__(self, name, content: bytes):
        self.name = name
        self._content = content

    def read(self):
        return self._content


@app.get("/")
def home():
    return {"status": "LINE Bot is running"}


@app.get("/download/{file_name}")
def download_file(file_name: str):
    file_path = OUTPUT_DIR / file_name

    if not file_path.exists():
        return {"error": "File not found"}

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/pdf",
    )


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


def get_destination(event):
    source = event.source
    return (
        getattr(source, "group_id", None)
        or getattr(source, "room_id", None)
        or getattr(source, "user_id", None)
    )


def reply_text(reply_token, text):
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        line_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)],
            )
        )


def push_text(destination, text):
    if not destination:
        return

    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        line_api.push_message(
            PushMessageRequest(
                to=destination,
                messages=[TextMessage(text=text)],
            )
        )


def process_line_pdf(message_id, file_name, destination):
    try:
        with ApiClient(configuration) as api_client:
            blob_api = MessagingApiBlob(api_client)
            file_content = blob_api.get_message_content(message_id)

        if not isinstance(file_content, bytes):
            file_content = file_content.read()

        uploaded_file = LineUploadedFile(file_name, file_content)

        result = process_document(
            uploaded_file=uploaded_file,
            config_path="config.json",
            template_path="ShippingForm.pdf",
            source="LINE",
        )

        output_file_name = result["output_file_name"]
        local_output = OUTPUT_DIR / output_file_name

        shutil.copyfile(result["output_path"], local_output)

        download_url = f"{BASE_URL}/download/{output_file_name}"

        push_text(
            destination,
            f"✅ แปลงไฟล์สำเร็จแล้ว\n\n"
            f"Job No: {result['job_no']}\n"
            f"ไฟล์: {output_file_name}\n\n"
            f"ดาวน์โหลดไฟล์:\n{download_url}",
        )

    except Exception as e:
        push_text(
            destination,
            f"❌ แปลงไฟล์ไม่สำเร็จ\n\n"
            f"Error: {str(e)}",
        )


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text(event):
    reply_text(
        event.reply_token,
        "ส่งไฟล์ PDF มาได้เลยครับ ระบบจะเปลี่ยนหัวเอกสารให้",
    )


@handler.add(MessageEvent, message=FileMessageContent)
def handle_file(event):
    file_name = event.message.file_name
    message_id = event.message.id
    destination = get_destination(event)

    if not file_name.lower().endswith(".pdf"):
        reply_text(event.reply_token, "ระบบรองรับเฉพาะไฟล์ PDF เท่านั้นครับ")
        return

    reply_text(
        event.reply_token,
        f"📄 ได้รับไฟล์แล้ว\n"
        f"ไฟล์: {file_name}\n\n"
        f"กำลังแปลงเอกสาร กรุณารอสักครู่ครับ",
    )

    executor.submit(process_line_pdf, message_id, file_name, destination)
