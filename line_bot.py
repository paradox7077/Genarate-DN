from fastapi import FastAPI, Request
from linebot.v3.messaging import (
    MessagingApi,
    MessagingApiBlob,
    Configuration,
    ApiClient
)
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FileMessageContent
import os
from pathlib import Path
from datetime import datetime

from converter import convert_pdf_file

app = FastAPI()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

DOWNLOAD_DIR = Path("downloads")
OUTPUT_DIR = Path("outputs")
DOWNLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    return {"status": "LINE Bot is running"}


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")
    handler.handle(body.decode("utf-8"), signature)
    return "OK"


def reply_text(reply_token, text):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text(event):
    reply_text(event.reply_token, "ส่งไฟล์ PDF มาได้เลยครับ ระบบจะเปลี่ยนหัวบิลให้")


@handler.add(MessageEvent, message=FileMessageContent)
def handle_file(event):
    file_name = event.message.file_name
    message_id = event.message.id

    if not file_name.lower().endswith(".pdf"):
        reply_text(event.reply_token, "ระบบรองรับเฉพาะไฟล์ PDF เท่านั้นครับ")
        return

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_path = DOWNLOAD_DIR / f"{timestamp}_{file_name}"
        output_path = OUTPUT_DIR / f"converted_{timestamp}_{file_name}"

        with ApiClient(configuration) as api_client:
            blob_api = MessagingApiBlob(api_client)
            file_content = blob_api.get_message_content(message_id)

        with open(input_path, "wb") as f:
            f.write(file_content)

        convert_pdf_file(
            input_pdf_path=input_path,
            output_pdf_path=output_path,
            config_path="config.json",
            template_path="ShippingForm.pdf"
        )

        file_size_kb = output_path.stat().st_size / 1024

        reply_text(
            event.reply_token,
            f"✅ แปลงไฟล์สำเร็จแล้วครับ\n"
            f"ไฟล์: {output_path.name}\n"
            f"ขนาด: {file_size_kb:.2f} KB\n\n"
            f"ขั้นต่อไปคือทำลิงก์ดาวน์โหลด/ส่งไฟล์กลับ LINE"
        )

    except Exception as e:
        reply_text(event.reply_token, f"❌ แปลงไฟล์ไม่สำเร็จ\nError: {str(e)}")
