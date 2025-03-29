from typing import Dict

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, \
    PreCheckoutQuery

from data.config import PAYMENT_TOKEN
from keyboards.inline import make_main_menu
from services.order_service import create_new_order_ext
from services.product_service import get_product


class OrderStates(StatesGroup):
    full_name = State()
    phone = State()
    comment = State()
    delivery_method = State()
    address = State()
    payment_method = State()


cart_router = Router()

user_carts: Dict[int, Dict[int, int]] = {}
temp_quantities: Dict[tuple, int] = {}
user_flow: Dict[int, Dict[str, str]] = {}


@cart_router.callback_query(F.data.startswith("viewprod:"))
async def callback_view_product(callback: CallbackQuery):
    pid = int(callback.data.split(":")[1])
    product = get_product(pid)

    if not product:
        await callback.answer("Товар не знайдено.")
        return

    temp_quantities[(callback.from_user.id, pid)] = 1

    try:
        await callback.message.delete()
    except:
        pass

    await send_product_view(callback.message, product, 1)
    await callback.answer()


@cart_router.callback_query(F.data.startswith("qty:"))
async def callback_change_quantity(callback: CallbackQuery):
    parts = callback.data.split(":")
    action = parts[1]
    pid = int(parts[2])
    key = (callback.from_user.id, pid)

    if key not in temp_quantities:
        temp_quantities[key] = 1

    qty = temp_quantities[key]
    product = get_product(pid)

    if not product:
        await callback.answer("Товар не знайдено.")
        return

    if action == "inc":
        qty += 1
        temp_quantities[key] = qty
        await callback.answer(f"Кількість: {qty}")
        await send_updated_product_view(callback.message, product, qty)

    elif action == "dec":
        if qty > 1:
            qty -= 1
            temp_quantities[key] = qty
            await callback.answer(f"Кількість: {qty}")
            await send_updated_product_view(callback.message, product, qty)
        else:
            await callback.answer("Мінімальна кількість 1")

    elif action == "add":
        if callback.from_user.id not in user_carts:
            user_carts[callback.from_user.id] = {}

        if pid not in user_carts[callback.from_user.id]:
            user_carts[callback.from_user.id][pid] = 0

        user_carts[callback.from_user.id][pid] += qty
        temp_quantities.pop(key, None)

        await callback.answer(f"Додано в кошик x{qty}")

        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer("Товар додано до кошика!", reply_markup=make_main_menu())


@cart_router.callback_query(F.data == "cart_clear")
async def on_cart_clear(callback: CallbackQuery):
    user_carts[callback.from_user.id] = {}
    await callback.answer("Кошик очищено!")

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer("Кошик очищено.", reply_markup=make_main_menu())


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
        await callback.message.answer("Вкажіть адресу для кур'єра:")
        await state.set_state(OrderStates.address)
    elif method in ["nova", "ukr"]:
        await callback.message.answer("Вкажіть номер відділення:")
        await state.set_state(OrderStates.address)

    await callback.answer()


@cart_router.message(OrderStates.address)
async def handle_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())


    await show_payment_options(message, state)


async def show_payment_options(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Оплатити зараз", callback_data="payment:now"),
            InlineKeyboardButton(text="Оплатити при отриманні", callback_data="payment:later")
        ]
    ])

    await message.answer("Оберіть спосіб оплати:", reply_markup=kb)
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
        await message.answer("Кошик порожній. Скасовано.", reply_markup=make_main_menu())
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
            title="Оплата замовлення",
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
            f"Помилка при створенні платежу: {str(e)}\nСпробуйте пізніше або виберіть інший спосіб оплати.")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатити при отриманні", callback_data="payment:later")]
        ])
        await message.answer("Ви можете обрати оплату при отриманні:", reply_markup=kb)


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
        await message.answer("Кошик порожній. Скасовано.", reply_markup=make_main_menu())
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

    if payment_status == "paid":
        await message.answer(
            f"Вітаю, замовлення №{order_id} оформлено та оплачено! Дякуємо!\n"
            f"Оператор з вами зв'яжеться для уточнення деталей.",
            reply_markup=make_main_menu()
        )
    else:
        await message.answer(
            f"Вітаю, замовлення №{order_id} оформлено! Дякуємо!\n"
            f"Оплата буде проведена при отриманні. Оператор з вами зв'яжеться для уточнення деталей.",
            reply_markup=make_main_menu()
        )


async def show_cart(message: Message, user_id: int = None):
    if user_id is None:
        user_id = message.from_user.id

    cart = user_carts.get(user_id, {})

    if not cart:
        await message.answer("Ваш кошик порожній.", reply_markup=make_main_menu())
        return

    text = "Ваш кошик:\n"
    total = 0

    for pid, qty in cart.items():
        product = get_product(pid)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            text += f"{product['name']} x {qty} = {subtotal} грн\n"

    text += f"\nЗагальна сума: {total} грн"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Очистити кошик", callback_data="cart_clear")],
        [InlineKeyboardButton(text="Оформити замовлення", callback_data="menu_order")],
        [InlineKeyboardButton(text="Назад", callback_data="go_main")]
    ])

    await message.answer(text, reply_markup=kb)


async def send_product_view(message: Message, product: dict, qty: int):
    brand = product['brand']
    caption = f"<b>{product['name']}</b> ({brand})\nЦіна: {product['price']} грн\n\nКількість: {qty}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="–", callback_data=f"qty:dec:{product['id']}"),
            InlineKeyboardButton(text=str(qty), callback_data="none"),
            InlineKeyboardButton(text="+", callback_data=f"qty:inc:{product['id']}")
        ],
        [InlineKeyboardButton(text="Додати в кошик", callback_data=f"qty:add:{product['id']}")],
        [InlineKeyboardButton(text="Назад", callback_data=f"back_to_brand:{brand}")]
    ])

    if product['photo_url']:
        await message.answer_photo(product['photo_url'], caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(caption, parse_mode="HTML", reply_markup=kb)


async def send_updated_product_view(message: Message, product: dict, qty: int):
    try:
        await message.delete()
    except:
        pass
    await send_product_view(message, product, qty)


async def confirm_order(callback: CallbackQuery, state: FSMContext):
    cart = user_carts.get(callback.from_user.id, {})
    if not cart:
        await callback.answer("Кошик порожній.")

        from keyboards.inline import make_main_menu
        await callback.message.answer(
            "Ваш кошик порожній. Спочатку додайте товари до кошика.",
            reply_markup=make_main_menu()
        )
        return

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer("Вкажіть ваше ПІБ (повне ім'я):")
    await state.set_state(OrderStates.full_name)
    await callback.answer()


@cart_router.message(OrderStates.full_name)
async def process_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())

    await message.answer("Вкажіть свій номер телефону:")
    await state.set_state(OrderStates.phone)


@cart_router.message(OrderStates.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())

    await message.answer("Якщо маєте коментар, напишіть тут (або «Немає»):")
    await state.set_state(OrderStates.comment)


@cart_router.message(OrderStates.comment)
async def process_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text.strip())

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Нова Пошта", callback_data="delivery:nova"),
            InlineKeyboardButton(text="УкрПошта", callback_data="delivery:ukr")
        ],
        [
            InlineKeyboardButton(text="Кур'єр", callback_data="delivery:cur"),
            InlineKeyboardButton(text="Самовивіз", callback_data="delivery:samov")
        ]
    ])

    await message.answer("Оберіть спосіб доставки:", reply_markup=kb)
    await state.set_state(OrderStates.delivery_method)