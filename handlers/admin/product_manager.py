from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from handlers.admin.router import admin_router
from handlers.admin.states import AdminActions
from handlers.admin.menu import show_admin_menu
from data.config import ADMIN_IDS
from services.product_service import add_new_product, remove_product, list_all_products


@admin_router.callback_query(F.data == "admin_add_product")
async def callback_add_product(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    await state.set_state(AdminActions.waiting_for_product_info)
    await callback.message.answer("Введіть: Назва|Ціна|Бренд|Фото URL")

    try:
        await callback.message.delete()
    except:
        pass

    await callback.answer()


@admin_router.callback_query(F.data == "admin_list_products")
async def callback_list_products(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    try:
        await callback.message.delete()
    except:
        pass

    products = list_all_products()
    txt = "📋 Список товарів:\n"

    if not products:
        txt += "Немає товарів."
    else:
        for p in products:
            txt += f"ID {p['id']}: {p['name']} ({p['brand']}) - {p['price']} грн\n"

    await callback.message.answer(txt)
    await show_admin_menu(callback.message)

    await callback.answer()


@admin_router.callback_query(F.data == "admin_del_product")
async def callback_delete_product(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Недостатньо прав.")
        return

    await state.set_state(AdminActions.waiting_for_product_id)
    await callback.message.answer("Введіть ID товару:")

    try:
        await callback.message.delete()
    except:
        pass

    await callback.answer()


@admin_router.message(AdminActions.waiting_for_product_info)
async def process_add_product(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    arr = message.text.split("|")
    if len(arr) < 4:
        await message.answer("❌ Невірний формат.")
        await show_admin_menu(message)
        await state.clear()
        return

    name = arr[0].strip()
    try:
        price = float(arr[1].strip())
    except ValueError:
        await message.answer("❌ Невірний формат ціни.")
        await show_admin_menu(message)
        await state.clear()
        return

    brand = arr[2].strip()
    photo_url = arr[3].strip()

    add_new_product(name, price, brand, photo_url)
    await message.answer("✅ Товар додано.")
    await show_admin_menu(message)
    await state.clear()


@admin_router.message(AdminActions.waiting_for_product_id)
async def process_del_product(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        pid = int(message.text)
    except ValueError:
        await message.answer("❌ Невірний ID.")
        await show_admin_menu(message)
        await state.clear()
        return

    remove_product(pid)
    await message.answer("✅ Товар видалено.")
    await show_admin_menu(message)
    await state.clear()