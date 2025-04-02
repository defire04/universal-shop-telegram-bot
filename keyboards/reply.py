from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data.config import ADMIN_IDS


def main_reply_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="🏠 Головне меню"),
            KeyboardButton(text="🏍️ Каталог")
        ],
        [
            KeyboardButton(text="🛒 Переглянути кошик"),
            KeyboardButton(text="📋 Мої замовлення")
        ],
        [
            KeyboardButton(text="📞 Зв'язатися з нами")
        ]
    ]

    if user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="⚙️ Адмін-меню")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )