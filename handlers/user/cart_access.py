import random

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message

from .router import user_router
from data.bot_texts import EMOJI_SET
from ..cart.cart_management import show_cart


@user_router.message(F.text == "🛒 Переглянути кошик")
async def access_cart(message: Message):
    cart_emoji = random.choice(EMOJI_SET["cart"])
    await show_cart(message)

@user_router.message(Command("cart"))
async def cmd_cart(message: Message):
    cart_emoji = random.choice(EMOJI_SET["cart"])
    await show_cart(message)