from fastapi import FastAPI, Request
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FileMessageContent
)
import os

app = FastAPI()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


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
    reply_text(event.reply_token, "ได้รับข้อความแล้วครับ")


@handler.add(MessageEvent, message=FileMessageContent)
def handle_file(event):
    file_name = event.message.file_name

    if file_name.lower().endswith(".pdf"):
        reply_text(event.reply_token, f"✅ ได้รับไฟล์ PDF แล้วครับ\nไฟล์: {file_name}")
    else:
        reply_text(event.reply_token, "ได้รับไฟล์แล้วครับ แต่ระบบรองรับเฉพาะ PDF")
