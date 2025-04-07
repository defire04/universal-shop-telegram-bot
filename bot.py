import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from data.config import BOT_TOKEN
from data.db import init_db
from handlers.admin import admin_router
from handlers.ai import ai_router
from handlers.cart import cart_router
from handlers.contact import contact_router
from handlers.fallback import fallback_router
from handlers.user import user_router

logging.basicConfig(level=logging.INFO)


async def main():
    init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties())

    dp = Dispatcher()

    dp.include_router(ai_router)
    dp.include_router(cart_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(contact_router)
    dp.include_router(fallback_router)



    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
