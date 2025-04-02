import re
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, \
    PreCheckoutQuery

from data.config import PAYMENT_TOKEN
from handlers.cart.router import cart_router
from handlers.cart.states import OrderStates, user_carts
from keyboards.inline import make_main_menu
from services.order_service import create_new_order_ext
from services.product_service import get_product


@cart_router.callback_query(F.data.startswith("delivery:"))
async def handle_delivery_method(callback: CallbackQuery, state: FSMContext):
    method = callback.data.split(":", 1)[1]

    await state.update_data(delivery_method=method)

    try:
        await callback.message.delete()
    except:
        pass

    if method == "samov":
        await state.update_data(address="Самовивіз")
        await show_payment_options(callback.message, state)
    elif method == "cur":
        await callback.message.answer(
            "📍 Вкажіть адресу для доставки кур'єром:\n\n<i>Приклад: м. Київ, вул. Хрещатик, 1, кв. 10</i>",
            parse_mode="HTML")
        await state.set_state(OrderStates.address)
    elif method == "nova":
        await callback.message.answer(
            "📮 Вкажіть номер відділення Нової Пошти:\n\n<i>Приклад: 33, 45, 100</i>",
            parse_mode="HTML")
        await state.set_state(OrderStates.address)
    elif method == "ukr":
        await callback.message.answer(
            "📮 Вкажіть номер відділення УкрПошти:\n\n<i>Приклад: 01001, 79000</i>",
            parse_mode="HTML")
        await state.set_state(OrderStates.address)

    await callback.answer()

@cart_router.message(OrderStates.address)
async def handle_address(message: Message, state: FSMContext):
    address = message.text.strip()
    data = await state.get_data()
    delivery_method = data.get("delivery_method", "")

    if delivery_method == "cur":
        if len(address) < 10:
            await message.answer(
                "❌ Адреса занадто коротка. Будь ласка, вкажіть повну адресу доставки.\n\n<i>Приклад: м. Київ, вул. Хрещатик, 1, кв. 10</i>",
                parse_mode="HTML")
            return
    elif delivery_method == "nova":
        if not re.search(r'\d+', address):
            await message.answer(
                "❌ Необхідно вказати числовий номер відділення Нової Пошти.\n\n<i>Приклад: 33, 45, 100</i>",
                parse_mode="HTML")
            return
    elif delivery_method == "ukr":
        if not re.search(r'\d+', address):
            await message.answer(
                "❌ Необхідно вказати числовий номер відділення або індекс УкрПошти.\n\n<i>Приклад: 01001, 79000</i>",
                parse_mode="HTML")
            return

    await state.update_data(address=address)
    await show_payment_options(message, state)






async def show_payment_options(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Оплатити зараз", callback_data="payment:now"),
            InlineKeyboardButton(text="💵 Оплатити при отриманні", callback_data="payment:later")
        ]
    ])

    await message.answer("💰 Оберіть спосіб оплати:", reply_markup=kb)
    await state.set_state(OrderStates.payment_method)


@cart_router.callback_query(F.data.startswith("payment:"))
async def handle_payment_method(callback: CallbackQuery, state: FSMContext):
    method = callback.data.split(":", 1)[1]
    await state.update_data(payment_method=method)

    try:
        await callback.message.delete()
    except:
        pass

    if method == "later":
        await finalize_order(callback.from_user.id, callback.message, state)
    else:
        await process_payment(callback.from_user.id, callback.message, state)

    await callback.answer()


async def process_payment(user_id: int, message: Message, state: FSMContext):
    cart = user_carts.get(user_id, {})
    if not cart:
        await message.answer("🛒 Кошик порожній. Замовлення скасовано.", reply_markup=make_main_menu())
        await state.clear()
        return

    total = 0
    cart_description = []

    for pid, qty in cart.items():
        product = get_product(pid)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            cart_description.append(f"{product['name']} x {qty}")

    await state.update_data(payment_amount=total)

    prices = [LabeledPrice(label="Замовлення", amount=int(total * 100))]

    try:
        await message.bot.send_invoice(
            chat_id=user_id,
            title="🛍️ Оплата замовлення",
            description="\n".join(cart_description[:20]) + ("\n..." if len(cart_description) > 20 else ""),
            payload=f"order_{user_id}_{int(total * 100)}",
            provider_token=PAYMENT_TOKEN,
            currency="UAH",
            prices=prices,
            max_tip_amount=5000,
            suggested_tip_amounts=[500, 1000, 2000],
            start_parameter="payment",
            protect_content=True
        )
    except Exception as e:
        await message.answer(
            f"❌ Помилка при створенні платежу: {str(e)}\nСпробуйте пізніше або виберіть інший спосіб оплати.")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💵 Оплатити при отриманні", callback_data="payment:later")]
        ])
        await message.answer("💡 Ви можете обрати оплату при отриманні:", reply_markup=kb)


