import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env файле")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не задан в .env файле")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID не задан в .env файле")
