from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from data.bot_texts import FEEDBACK_THANKS, CONTACT_INFO, CONTACT_TITLE, HELP_MESSAGE, FEEDBACK_TITLE
from handlers.contact import contact_router
from services.feedback_service import save_new_feedback


class FeedbackStates(StatesGroup):
    waiting_for_message = State()


@contact_router.message(Command("contact"))
async def cmd_contact(message: Message):
    await show_contact_menu(message)


@contact_router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext):
    await start_feedback(message, state)


@contact_router.message(F.text == "Зв'язатися з нами")
async def text_contact(message: Message):
    await show_contact_menu(message)


@contact_router.callback_query(F.data == "contact_menu")
async def callback_contact_menu(callback: CallbackQuery):
    await show_contact_menu(callback.message)
    await callback.answer()


@contact_router.callback_query(F.data == "help_guide")
async def callback_help_guide(callback: CallbackQuery):
    await callback.message.answer(HELP_MESSAGE, parse_mode="Markdown")
    await callback.answer()


@contact_router.callback_query(F.data == "leave_feedback")
async def callback_leave_feedback(callback: CallbackQuery, state: FSMContext):
    await start_feedback(callback.message, state)
    await callback.answer()


@contact_router.callback_query(F.data == "show_contacts")
async def callback_show_contacts(callback: CallbackQuery):
    await show_contacts_info(callback.message)
    await callback.answer()


@contact_router.message(FeedbackStates.waiting_for_message)
async def process_feedback(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    feedback_text = message.text

    save_new_feedback(user_id, username, full_name, feedback_text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_main")]
    ])

    await message.answer(FEEDBACK_THANKS, reply_markup=kb)
    await state.clear()


async def show_contact_menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Довідник по боту", callback_data="help_guide")],
        [InlineKeyboardButton(text="💬 Залишити відгук", callback_data="leave_feedback")],
        [InlineKeyboardButton(text="📞 Контакти", callback_data="show_contacts")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_main")]
    ])

    await message.answer(f"<b>{CONTACT_TITLE}</b>\n\nОберіть опцію:", parse_mode="HTML", reply_markup=kb)


async def show_contacts_info(message: Message):
    contact_text = f"<b>📞 Наші контакти</b>\n\n"
    contact_text += f"☎️ Телефон: {CONTACT_INFO['phone']}\n"
    contact_text += f"📧 Email: {CONTACT_INFO['email']}\n"
    contact_text += f"📍 Адреса: {CONTACT_INFO['address']}\n"
    contact_text += f"🕙 Графік роботи: {CONTACT_INFO['work_hours']}\n\n"

    contact_text += "<b>Соціальні мережі:</b>\n"
    contact_text += f"📸 Instagram: {CONTACT_INFO['social']['instagram']}\n"
    contact_text += f"📘 Facebook: {CONTACT_INFO['social']['facebook']}\n"
    contact_text += f"📱 Telegram: {CONTACT_INFO['social']['telegram']}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="contact_menu")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_main")]
    ])

    await message.answer(contact_text, parse_mode="HTML", reply_markup=kb)


async def start_feedback(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="contact_menu")]
    ])

    await message.answer(
        f"<b>{FEEDBACK_TITLE}</b>\n\n"
        f"Напишіть ваш відгук або повідомлення для нас. "
        f"Ми цінуємо вашу думку і відповімо якнайшвидше!",
        parse_mode="HTML",
        reply_markup=kb
    )

    await state.set_state(FeedbackStates.waiting_for_message)