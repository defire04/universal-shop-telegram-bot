import random
from aiogram import F
from aiogram.types import Message, CallbackQuery

from .router import user_router, EMOJI_SET
from keyboards.inline import make_brand_menu, make_products_list
from keyboards.reply import main_reply_keyboard
from services.product_service import get_all_brands, list_products_by_brand


@user_router.message(F.text == "Каталог")
async def show_catalog(message: Message):
    """Handle the 'Каталог' button press"""
    brands = get_all_brands()
    if not brands:
        await message.answer(
            f"На жаль, зараз товари відсутні {random.choice(['😔', '😢', '😕'])}. "
            f"Повернись пізніше або запитай щось іще! {random.choice(EMOJI_SET['waiting'])}",
            reply_markup=main_reply_keyboard(message.from_user.id)
        )
        return

    catalog_emoji = random.choice(EMOJI_SET["catalog"])
    await message.answer(
        f"Ось наші бренди {catalog_emoji}. Обирай, будь ласка:",
        reply_markup=make_brand_menu(brands)
    )


@user_router.callback_query(F.data == "menu_catalog")
async def on_menu_catalog(callback: CallbackQuery):
    """Handle the menu_catalog callback"""
    try:
        await callback.message.delete()
    except Exception:
        pass

    brands = get_all_brands()
    if not brands:
        await callback.message.answer(
            f"Товари відсутні {random.choice(['😔', '😢', '😕'])}.",
            reply_markup=main_reply_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return

    catalog_emoji = random.choice(EMOJI_SET["catalog"])
    await callback.message.answer(
        f"Будь ласка, оберіть бренд {catalog_emoji}:",
        reply_markup=make_brand_menu(brands)
    )

    await callback.answer()


@user_router.callback_query(F.data.startswith("brand:"))
async def on_choose_brand(callback: CallbackQuery):
    """Handle brand selection callback"""
    brand = callback.data.split(":", 1)[1]
    products = list_products_by_brand(brand)

    try:
        await callback.message.delete()
    except Exception:
        pass

    if not products:
        await callback.message.answer(
            f"Поки що товарів бренду {brand} немає {random.choice(['😔', '😢', '😕'])}.",
            reply_markup=main_reply_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return

    catalog_emoji = random.choice(EMOJI_SET["catalog"])
    await callback.message.answer(
        f"Товари бренду {brand} {catalog_emoji}:",
        reply_markup=make_products_list(products)
    )

    await callback.answer()


@user_router.callback_query(F.data.startswith("back_to_brand:"))
async def on_back_to_brand(callback: CallbackQuery):
    """Handle back to brand callback"""
    try:
        await callback.message.delete()
    except Exception:
        pass

    brand = callback.data.split(":", 1)[1]
    products = list_products_by_brand(brand)

    if not products:
        await callback.message.answer(
            f"Поки що товарів бренду {brand} немає {random.choice(['😔', '😢', '😕'])}."
        )
        await callback.answer()
        return

    catalog_emoji = random.choice(EMOJI_SET["catalog"])
    await callback.message.answer(
        f"Товари бренду {brand} {catalog_emoji}:",
        reply_markup=make_products_list(products)
    )

    await callback.answer()