import random

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.bot_texts import EMOJI_SET, NAVIGATION_EMOJI, ORDERS_PER_PAGE
from keyboards.reply import main_reply_keyboard
from services.order_service import get_user_orders, get_items_for_order
from .router import user_router


@user_router.message(Command("orders"))
async def cmd_orders(message: Message):
    await show_orders_logic(message)


@user_router.message(F.text == "📋 Мої замовлення")
async def show_user_orders(message: Message):
    await show_orders_logic(message)


async def show_orders_logic(message: Message, page: int = 0):
    orders = get_user_orders(message.from_user.id)
    orders_emoji = random.choice(EMOJI_SET["orders"])

    if not orders:
        encouraging_emoji = random.choice(['😊', '🙂', '😉', '🤗'])
        catalog_emoji = random.choice(EMOJI_SET['catalog'])

        await message.answer(
            f"У тебе поки немає замовлень {encouraging_emoji}.\n\n"
            f"Час зробити своє перше замовлення! {catalog_emoji} "
            f"Переглянь наш каталог - там багато цікавого! {random.choice(['✨', '🔥', '💫'])}",
            reply_markup=main_reply_keyboard(message.from_user.id)
        )
        return

    # Расчет пагинации
    total_pages = (len(orders) + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE
    start_idx = page * ORDERS_PER_PAGE
    end_idx = min(start_idx + ORDERS_PER_PAGE, len(orders))
    current_orders = orders[start_idx:end_idx]

    # Создаем клавиатуру для навигации
    kb = InlineKeyboardBuilder()

    if page > 0:
        kb.button(text=f"{NAVIGATION_EMOJI[0]} Назад", callback_data=f"orders_page:{page - 1}")

    if total_pages > 1:
        kb.button(text=f"{page + 1}/{total_pages} {NAVIGATION_EMOJI[2]}", callback_data="orders_refresh")

    if page < total_pages - 1:
        kb.button(text=f"Далі {NAVIGATION_EMOJI[1]}", callback_data=f"orders_page:{page + 1}")

    kb.adjust(2)  # Размещаем кнопки по 2 в ряд

    # Формируем текст сообщения
    header_emojis = [random.choice(['📦', '🧾', '🛍️', '🛒', '🏆']) for _ in range(len(current_orders))]

    txt = f"💼 *Твої замовлення* {orders_emoji}\n"
    txt += f"_Сторінка {page + 1} з {total_pages}_\n\n"

    for i, order in enumerate(current_orders):
        order_emoji = header_emojis[i]
        # Правильное обращение к полям в словаре заказа
        delivery_method = order['delivery_method'] if 'delivery_method' in order else 'Не вказано'
        payment_status = "✅ Оплачено" if order['payment_status'] == "paid" else "⏳ Очікує оплати"

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

    # Отправляем сообщение с клавиатурой
    await message.answer(
        txt,
        parse_mode="Markdown",
        reply_markup=kb.as_markup() if total_pages > 1 else None
    )


@user_router.callback_query(F.data.startswith("orders_page:"))
async def process_orders_page(callback: CallbackQuery):
    page = int(callback.data.split(":", 1)[1])

    try:
        await callback.message.delete()
    except Exception:
        pass

    # Вызываем с передачей правильного user_id
    await show_orders_logic_with_user_id(callback.message, callback.from_user.id, page)
    await callback.answer()


@user_router.callback_query(F.data == "orders_refresh")
async def refresh_orders(callback: CallbackQuery):
    # Получаем текущую страницу из текста сообщения
    text = callback.message.text
    try:
        current_page = int(text.split("Сторінка ")[1].split(" з")[0]) - 1
    except (IndexError, ValueError):
        current_page = 0

    try:
        await callback.message.delete()
    except Exception:
        pass

    # Вызываем с передачей правильного user_id
    await show_orders_logic_with_user_id(callback.message, callback.from_user.id, current_page)
    await callback.answer(f"Оновлено! {random.choice(['✨', '🔄', '✅'])}")


# Отдельный метод для обработки callback запросов
async def show_orders_logic_with_user_id(message: Message, user_id: int, page: int = 0):
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

    # Расчет пагинации
    total_pages = (len(orders) + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE
    start_idx = page * ORDERS_PER_PAGE
    end_idx = min(start_idx + ORDERS_PER_PAGE, len(orders))
    current_orders = orders[start_idx:end_idx]

    # Создаем клавиатуру для навигации
    kb = InlineKeyboardBuilder()

    if page > 0:
        kb.button(text=f"{NAVIGATION_EMOJI[0]} Назад", callback_data=f"orders_page:{page - 1}")

    if total_pages > 1:
        kb.button(text=f"{page + 1}/{total_pages} {NAVIGATION_EMOJI[2]}", callback_data="orders_refresh")

    if page < total_pages - 1:
        kb.button(text=f"Далі {NAVIGATION_EMOJI[1]}", callback_data=f"orders_page:{page + 1}")

    kb.adjust(2)  # Размещаем кнопки по 2 в ряд

    # Формируем текст сообщения
    header_emojis = [random.choice(['📦', '🧾', '🛍️', '🛒', '🏆']) for _ in range(len(current_orders))]

    txt = f"💼 *Твої замовлення* {orders_emoji}\n"
    txt += f"_Сторінка {page + 1} з {total_pages}_\n\n"

    for i, order in enumerate(current_orders):
        order_emoji = header_emojis[i]
        # Правильное обращение к полям в словаре заказа
        delivery_method = order['delivery_method'] if 'delivery_method' in order else 'Не вказано'
        payment_status = "✅ Оплачено" if order['payment_status'] == "paid" else "⏳ Очікує оплати"

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

    # Отправляем сообщение с клавиатурой
    await message.answer(
        txt,
        parse_mode="Markdown",
        reply_markup=kb.as_markup() if total_pages > 1 else None
    )
