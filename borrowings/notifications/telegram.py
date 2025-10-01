import os

import requests
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_telegram_notification(message: str) -> None:

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError(
            "Telegram credentials missing. "
            "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env."
        )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    requests.post(TELEGRAM_API_URL, data=payload)
