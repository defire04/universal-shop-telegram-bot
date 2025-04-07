import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("QUAD_BOT_TOKEN", "")
DB_PATH = os.getenv("DB_PATH") if os.getenv("DB_PATH") else "data/database2.db"

admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id_str) for id_str in admin_ids_str.split(",") if id_str] if admin_ids_str else []
PAYMENT_TOKEN = os.getenv("QUAD_PAYMENT_TOKEN", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
