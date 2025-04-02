from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

async def show_admin_menu(message: Message):
    buttons = [
        [InlineKeyboardButton(text="➕ Додати товар", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="📋 Список товарів", callback_data="admin_list_products")],
        [InlineKeyboardButton(text="🗑️ Видалити товар", callback_data="admin_del_product")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📦 Замовлення", callback_data="admin_list_orders_page:0")],
        [InlineKeyboardButton(text="📦 Відгуки", callback_data="admin_list_feedback_page:0")],
        [InlineKeyboardButton(text="🚪 Вийти", callback_data="admin_exit")]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        "👨‍💼 *Адмін-меню*\n"
        "Оберіть опцію:",
        parse_mode="Markdown",
        reply_markup=kb
    )