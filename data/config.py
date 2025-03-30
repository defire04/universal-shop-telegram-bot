
import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "TOKEN")
print(BOT_TOKEN)
DB_PATH = os.getenv("DB_PATH", "/data/database.db")
print(DB_PATH)
ADMIN_IDS = [int(os.getenv("ADMIN_IDS"))] if os.getenv("ADMIN_IDS") else []
print(ADMIN_IDS)
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")

print(PAYMENT_TOKEN)