@cart_router.pre_checkout_query()
async def process_pre_checkout(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)


@cart_router.message(F.successful_payment)
async def process_successful_payment(message: Message, state: FSMContext):
    await state.update_data(payment_status="paid")
    await finalize_order(message.from_user.id, message, state)


async def finalize_order(user_id: int, message: Message, state: FSMContext):
    cart = user_carts.get(user_id, {})
    if not cart:
        await message.answer("🛒 Кошик порожній. Замовлення скасовано.", reply_markup=make_main_menu())
        await state.clear()
        return

    data = await state.get_data()
    phone = data.get("phone", "")
    comment = data.get("comment", "")
    full_name = data.get("full_name", "")
    delivery_method = data.get("delivery_method", "")
    address = data.get("address", "")
    payment_method = data.get("payment_method", "")
    payment_status = data.get("payment_status", "pending")

    if payment_method == "later":
        payment_status = "pending"

    order_id = create_new_order_ext(
        user_id, cart,
        delivery_method, address,
        phone, comment,
        full_name, payment_method, payment_status
    )

    user_carts[user_id] = {}
    await state.clear()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="go_main")],
        [InlineKeyboardButton(text="💬 Залишити відгук", callback_data="leave_feedback")]
    ])

    from data.bot_texts import ORDER_SUCCESS, ORDER_PAID_SUCCESS

    if payment_status == "paid":
        await message.answer(
            ORDER_PAID_SUCCESS.format(order_id=order_id),
            reply_markup=kb
        )
    else:
        await message.answer(
            ORDER_SUCCESS.format(order_id=order_id),
            reply_markup=kb
        )


async def confirm_order(callback: CallbackQuery, state: FSMContext):
    cart = user_carts.get(callback.from_user.id, {})
    if not cart:
        await callback.answer("🛒 Кошик порожній.")

        from keyboards.inline import make_main_menu
        await callback.message.answer(
            "🛒 Ваш кошик порожній. Спочатку додайте товари до кошика.",
            reply_markup=make_main_menu()
        )
        return

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer("👤 Вкажіть ваше повне ім'я (ПІБ):\n\n<i>Приклад: Шевченко Тарас Григорович</i>",
                                  parse_mode="HTML")
    await state.set_state(OrderStates.full_name)
    await callback.answer()


@cart_router.message(OrderStates.full_name)
async def process_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    name_parts = full_name.split()
    if len(name_parts) < 3:
        await message.answer("❌ Необхідно вказати прізвище, ім'я та по батькові.\n\n<i>Приклад: Шевченко Тарас Григорович</i>",
                           parse_mode="HTML")
        return

    await state.update_data(full_name=full_name)

    await message.answer("📱 Вкажіть ваш номер телефону:\n\n<i>Приклад: +380501234567 або 0501234567</i>",
                       parse_mode="HTML")
    await state.set_state(OrderStates.phone)


@cart_router.message(OrderStates.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    digits = ''.join(re.findall(r'\d', phone))

    if not (
            (digits.startswith('380') and len(digits) == 12) or
            (digits.startswith('0') and len(digits) == 10)
    ):
        await message.answer(
            "❌ Некоректний формат телефону. Номер має починатися з +380 або 0 та містити 10-12 цифр.\n\n"
            "<i>Приклад: +380501234567 або 0501234567</i>",
            parse_mode="HTML"
        )
        return

    if digits.startswith('0'):
        normalized_phone = "+38" + digits
    elif digits.startswith('380'):
        normalized_phone = "+" + digits
    else:
        normalized_phone = phone

    await state.update_data(phone=normalized_phone)

    await message.answer("💬 Якщо маєте коментар до замовлення, напишіть тут (або введіть «-» чи «Немає»):")
    await state.set_state(OrderStates.comment)


@cart_router.message(OrderStates.comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text.strip()

    if comment.lower() in ['-', 'немає', 'нет', 'no', 'none']:
        comment = "-"

    await state.update_data(comment=comment)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Нова Пошта", callback_data="delivery:nova"),
            InlineKeyboardButton(text="📮 УкрПошта", callback_data="delivery:ukr")
        ],
        [
            InlineKeyboardButton(text="🚚 Кур'єрська доставка", callback_data="delivery:cur"),
            InlineKeyboardButton(text="🏪 Самовивіз", callback_data="delivery:samov")
        ]
    ])

    await message.answer("🚚 Оберіть спосіб доставки:", reply_markup=kb)
    await state.set_state(OrderStates.delivery_method)