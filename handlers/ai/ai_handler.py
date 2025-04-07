import random

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.bot_texts import (
    AI_HELPER_WELCOME, AI_HELPER_THINKING,
    AI_HELPER_ERROR
)
from services.ai_service import ask_gemini
from services.product_service import get_top_products, list_all_products
from .router import ai_router


class AIAssistantStates(StatesGroup):
    """Стани для роботи з AI асистентом"""
    waiting_for_question = State()


@ai_router.message(F.text == "🤖 AI помічник")
async def start_ai_assistant(message: Message, state: FSMContext):
    """Початок роботи з AI помічником"""
    ai_emoji = random.choice(["🤖", "🧠", "💬", "🔍"])

    # Отримуємо рекомендовані товари
    top_products = get_top_products(3)

    # Створюємо клавіатуру з рекомендаціями, якщо є товари
    keyboard = None
    if top_products:
        kb = InlineKeyboardBuilder()

        # Додаємо кнопки з топ товарами
        for product in top_products:
            kb.button(
                text=f"🔍 {product['name']} - {product['price']} грн",
                callback_data=f"viewprod:{product['id']}"
            )

        # Додаємо кнопку для каталогу
        kb.button(
            text="📋 Переглянути каталог",
            callback_data="menu_catalog"
        )

        # Розміщуємо кнопки по одній в рядку
        kb.adjust(1)
        keyboard = kb.as_markup()

    # Використовуємо текст з bot_texts.py
    await message.answer(
        AI_HELPER_WELCOME.format(ai_emoji=ai_emoji),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    # Встановлюємо стан очікування питання
    await state.set_state(AIAssistantStates.waiting_for_question)


@ai_router.message(Command("ai"))
async def cmd_ai_assistant(message: Message, state: FSMContext):
    """Обробка команди /ai"""
    await start_ai_assistant(message, state)


@ai_router.message(AIAssistantStates.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    """Обробка питання користувача для AI"""
    # Перевіряємо, чи не натиснув користувач кнопку меню для виходу
    if message.text and message.text in [
        "🏠 Головне меню", "🏍️ Каталог", "🛒 Переглянути кошик",
        "📋 Мої замовлення", "📞 Зв'язатися з нами", "⚙️ Адмін-меню"
    ]:
        # Скидаємо стан і виходимо з режиму AI
        await state.clear()
        return

    # Надсилаємо індикатор набору тексту
    await message.answer(AI_HELPER_THINKING)

    try:
        # Звертаємося до Gemini API
        ai_response = await ask_gemini(message.text)

        # Додаємо кнопки для навігації по каталогу, якщо питання пов'язане з товарами
        product_keywords = ['квадроцикл', 'товар', 'модель', 'ціна', 'каталог', 'бренд']
        has_product_question = any(keyword in message.text.lower() for keyword in product_keywords)

        keyboard = None
        if has_product_question:
            kb = InlineKeyboardBuilder()

            # Додаємо кнопку для каталогу
            kb.button(
                text="📋 Переглянути каталог",
                callback_data="menu_catalog"
            )

            # Отримуємо всі бренди
            products = list_all_products()
            brands = list(set([p['brand'] for p in products]))[:5]  # Максимум 5 брендів

            # Додаємо кнопки брендів
            for brand in brands:
                kb.button(
                    text=f"🏍️ {brand}",
                    callback_data=f"brand:{brand}"
                )

            # Розміщуємо кнопки по одній в рядку
            kb.adjust(1)
            keyboard = kb.as_markup()

        # Якщо відповідь занадто довга, розбиваємо її на частини
        if len(ai_response) > 4000:
            chunks = [ai_response[i:i + 4000] for i in range(0, len(ai_response), 4000)]
            for i, chunk in enumerate(chunks):
                # Додаємо кнопки тільки до останньої частини
                if i == len(chunks) - 1:
                    await message.answer(chunk, parse_mode="Markdown", reply_markup=keyboard)
                else:
                    await message.answer(chunk, parse_mode="Markdown")
        else:
            await message.answer(ai_response, parse_mode="Markdown", reply_markup=keyboard)

    except Exception as e:
        # У випадку помилки виводимо повідомлення про помилку
        await message.answer(AI_HELPER_ERROR)
        print(f"AI Assistant error: {str(e)}")
