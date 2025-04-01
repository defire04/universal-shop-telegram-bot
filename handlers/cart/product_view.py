
from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.cart.router  import cart_router, temp_quantities, user_carts
from keyboards.inline import make_main_menu
from services.product_service import get_product


@cart_router.callback_query(F.data.startswith("viewprod:"))
async def callback_view_product(callback: CallbackQuery):
    pid = int(callback.data.split(":")[1])
    product = get_product(pid)

    if not product:
        await callback.answer("Товар не знайдено.")
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
        await callback.answer("Товар не знайдено.")
        return

    if action == "inc":
        qty += 1
        temp_quantities[key] = qty
        await callback.answer(f"Кількість: {qty}")
        await send_updated_product_view(callback.message, product, qty)

    elif action == "dec":
        if qty > 1:
            qty -= 1
            temp_quantities[key] = qty
            await callback.answer(f"Кількість: {qty}")
            await send_updated_product_view(callback.message, product, qty)
        else:
            await callback.answer("Мінімальна кількість 1")

    elif action == "add":
        if callback.from_user.id not in user_carts:
            user_carts[callback.from_user.id] = {}

        if pid not in user_carts[callback.from_user.id]:
            user_carts[callback.from_user.id][pid] = 0

        user_carts[callback.from_user.id][pid] += qty
        temp_quantities.pop(key, None)

        await callback.answer(f"Додано в кошик x{qty}")

        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer("Товар додано до кошика!", reply_markup=make_main_menu())


async def send_product_view(message: Message, product: dict, qty: int):
    brand = product['brand']
    caption = f"<b>{product['name']}</b> ({brand})\nЦіна: {product['price']} грн\n\nКількість: {qty}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="–", callback_data=f"qty:dec:{product['id']}"),
            InlineKeyboardButton(text=str(qty), callback_data="none"),
            InlineKeyboardButton(text="+", callback_data=f"qty:inc:{product['id']}")
        ],
        [InlineKeyboardButton(text="Додати в кошик", callback_data=f"qty:add:{product['id']}")],
        [InlineKeyboardButton(text="Назад", callback_data=f"back_to_brand:{brand}")]
    ])

    if product['photo_url']:
        await message.answer_photo(product['photo_url'], caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(caption, parse_mode="HTML", reply_markup=kb)


async def send_updated_product_view(message: Message, product: dict, qty: int):
    try:
        await message.delete()
    except:
        pass
    await send_product_view(message, product, qty)