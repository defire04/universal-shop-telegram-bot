import random

from aiogram.filters import Command
from aiogram.types import Message

from data.bot_texts import GREETING_MESSAGE, EMOJI_SET
from keyboards.reply import main_reply_keyboard
from services.user_service import ensure_user_exists
from .router import user_router


@user_router.message(Command("start"))
async def cmd_start(message: Message):
    user_fullname = (message.from_user.first_name or '') + ' ' + (message.from_user.last_name or '')
    user_fullname = user_fullname.strip()

    ensure_user_exists(message.from_user.id, user_fullname)

    final_text = GREETING_MESSAGE.format(emoji=random.choice(EMOJI_SET['success']))

    await message.answer(
        final_text,
        parse_mode="Markdown",
        reply_markup=main_reply_keyboard(message.from_user.id),
    )