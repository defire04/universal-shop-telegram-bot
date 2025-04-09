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

# Import all required handlers at the module level
from handlers.user.main_menu import show_main_menu
from handlers.user.catalog import show_catalog_logic
from handlers.cart.cart_management import show_cart
from handlers.user.orders import show_user_orders
from handlers.contact.contact_menu import text_contact
from handlers.user.admin_access import access_admin_menu


class AIAssistantStates(StatesGroup):
    waiting_for_question = State()


@ai_router.message(F.text == "🤖 AI помічник")
async def start_ai_assistant(message: Message, state: FSMContext):
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


@ai_router.message(AIAssistantStates.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    user_id = message.from_user.id

    menu_handlers = {
        "🏠 Головне меню": lambda: show_main_menu(message),
        "🏍️ Каталог": lambda: show_catalog_logic(message),
        "🛒 Переглянути кошик": lambda: show_cart(message, user_id),
        "📋 Мої замовлення": lambda: show_user_orders(message),
        "📞 Зв'язатися з нами": lambda: text_contact(message),
        "⚙️ Адмін-меню": lambda: access_admin_menu(message)
    }

    if message.text in menu_handlers:
        await state.clear()
        handler = menu_handlers[message.text]
        return await handler()

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