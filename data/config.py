import os



BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = os.getenv("DB_PATH") if os.getenv("DB_PATH") else "data/database2.db"

ADMIN_IDS = [int(os.getenv("ADMIN_IDS"))] if os.getenv("ADMIN_IDS") else [int("")]
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")