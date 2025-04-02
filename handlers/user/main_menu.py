import random
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from .router import user_router, EMOJI_SET
from keyboards.inline import make_main_menu
from keyboards.reply import main_reply_keyboard
from ..cart.cart_management import show_cart
from ..cart.order_process import confirm_order


@user_router.message(F.text == "Головне меню")
async def show_main_menu(message: Message):
    await message.answer(
        f"Обери, що хочеш зробити: {random.choice(EMOJI_SET['catalog'])}",
        reply_markup=make_main_menu()
    )


@user_router.callback_query(F.data.in_(["menu_cart", "menu_order", "go_main"]))
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except Exception:
        pass

    if callback.data == "menu_cart":
        await show_cart(callback.message, callback.from_user.id)

    elif callback.data == "menu_order":
        await confirm_order(callback, state)

    elif callback.data == "go_main":
        emoji = random.choice(EMOJI_SET["catalog"])
        await callback.message.answer(
            f"Головне меню {emoji}:",
            reply_markup=make_main_menu()
        )

    await callback.answer()