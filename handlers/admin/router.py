from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from data.config import ADMIN_IDS
from handlers.admin.menu import show_admin_menu

admin_router = Router()


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return


    await show_admin_menu(message)