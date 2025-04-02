import random
from aiogram import F
from aiogram.types import Message

from .router import user_router
from data.bot_texts import EMOJI_SET
from data.config import ADMIN_IDS
from ..admin.menu import show_admin_menu


@user_router.message(F.text == "⚙️ Адмін-меню")
async def access_admin_menu(message: Message):
    admin_emoji = random.choice(EMOJI_SET["admin"])

    if message.from_user.id in ADMIN_IDS:
        await show_admin_menu(message)
    else:
        await message.answer(
            f"Недостатньо прав для доступу до адмін-меню {random.choice(['🔒', '⛔', '🚫'])}.\n"
            f"Ця функція доступна лише для адміністраторів {admin_emoji}."
        )