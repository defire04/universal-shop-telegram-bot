from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from data.config import ADMIN_IDS
from services.order_service import get_stats, get_all_orders, get_items_for_order
from services.product_service import add_new_product, remove_product, list_all_products
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_router = Router()


class AdminActions(StatesGroup):
    waiting_for_product_info = State()
    waiting_for_product_id = State()


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    await show_admin_menu(message)


@admin_router.callback_query(F.data.startswith("admin_"))
async def callback_admin(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    action = callback.data

    if action == "admin_add_product":
        await state.set_state(AdminActions.waiting_for_product_info)
        await callback.message.answer("Введіть: Назва|Ціна|Бренд|Фото URL")

        try:
            await callback.message.delete()
        except:
            pass

    elif action == "admin_list_products":
        try:
            await callback.message.delete()
        except:
            pass

        products = list_all_products()
        txt = "Список товарів:\n"

        if not products:
            txt += "Немає товарів."
        else:
            for p in products:
                txt += f"ID {p['id']}: {p['name']} ({p['brand']}) - {p['price']} грн\n"

        await callback.message.answer(txt)
        await show_admin_menu(callback.message)

    elif action == "admin_del_product":
        await state.set_state(AdminActions.waiting_for_product_id)
        await callback.message.answer("Введіть ID товару:")

        try:
            await callback.message.delete()
        except:
            pass

    elif action == "admin_stats":
        c, t = get_stats()
        txt = f"Статистика:\nЗамовлень: {c}\nСума: {t}"

        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer(txt)
        await show_admin_menu(callback.message)

    elif action.startswith("admin_list_orders_page:"):
        parts = action.split(":")
        try:
            page = int(parts[1])
        except:
            page = 0

        try:
            await callback.message.delete()
        except:
            pass

        await show_orders_page(callback.message, page)

    elif action == "admin_back":
        try:
            await callback.message.delete()
        except:
            pass

        await show_admin_menu(callback.message)

    elif action == "admin_exit":
        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer("Вихід з адмін-меню.")

    await callback.answer()


@admin_router.message(AdminActions.waiting_for_product_info)
async def process_add_product(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    arr = message.text.split("|")
    if len(arr) < 4:
        await message.answer("Невірний формат.")
        await show_admin_menu(message)
        await state.clear()
        return

    name = arr[0].strip()
    try:
        price = float(arr[1].strip())
    except ValueError:
        await message.answer("Невірний формат ціни.")
        await show_admin_menu(message)
        await state.clear()
        return

    brand = arr[2].strip()
    photo_url = arr[3].strip()

    add_new_product(name, price, brand, photo_url)
    await message.answer("Товар додано.")
    await show_admin_menu(message)
    await state.clear()


@admin_router.message(AdminActions.waiting_for_product_id)
async def process_del_product(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        pid = int(message.text)
    except ValueError:
        await message.answer("Невірний ID.")
        await show_admin_menu(message)
        await state.clear()
        return

    remove_product(pid)
    await message.answer("Товар видалено.")
    await show_admin_menu(message)
    await state.clear()


async def show_orders_page(message: Message, page: int):
    page_size = 5
    orders = get_all_orders()
    total = len(orders)
    start = page * page_size
    end = start + page_size
    page_orders = orders[start:end]


    if not page_orders:
        text = "Немає замовлень на цій сторінці."
    else:
        text = f"Сторінка {page + 1} із {((total - 1) // page_size) + 1}\n\n"
        for o in page_orders:
            text += (
                f"Замовлення №{o['id']}\n"
                f"Ім'я: {o['full_name']}\n"
                f"Сума: {o['total_price']}\n"
                f"Доставка: {o['delivery_method']}\n"
                f"Адреса: {o['address']}\n"
                f"Телефон: {o['phone']}\n"
                f"Коментар: {o['comment']}\n"
                f"Спосіб оплати: {o['payment_method']}\n"
                f"Статус оплати: {o['payment_status']}\n"
                f"Дата: {o['created_at']}\n"
            )

            items = get_items_for_order(o["id"])
            if items:
                text += "Товари:\n"
                for it in items:
                    subtotal = it["product_price"] * it["quantity"]
                    text += f"  {it['product_name']} x {it['quantity']} = {subtotal}\n"
            text += "--------------------------------\n"

    buttons = []
    if page > 0:
        buttons.append([
            InlineKeyboardButton(text="Попередня", callback_data=f"admin_list_orders_page:{page - 1}")
        ])

    if end < total:
        buttons.append([
            InlineKeyboardButton(text="Наступна", callback_data=f"admin_list_orders_page:{page + 1}")
        ])

    buttons.append([
        InlineKeyboardButton(text="Назад", callback_data="admin_back")
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=kb)


async def show_admin_menu(message: Message):

    buttons = [
        [InlineKeyboardButton(text="Додати товар", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="Список товарів", callback_data="admin_list_products")],
        [InlineKeyboardButton(text="Видалити товар", callback_data="admin_del_product")],
        [InlineKeyboardButton(text="Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="Замовлення (5 на сторінку)", callback_data="admin_list_orders_page:0")],
        [InlineKeyboardButton(text="Вийти", callback_data="admin_exit")]
    ]

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Адмін-меню:", reply_markup=kb)
