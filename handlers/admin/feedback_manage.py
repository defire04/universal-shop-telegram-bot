import random

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.bot_texts import EMOJI_SET, DATA_PER_PAGE
from data.config import ADMIN_IDS
from handlers.admin.router import admin_router
from services.feedback_service import get_feedback_page, get_feedback_count


@admin_router.callback_query(F.data == "admin_list_feedback")
async def callback_list_feedback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    try:
        await callback.message.delete()
    except:
        pass

    await show_feedback_page(callback.message, 0)

    await callback.answer()


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

    kb = InlineKeyboardBuilder()
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
            text += "\n" + "─" * 25 + "\n\n"

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",  # Fixed direction
            callback_data=f"admin_list_feedback_page:{page - 1}"
        ))

    if (page + 1) * page_size < total_count:
        nav_buttons.append(InlineKeyboardButton(
            text="➡️ Вперед",  # Fixed direction
            callback_data=f"admin_list_feedback_page:{page + 1}"
        ))

    if nav_buttons:
        kb.row(*nav_buttons)

    kb.row(
        InlineKeyboardButton(
            text="🔄 Оновити",
            callback_data=f"admin_list_feedback_page:{page}"
        )
    )

    kb.row(InlineKeyboardButton(
        text="🔙 В адмін-меню",
        callback_data="admin_back"
    ))

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
