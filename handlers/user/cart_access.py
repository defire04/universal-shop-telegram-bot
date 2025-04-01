import random

from aiogram import F
from aiogram.types import Message

from .router import user_router, EMOJI_SET
from ..cart.cart_management import show_cart


@user_router.message(F.text == "Переглянути кошик")
async def access_cart(message: Message):
    """Handle the 'Переглянути кошик' button press"""
    cart_emoji = random.choice(EMOJI_SET["cart"])
    await show_cart(message)