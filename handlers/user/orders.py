import random

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.reply import main_reply_keyboard
from services.order_service import get_user_orders, get_items_for_order
from .router import user_router, EMOJI_SET


@user_router.message(Command("orders"))
async def cmd_orders(message: Message):
    await show_orders_logic(message)


@user_router.message(F.text == "📋 Мої замовлення")
async def show_user_orders(message: Message):
    await show_orders_logic(message)


async def show_orders_logic(message: Message):
    orders = get_user_orders(message.from_user.id)

    orders_emoji = random.choice(EMOJI_SET["orders"])

    if not orders:
        await message.answer(
            f"У тебе поки немає замовлень {random.choice(['😊', '🙂', '😉'])}. "
            f"Може, зазирнемо в каталог? {random.choice(EMOJI_SET['catalog'])}",
            reply_markup=main_reply_keyboard(message.from_user.id)
        )
    else:
        txt = f"Ось твої попередні замовлення {orders_emoji}:\n\n"

        for o in orders:
            txt += f"№{o['id']} | сума {o['total_price']} грн | {o['created_at']} {random.choice(['📦', '🧾', '🛍️'])}\n"
            items = get_items_for_order(o["id"])
            if items:
                txt += "Товари:\n"
                for it in items:
                    subtotal = it["product_price"] * it["quantity"]
                    txt += f"  {it['product_name']} x {it['quantity']} = {subtotal} грн\n"
            txt += "--------------------------------\n"

        success_emoji = random.choice(EMOJI_SET["success"])
        txt += f"\nЯкщо маєш питання щодо своїх замовлень, пиши нам! {success_emoji}"

        await message.answer(
            txt,
            reply_markup=main_reply_keyboard(message.from_user.id)
        )
