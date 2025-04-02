import random

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.bot_texts import EMOJI_SET, DATA_PER_PAGE
from data.config import ADMIN_IDS
from handlers.admin.menu import get_pagination_keyboard
from handlers.admin.router import admin_router
from services.feedback_service import get_feedback_page, get_feedback_count



@admin_router.callback_query(F.data.startswith("admin_list_feedback_page:"))
async def callback_list_feedback_page(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    parts = callback.data.split(":")
    try:
        page = int(parts[1])
    except:
        page = 0

    try:
        await callback.message.delete()
    except:
        pass

    await show_feedback_page(callback.message, page)

    await callback.answer()


async def show_feedback_page(message: Message, page: int):
    feedback_emoji = random.choice(EMOJI_SET.get("feedback", ["📝", "💬", "📊"]))

    page_size = DATA_PER_PAGE
    feedback_items = get_feedback_page(page, page_size)
    total_count = get_feedback_count()

    total_pages = (total_count + page_size - 1) // page_size

    text = f"📝 *Відгуки клієнтів* {feedback_emoji}\n"
    text += f"_Сторінка {page + 1} з {total_pages}_\n\n"

    if not feedback_items:
        text += "📭 На цій сторінці немає відгуків."
    else:
        for f in feedback_items:
            text += (
                f"*№{f['id']}* 👤\n"
                f"👤 *Клієнт:* {f['full_name'] or 'Не вказано'}\n"
                f"👤 *Username:* @{f['username'] or 'Не вказано'}\n"
                f"✍️ *Відгук:* _{f['feedback_text']}_\n"
                f"📅 _{f['created_at']}_\n"
            )
            text += "\n" + "─" * 20 + "\n\n"

    kb = get_pagination_keyboard(
        page=page,
        total_count=total_count,
        page_size=page_size,
        base_callback="admin_list_feedback_page"
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
