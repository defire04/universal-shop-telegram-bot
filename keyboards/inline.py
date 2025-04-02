from typing import List, Dict, Any

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def make_main_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏍️ Каталог", callback_data="menu_catalog")],
            [InlineKeyboardButton(text="🛒 Кошик", callback_data="menu_cart")],
            [InlineKeyboardButton(text="📦 Оформити замовлення", callback_data="menu_order")],
            [InlineKeyboardButton(text="📞 Зв'язатися з нами", callback_data="contact_menu")]
        ]
    )
    return keyboard


def make_brand_menu(brands: List[str]) -> InlineKeyboardMarkup:
    buttons = []

    for brand in brands:
        buttons.append([InlineKeyboardButton(text=brand, callback_data=f"brand:{brand}")])

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="go_main")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def make_products_list(products: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []

    brand = products[0]['brand'] if products else ""

    for product in products:
        buttons.append([
            InlineKeyboardButton(
                text=f"{product['name']} - {product['price']} грн",
                callback_data=f"viewprod:{product['id']}"
            )
        ])

    buttons.append([InlineKeyboardButton(text="🔙 Назад до брендів", callback_data="menu_catalog")])
    buttons.append([InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_main")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)