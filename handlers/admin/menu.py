from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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

def get_pagination_keyboard(page: int, total_count: int, page_size: int, base_callback: str,
                            include_refresh: bool = True):
    kb = InlineKeyboardBuilder()
    total_pages = (total_count + page_size - 1) // page_size

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"{base_callback}:{page - 1}"
        ))

    if (page + 1) * page_size < total_count:
        nav_buttons.append(InlineKeyboardButton(
            text="➡️ Вперед",
            callback_data=f"{base_callback}:{page + 1}"
        ))

    if nav_buttons:
        kb.row(*nav_buttons)

    if include_refresh:
        kb.row(
            InlineKeyboardButton(
                text="🔄 Оновити",
                callback_data=f"{base_callback}:{page}"
            )
        )

    kb.row(InlineKeyboardButton(
        text="🔙 В адмін-меню",
        callback_data="admin_back"
    ))

    return kb



