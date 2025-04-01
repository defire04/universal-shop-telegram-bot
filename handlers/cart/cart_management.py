from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.cart.router  import cart_router, user_carts
from keyboards.inline import make_main_menu
from services.product_service import get_product


@cart_router.callback_query(F.data == "cart_clear")
async def on_cart_clear(callback: CallbackQuery):
    user_carts[callback.from_user.id] = {}
    await callback.answer("Кошик очищено!")

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer("Кошик очищено.", reply_markup=make_main_menu())


async def show_cart(message: Message, user_id: int = None):
    if user_id is None:
        user_id = message.from_user.id

    cart = user_carts.get(user_id, {})

    if not cart:
        await message.answer("Ваш кошик порожній.", reply_markup=make_main_menu())
        return

    text = "Ваш кошик:\n"
    total = 0

    for pid, qty in cart.items():
        product = get_product(pid)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            text += f"{product['name']} x {qty} = {subtotal} грн\n"

    text += f"\nЗагальна сума: {total} грн"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Очистити кошик", callback_data="cart_clear")],
        [InlineKeyboardButton(text="Оформити замовлення", callback_data="menu_order")],
        [InlineKeyboardButton(text="Назад", callback_data="go_main")]
    ])

    await message.answer(text, reply_markup=kb)