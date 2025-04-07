from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.cart.cart_management import show_cart
from handlers.cart.router import cart_router
from handlers.cart.states import user_carts, temp_quantities
from services.product_service import get_product, get_next_prev_products


@cart_router.callback_query(F.data.startswith("viewprod:"))
async def callback_view_product(callback: CallbackQuery):
    pid = int(callback.data.split(":")[1])
    product = get_product(pid)

    if not product:
        await callback.answer("❌ Товар не знайдено.")
        return

    temp_quantities[(callback.from_user.id, pid)] = 1

    try:
        await callback.message.delete()
    except:
        pass

    await send_product_view(callback.message, product, 1)
    await callback.answer()


@cart_router.callback_query(F.data.startswith("qty:"))
async def callback_change_quantity(callback: CallbackQuery):
    parts = callback.data.split(":")
    action = parts[1]
    pid = int(parts[2])
    key = (callback.from_user.id, pid)

    if key not in temp_quantities:
        temp_quantities[key] = 1

    qty = temp_quantities[key]
    product = get_product(pid)

    if not product:
        await callback.answer("❌ Товар не знайдено.")
        return

    if action == "inc":
        qty += 1
        temp_quantities[key] = qty
        await callback.answer(f"🔢 Кількість: {qty}")
        await send_updated_product_view(callback.message, product, qty)

    elif action == "dec":
        if qty > 1:
            qty -= 1
            temp_quantities[key] = qty
            await callback.answer(f"🔢 Кількість: {qty}")
            await send_updated_product_view(callback.message, product, qty)
        else:
            await callback.answer("⚠️ Мінімальна кількість - 1")

    elif action == "add":
        if callback.from_user.id not in user_carts:
            user_carts[callback.from_user.id] = {}

        if pid not in user_carts[callback.from_user.id]:
            user_carts[callback.from_user.id][pid] = 0

        user_carts[callback.from_user.id][pid] += qty
        temp_quantities.pop(key, None)

        await callback.answer(f"✅ Додано в кошик x{qty}")

        try:
            await callback.message.delete()
        except:
            pass

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Перейти до кошика", callback_data="cart_view")],
            [InlineKeyboardButton(text="🔙 Продовжити покупки", callback_data="go_main")]
        ])

        await callback.message.answer("✅ Товар успішно додано до кошика!", reply_markup=kb)


@cart_router.callback_query(F.data == "cart_view")
async def show_cart_callback(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    await show_cart(callback.message, callback.from_user.id)
    await callback.answer()


@cart_router.callback_query(F.data.startswith("nav_product:"))
async def navigate_products(callback: CallbackQuery):
    pid = int(callback.data.split(":")[1])
    product = get_product(pid)

    if not product:
        await callback.answer("❌ Товар не знайдено.")
        return

    key = (callback.from_user.id, pid)
    if key not in temp_quantities:
        temp_quantities[key] = 1

    try:
        await callback.message.delete()
    except:
        pass

    await send_product_view(callback.message, product, temp_quantities[key])
    await callback.answer()


async def send_product_view(message: Message, product: dict, qty: int):
    brand = product['brand']
    price = product['price']
    total_price = price * qty

    prev_id, next_id = get_next_prev_products(product['id'], brand)

    caption = f"<b>🛍️ {product['name']}</b>\n"
    caption += f"<i>Бренд: {brand}</i>\n\n"
    description = product['description']
    if description:
        caption += f"📝 <b>Опис:</b>\n{description}\n\n"

    caption += f"💰 Ціна: <b>{price} грн</b>\n"
    caption += f"🔢 Кількість: <b>{qty}</b>\n"
    caption += f"💵 Загалом: <b>{total_price} грн</b>"

    keyboard = [
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"nav_product:{prev_id}"),
            InlineKeyboardButton(text=f"{brand}", callback_data=f"back_to_brand:{brand}"),
            InlineKeyboardButton(text="➡️", callback_data=f"nav_product:{next_id}")
        ],
        [
            InlineKeyboardButton(text="➖", callback_data=f"qty:dec:{product['id']}"),
            InlineKeyboardButton(text=f"{qty} шт", callback_data="none"),
            InlineKeyboardButton(text="➕", callback_data=f"qty:inc:{product['id']}")
        ],
        [InlineKeyboardButton(text="🛒 Додати в кошик", callback_data=f"qty:add:{product['id']}")],
        [InlineKeyboardButton(text="🔙 Повернутись до каталогу", callback_data=f"back_to_brand:{brand}")]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if product['photo_url']:
        await message.answer_photo(product['photo_url'], caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(caption, parse_mode="HTML", reply_markup=kb)


async def send_updated_product_view(message: Message, product: dict, qty: int):
    await send_product_view(message, product, qty)
    try:
        await message.delete()
    except:
        pass
