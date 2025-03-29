import random

import telebot
from telebot.types import Message, CallbackQuery

import handlers.cart as cart
from data.config import ADMIN_IDS
from keyboards.inline import make_main_menu, make_products_list, make_brand_menu
from keyboards.reply import main_reply_keyboard
from services.order_service import get_user_orders, get_items_for_order
from services.product_service import get_all_brands, list_products_by_brand
from services.user_service import ensure_user_exists

FRIENDLY_STICKER_ID = "👋"


def register_user_menu(bot: telebot.TeleBot):
    greetings = [
        "Привіт, {}! Радий тебе бачити!",
        "Вітаю, {}! Сподіваюся, у тебе все добре!",
    ]

    @bot.message_handler(commands=['start'])
    def cmd_start(message: Message):
        user_fullname = (message.from_user.first_name or '') + ' ' + (message.from_user.last_name or '')
        user_fullname = user_fullname.strip()
        ensure_user_exists(message.from_user.id, user_fullname)

        try:
            bot.send_sticker(message.chat.id, FRIENDLY_STICKER_ID)
        except:
            pass

        greet = random.choice(greetings).format(user_fullname)
        text = greet + "\nТут ти можеш переглянути каталог, додати товари в кошик і оформити замовлення."

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=main_reply_keyboard(message.from_user.id)
        )

    @bot.message_handler(func=lambda m: m.text in [
        "Головне меню",
        "Каталог",
        "Переглянути кошик",
        "Мої замовлення",
        "Адмін-меню"
    ])
    def on_reply_menu(message: Message):
        if message.text == "Головне меню":
            bot.send_message(
                message.chat.id,
                "Обери, що хочеш зробити:",
                reply_markup=make_main_menu()
            )

        elif message.text == "Каталог":
            brands = get_all_brands()
            if not brands:
                bot.send_message(
                    message.chat.id,
                    "Зараз товари відсутні. Повернись пізніше або запитай щось іще!",
                    reply_markup=main_reply_keyboard(message.from_user.id)
                )
                return
            kb = telebot.types.InlineKeyboardMarkup()
            for b in brands:
                kb.add(telebot.types.InlineKeyboardButton(b, callback_data=f"brand:{b}"))
            kb.add(telebot.types.InlineKeyboardButton("Назад", callback_data="go_main"))
            bot.send_message(
                message.chat.id,
                "Ось наші бренди. Обирай, будь ласка:",
                reply_markup=kb
            )

        elif message.text == "Переглянути кошик":
            cart.show_cart(bot, message.from_user.id, message.chat.id)



        elif message.text == "Мої замовлення":
            orders = get_user_orders(message.from_user.id)
            if not orders:
                bot.send_message(
                    message.chat.id,
                    "У тебе поки немає замовлень. Може, зазирнемо в каталог?",
                    reply_markup=main_reply_keyboard(message.from_user.id)
                )

            else:

                txt = "Ось твої попередні замовлення:\n"

                for o in orders:

                    payment_method = o.get('payment_method', 'Не вказано')

                    payment_status = o.get('payment_status', 'Не вказано')

                    # Format payment status more user-friendly

                    if payment_status == "paid":

                        payment_status = "Оплачено"

                    elif payment_status == "pending":

                        payment_status = "Очікується"

                    txt += f"№{o['id']} | сума {o['total_price']} грн | {payment_method} ({payment_status}) | {o['created_at']}\n"

                    items = get_items_for_order(o["id"])

                    if items:

                        txt += "Товари:\n"

                        for it in items:
                            subtotal = it["product_price"] * it["quantity"]

                            txt += f"  {it['product_name']} x {it['quantity']} = {subtotal} грн\n"

                    txt += "--------------------------------\n"

                txt += "\nЯкщо маєш питання, пиши нам!"

                bot.send_message(

                    message.chat.id,

                    txt,

                    reply_markup=main_reply_keyboard(message.from_user.id))

        elif message.text == "Адмін-меню":
            if message.from_user.id in ADMIN_IDS:
                from handlers.admin_menu import show_admin_menu
                show_admin_menu(bot, message.chat.id)
            else:
                bot.send_message(message.chat.id, "Недостатньо прав.")

    @bot.callback_query_handler(func=lambda call: call.data in ["menu_cart", "menu_order", "go_main"])
    def callback_main_menu(call: CallbackQuery):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        if call.data == "menu_cart":
            cart.show_cart(bot, call.from_user.id, call.message.chat.id)

        elif call.data == "menu_order":
            cart.confirm_order(bot, call)

        elif call.data == "go_main":
            bot.send_message(
                call.message.chat.id,
                "Головне меню:",
                reply_markup=make_main_menu()
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("brand:"))
    def on_choose_brand(call: CallbackQuery):
        brand = call.data.split(":", 1)[1]
        products = list_products_by_brand(brand)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        if not products:
            bot.send_message(
                call.message.chat.id,
                f"Поки що товарів бренду {brand} немає.",
                reply_markup=main_reply_keyboard(call.from_user.id)
            )
            return
        kb = make_products_list(products)
        bot.send_message(
            call.message.chat.id,
            f"Товари бренду {brand}:",
            reply_markup=kb
        )

    @bot.callback_query_handler(func=lambda call: call.data == "menu_catalog")
    def on_menu_catalog(call: CallbackQuery):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        b = get_all_brands()
        if not b:
            bot.send_message(
                call.message.chat.id,
                "Товари відсутні.",
                reply_markup=main_reply_keyboard(call.from_user.id)
            )
            return
        kb = make_brand_menu(b)
        bot.send_message(
            call.message.chat.id,
            "Будь ласка, оберіть бренд:",
            reply_markup=kb
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_brand:"))
    def on_back_to_brand(call: CallbackQuery):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        brand = call.data.split(":", 1)[1]
        products = list_products_by_brand(brand)
        if not products:
            bot.send_message(
                call.message.chat.id,
                f"Поки що товарів бренду {brand} немає.",
            )
            return

        kb = make_products_list(products)
        bot.send_message(
            call.message.chat.id,
            f"Товари бренду {brand}:",
            reply_markup=kb
        )
