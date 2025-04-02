from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from .feedback import start_feedback
from .router import contact_router
from data.bot_texts import CONTACT_TITLE


@contact_router.message(Command("contact"))
async def cmd_contact(message: Message):
    await show_contact_menu(message)

@contact_router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext):
    await start_feedback(message, state)

@contact_router.message(F.text == "📞 Зв'язатися з нами")
async def text_contact(message: Message):
    await show_contact_menu(message)


@contact_router.callback_query(F.data == "contact_menu")
async def callback_contact_menu(callback: CallbackQuery):
    await show_contact_menu(callback.message)
    await callback.answer()


@contact_router.callback_query(F.data == "show_contacts")
async def callback_show_contacts(callback: CallbackQuery):
    await show_contacts_info(callback.message)
    await callback.answer()


async def show_contact_menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Довідник по боту", callback_data="help_guide")],
        [InlineKeyboardButton(text="💬 Залишити відгук", callback_data="leave_feedback")],
        [InlineKeyboardButton(text="📞 Контакти", callback_data="show_contacts")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_main")]
    ])

    await message.answer(f"<b>{CONTACT_TITLE}</b>\n\nОберіть опцію:", parse_mode="HTML", reply_markup=kb)


async def show_contacts_info(message: Message):
    from data.bot_texts import CONTACT_INFO

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