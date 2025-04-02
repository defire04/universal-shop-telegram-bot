from aiogram import F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from .router import contact_router
from data.bot_texts import HELP_MESSAGE

@contact_router.callback_query(F.data == "help_guide")
async def callback_help_guide(callback: CallbackQuery):
    await callback.message.answer(HELP_MESSAGE, parse_mode="Markdown")
    await callback.answer()

@contact_router.message(Command("help"))
async def handle_help_command(message: Message):
    await message.answer(HELP_MESSAGE, parse_mode="Markdown")