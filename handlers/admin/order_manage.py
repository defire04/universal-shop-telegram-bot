from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from data.config import ADMIN_IDS
from handlers.admin.menu import show_admin_menu
from handlers.admin.router import admin_router
from services.order_service import get_stats, get_all_orders, get_items_for_order


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
    page_size = 5
    orders = get_all_orders()
    total = len(orders)
    start = page * page_size
    end = start + page_size
    page_orders = orders[start:end]

    if not page_orders:
        text = "📭 Немає замовлень на цій сторінці."
    else:
        text = f"📄 Сторінка {page + 1} із {((total - 1) // page_size) + 1}\n\n"
        for o in page_orders:
            text += (
                f"📦 Замовлення №{o['id']}\n"
                f"👤 Ім'я: {o['full_name']}\n"
                f"💰 Сума: {o['total_price']}\n"
                f"🚚 Доставка: {o['delivery_method']}\n"
                f"📍 Адреса: {o['address']}\n"
                f"📞 Телефон: {o['phone']}\n"
                f"💬 Коментар: {o['comment']}\n"
                f"💳 Спосіб оплати: {o['payment_method']}\n"
                f"🧾 Статус оплати: {o['payment_status']}\n"
                f"📅 Дата: {o['created_at']}\n"
            )

            items = get_items_for_order(o["id"])
            if items:
                text += "🛍️ Товари:\n"
                for it in items:
                    subtotal = it["product_price"] * it["quantity"]
                    text += f"  {it['product_name']} x {it['quantity']} = {subtotal}\n"
            text += "--------------------------------\n"

    buttons = []
    if page > 0:
        buttons.append([
            InlineKeyboardButton(text="⬅️ Попередня", callback_data=f"admin_list_orders_page:{page - 1}")
        ])

    if end < total:
        buttons.append([
            InlineKeyboardButton(text="➡️ Наступна", callback_data=f"admin_list_orders_page:{page + 1}")
        ])

    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=kb)
