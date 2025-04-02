from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from .router import contact_router
from data.bot_texts import FEEDBACK_THANKS, FEEDBACK_TITLE
from services.feedback_service import save_new_feedback
from .states import FeedbackStates


@contact_router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext):
    await start_feedback(message, state)

@contact_router.callback_query(F.data == "leave_feedback")
async def callback_leave_feedback(callback: CallbackQuery, state: FSMContext):
    await start_feedback(callback.message, state)
    await callback.answer()


@contact_router.message(FeedbackStates.waiting_for_message)
async def process_feedback(message: Message, state: FSMContext):
    state_data = await state.get_data()
    feedback_msg_id = state_data.get("feedback_msg_id")

    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    feedback_text = message.text

    save_new_feedback(user_id, username, full_name, feedback_text)

    if feedback_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, feedback_msg_id)
        except Exception:
            pass

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_main")]
    ])

    await message.answer(FEEDBACK_THANKS, reply_markup=kb)
    await state.clear()


async def start_feedback(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="contact_menu")]
    ])

    feedback_msg = await message.answer(
        f"<b>{FEEDBACK_TITLE}</b>\n\n"
        f"Напишіть ваш відгук або повідомлення для нас. "
        f"Ми цінуємо вашу думку і відповімо якнайшвидше!",
        parse_mode="HTML",
        reply_markup=kb
    )

    await state.update_data(feedback_msg_id=feedback_msg.message_id)
    await state.set_state(FeedbackStates.waiting_for_message)




