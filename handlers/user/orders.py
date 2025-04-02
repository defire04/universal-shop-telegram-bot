import random

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.bot_texts import EMOJI_SET, NAVIGATION_EMOJI, DATA_PER_PAGE
from keyboards.reply import main_reply_keyboard
from services.order_service import get_user_orders, get_items_for_order
from .router import user_router


@user_router.message(Command("orders"))
async def cmd_orders(message: Message):
    await show_orders(message, message.from_user.id)


@user_router.message(F.text == "📋 Мої замовлення")
async def show_user_orders(message: Message):
    await show_orders(message, message.from_user.id)


@user_router.callback_query(F.data.startswith("orders_page:"))
async def process_orders_page(callback: CallbackQuery):
    page = int(callback.data.split(":", 1)[1])

    try:
        await callback.message.delete()
    except Exception:
        pass

    await show_orders(callback.message, callback.from_user.id, page)
    await callback.answer()


async def show_orders(message: Message, user_id: int, page: int = 0):
    orders = get_user_orders(user_id)
    orders_emoji = random.choice(EMOJI_SET["orders"])

    if not orders:
        encouraging_emoji = random.choice(['😊', '🙂', '😉', '🤗'])
        catalog_emoji = random.choice(EMOJI_SET['catalog'])

        await message.answer(
            f"У тебе поки немає замовлень {encouraging_emoji}.\n\n"
            f"Час зробити своє перше замовлення! {catalog_emoji} "
            f"Переглянь наш каталог - там багато цікавого! {random.choice(['✨', '🔥', '💫'])}",
            reply_markup=main_reply_keyboard(user_id)
        )
        return

    total_pages = (len(orders) + DATA_PER_PAGE - 1) // DATA_PER_PAGE
    start_idx = page * DATA_PER_PAGE
    end_idx = min(start_idx + DATA_PER_PAGE, len(orders))
    current_orders = orders[start_idx:end_idx]

    kb = InlineKeyboardBuilder()

    nav_buttons = []
    if page > 0:
        nav_buttons.append((f"{NAVIGATION_EMOJI[0]} Назад", f"orders_page:{page - 1}"))

    if page < total_pages - 1:
        nav_buttons.append((f"Далі {NAVIGATION_EMOJI[1]}", f"orders_page:{page + 1}"))

    for button_text, callback_data in nav_buttons:
        kb.button(text=button_text, callback_data=callback_data)

    if nav_buttons:
        kb.adjust(len(nav_buttons))

    kb.row(
        InlineKeyboardBuilder().button(
            text="🏠 Повернутися в головне меню",
            callback_data="go_main"
        ).as_markup().inline_keyboard[0][0]
    )

    header_emojis = [random.choice(['📦', '🧾', '🛍️', '🛒', '🏆']) for _ in range(len(current_orders))]

    txt = f"💼 *Твої замовлення* {orders_emoji}\n"
    txt += f"_Сторінка {page + 1} з {total_pages}_\n\n"

    for i, order in enumerate(current_orders):
        order_emoji = header_emojis[i]
        delivery_method = order['delivery_method'] if order['delivery_method'] else 'Не вказано'
        payment_status = "✅ Сплачено" if order['payment_status'] == "paid" else "⏳ Очікує оплати"

        txt += f"*№{order['id']}* {order_emoji}\n"
        txt += f"📅 Дата: _{order['created_at']}_\n"
        txt += f"💰 Сума: *{order['total_price']}* грн\n"
        txt += f"🚚 Доставка: _{delivery_method}_\n"
        txt += f"💳 Статус: {payment_status}\n\n"

        items = get_items_for_order(order["id"])
        if items:
            txt += "📝 *Товари:*\n"
            for item in items:
                subtotal = item["product_price"] * item["quantity"]
                txt += f"  • {item['product_name']} x {item['quantity']} = {subtotal} грн\n"

        if i < len(current_orders) - 1:
            txt += "\n" + "─" * 20 + "\n\n"

    motivation_emoji = random.choice(EMOJI_SET["success"])
    txt += f"\n🙏 Дякуємо за довіру до нашого магазину! {motivation_emoji}"

    await message.answer(
        txt,
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
