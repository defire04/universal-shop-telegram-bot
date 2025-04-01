import random

from aiogram.filters import Command
from aiogram.types import Message

from keyboards.reply import main_reply_keyboard
from services.user_service import ensure_user_exists
from .router import user_router, GREETINGS, EMOJI_SET


@user_router.message(Command("start"))
async def cmd_start(message: Message):
    user_fullname = (message.from_user.first_name or '') + ' ' + (message.from_user.last_name or '')
    user_fullname = user_fullname.strip()

    ensure_user_exists(message.from_user.id, user_fullname)

    greeting_emoji = random.choice(EMOJI_SET["greeting"])
    await message.answer(greeting_emoji)

    greet = random.choice(GREETINGS).format(user_fullname, random.choice(EMOJI_SET["greeting"]))

    text = f"{greet}\n\n"
    text += f"Ласкаво просимо до нашого магазину квадроциклів! {random.choice(EMOJI_SET['catalog'])}\n"
    text += "Тут ти можеш переглянути наші квадроцикли, додати товар до кошика та оформити замовлення.\n"
    text += f"\nГотовий до пригод? Почнімо! {random.choice(EMOJI_SET['success'])}"

    await message.answer(
        text,
        reply_markup=main_reply_keyboard(message.from_user.id)
    )
