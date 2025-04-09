import random

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.bot_texts import (
    AI_HELPER_WELCOME, AI_HELPER_THINKING,
    AI_HELPER_ERROR
)
from services.ai.ai_service import clear_user_context, ask_ai
from .router import ai_router


class AIAssistantStates(StatesGroup):
    """Стани для роботи з AI асистентом"""
    waiting_for_question = State()


@ai_router.message(F.text == "🤖 AI помічник")
async def start_ai_assistant(message: Message, state: FSMContext):
    """Початок роботи з AI помічником"""
    ai_emoji = random.choice(["🤖", "🧠", "💬", "🔍"])
    user_id = message.from_user.id

    clear_user_context(user_id)

    kb = InlineKeyboardBuilder()
    kb.button(
        text="📋 Переглянути каталог",
        callback_data="menu_catalog"
    )
    kb.button(
        text="🔄 Очистити історію розмови",
        callback_data="ai_clear_context"
    )
    kb.adjust(1)
    keyboard = kb.as_markup()

    # Используем текст с bot_texts.py
    await message.answer(
        AI_HELPER_WELCOME.format(ai_emoji=ai_emoji),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await state.set_state(AIAssistantStates.waiting_for_question)


@ai_router.message(Command("ai"))
async def cmd_ai_assistant(message: Message, state: FSMContext):
    await start_ai_assistant(message, state)


@ai_router.callback_query(F.data == "ai_clear_context")
async def clear_ai_context(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    clear_user_context(user_id)

    await callback_query.answer("✅ Історію розмови очищено")
    await callback_query.message.answer(
        "✅ Історію нашої розмови було очищено. Тепер ми можемо почати спілкування з чистого аркушу."
    )


@ai_router.callback_query(F.data == "menu_catalog")
async def ai_to_catalog(callback_query: CallbackQuery, state: FSMContext):
    # Просто очищаем состояние AI и отвечаем на callback
    await state.clear()
    await callback_query.answer()

    try:
        # Вызываем напрямую нужный обработчик, а не полагаемся на роутинг
        from handlers.user.catalog import show_catalog_logic
        await show_catalog_logic(callback_query.message)
        await callback_query.message.delete()
    except Exception as e:
        print(f"Error in menu navigation: {str(e)}")


@ai_router.message(AIAssistantStates.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text == "🏠 Головне меню":
        await state.clear()
        from handlers.user.main_menu import show_main_menu
        return await show_main_menu(message)

    if message.text == "🏍️ Каталог":
        await state.clear()
        from handlers.user.catalog import show_catalog_logic
        return await show_catalog_logic(message)

    if message.text == "🛒 Переглянути кошик":
        await state.clear()
        from handlers.cart.cart_management import show_cart
        return await show_cart(message, user_id)

    if message.text == "📋 Мої замовлення":
        await state.clear()
        from handlers.user.orders import show_user_orders
        return await show_user_orders(message)

    if message.text == "📞 Зв'язатися з нами":
        await state.clear()
        from handlers.contact.contact_menu import text_contact
        return await text_contact(message)

    if message.text == "⚙️ Адмін-меню":
        await state.clear()
        from handlers.user.admin_access import access_admin_menu
        return await access_admin_menu(message)

    await message.answer(AI_HELPER_THINKING)

    try:
        ai_response = await ask_ai(user_id, message.text)

        kb = InlineKeyboardBuilder()
        kb.button(
            text="📋 Переглянути каталог",
            callback_data="menu_catalog"
        )
        kb.button(
            text="🔄 Очистити історію розмови",
            callback_data="ai_clear_context"
        )
        kb.adjust(1)
        keyboard = kb.as_markup()

        if len(ai_response) > 1000:
            chunks = [ai_response[i:i + 1000] for i in range(0, len(ai_response), 1000)]
            for i, chunk in enumerate(chunks):
                if i == len(chunks) - 1:
                    await message.answer(chunk, parse_mode="Markdown", reply_markup=keyboard)
                else:
                    await message.answer(chunk, parse_mode="Markdown")
        else:
            await message.answer(ai_response, parse_mode="Markdown", reply_markup=keyboard)

    except Exception as e:
        error_message = f"{AI_HELPER_ERROR}\n\nПомилка: {str(e)}"
        await message.answer(error_message)

        clear_user_context(user_id)

        await message.answer("🔄 Історію розмови було автоматично очищено через помилку.")

        print(f"AI Assistant error: {str(e)}")