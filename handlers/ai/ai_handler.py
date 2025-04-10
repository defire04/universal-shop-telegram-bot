import random

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.bot_texts import (
    AI_HELPER_WELCOME, AI_HELPER_THINKING,
    AI_HELPER_ERROR, AI_MEDIA_NOT_SUPPORTED, AI_CONTEXT_LIMIT_ERROR
)
from services.ai.ai_service import clear_user_context, ask_ai
from .router import ai_router

from handlers.user.main_menu import show_main_menu
from handlers.user.catalog import show_catalog_logic
from handlers.cart.cart_management import show_cart
from handlers.user.orders import show_user_orders
from handlers.contact.contact_menu import text_contact
from handlers.user.admin_access import access_admin_menu


class AIAssistantStates(StatesGroup):
    waiting_for_question = State()


def get_ai_keyboard():
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
    return kb.as_markup()


@ai_router.message(F.text == "🤖 AI помічник")
async def start_ai_assistant(message: Message, state: FSMContext):
    ai_emoji = random.choice(["🤖", "🧠", "💬", "🔍"])
    user_id = message.from_user.id

    clear_user_context(user_id)

    await message.answer(
        AI_HELPER_WELCOME.format(ai_emoji=ai_emoji),
        parse_mode="Markdown",
        reply_markup=get_ai_keyboard()
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

@ai_router.message(AIAssistantStates.waiting_for_question, F.photo | F.document | F.video | F.voice | F.audio | F.sticker | F.animation)
async def handle_media_message(message: Message, state: FSMContext):
    await message.answer(
        AI_MEDIA_NOT_SUPPORTED,
        parse_mode="Markdown",
        reply_markup=get_ai_keyboard()
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

    thinking_message = await message.answer(AI_HELPER_THINKING)

    try:
        ai_response = await ask_ai(user_id, message.text)


        await thinking_message.delete()
        await message.answer(ai_response, parse_mode="Markdown", reply_markup=get_ai_keyboard())

    except Exception as e:
        error_str = str(e).lower()

        if "can't find end of the entity" in error_str or "context limit" in error_str or "limit exceed" in error_str:
            await message.answer(
                AI_CONTEXT_LIMIT_ERROR,
                parse_mode="Markdown",
                reply_markup=get_ai_keyboard()
            )
            clear_user_context(user_id)
        else:
            await message.answer(
                AI_HELPER_ERROR,
                parse_mode="Markdown",
                reply_markup=get_ai_keyboard()
            )

        print(f"AI Assistant error for user {user_id}: {str(e)}")