import random

from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.bot_texts import DATA_PER_PAGE, EMOJI_SET
from data.config import ADMIN_IDS
from handlers.admin.menu import show_admin_menu
from handlers.admin.router import admin_router
from services.order_service import get_stats, get_all_orders, get_items_for_order, get_orders_page, get_orders_count


@admin_router.callback_query(F.data == "admin_stats")
async def callback_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    c, t = get_stats()
    txt = f"📊 Статистика:\n📦 Замовлень: {c}\n💰 Сума: {t}"

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(txt)
    await show_admin_menu(callback.message)

    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin_list_orders_page:"))
async def callback_list_orders(callback: CallbackQuery):
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

    await show_orders_page(callback.message, page)

    await callback.answer()


@admin_router.callback_query(F.data == "admin_back")
async def callback_back(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    try:
        await callback.message.delete()
    except:
        pass

    await show_admin_menu(callback.message)

    await callback.answer()


@admin_router.callback_query(F.data == "admin_exit")
async def callback_exit(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer("👋 Вихід з адмін-меню.")

    await callback.answer()


async def show_orders_page(message: Message, page: int):
    orders_emoji = random.choice(EMOJI_SET["orders"])

    page_size = DATA_PER_PAGE
    page_orders = get_orders_page(page, page_size)
    total = get_orders_count()

    total_pages = (total + page_size - 1) // page_size

    kb = InlineKeyboardBuilder()
    text = f"📦 *Всі замовлення* {orders_emoji}\n"
    text += f"_Сторінка {page + 1} з {total_pages}_\n\n"

    if not page_orders:
        text += "📭 На цій сторінці немає замовлень."
    else:
        for o in page_orders:
            status_emoji = "✅" if o['payment_status'] == "paid" else "⚠️"
            delivery_emoji = random.choice(["🚚", "🚛", "📦"])

            text += (
                f"*№{o['id']}* {delivery_emoji}\n"
                f"👤 *Клієнт:* {o['full_name']}\n"
                f"📞 `{o['phone']}`\n"
                f"📍 _{o['address']}_\n\n"
                f"💰 *Сума:* {o['total_price']} грн\n"
                f"💳 *Оплата:* {o['payment_method']} ({status_emoji} {o['payment_status']})\n"
                f"💳 *Коментар:* {o['comment']}\n"
                f"📅 _{o['created_at']}_\n"
            )

            items = get_items_for_order(o["id"])
            if items:
                text += "🛍️ *Товари:*\n"
                for it in items:
                    subtotal = it["product_price"] * it["quantity"]
                    text += f"  • {it['product_name']} x {it['quantity']} = {subtotal} грн\n"

            text += "\n" + "─" * 25 + "\n\n"

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"admin_list_orders_page:{page - 1}"
        ))

    if (page + 1) * page_size < total:
        nav_buttons.append(InlineKeyboardButton(
            text="➡️ Вперед",
            callback_data=f"admin_list_orders_page:{page + 1}"
        ))

    if nav_buttons:
        kb.row(*nav_buttons)

    kb.row(
        InlineKeyboardButton(
            text="🔄 Оновити",
            callback_data=f"admin_list_orders_page:{page}"
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