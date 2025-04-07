import random

from repositories import product_repository
from services import order_service


def add_new_product(name, price, brand, description, photo_url):
    product_repository.create_product(name, price, brand, description, photo_url)


def get_all_brands():
    return product_repository.get_all_brands()


def list_products_by_brand(brand):
    return product_repository.get_products_by_brand(brand)


def list_all_products():
    return product_repository.get_all_products()


def get_product(product_id):
    return product_repository.get_product_by_id(product_id)


def remove_product(product_id):
    product_repository.delete_product(product_id)


def get_next_prev_products(product_id, brand):
    return product_repository.get_next_prev_product_ids(product_id, brand)


def get_random_recommendation(category=None, brand=None, price_range=None):
    products = product_repository.get_all_products()

    if not products:
        return None

    if brand:
        products = [p for p in products if p['brand'].lower() == brand.lower()]

    if price_range and len(price_range) == 2:
        min_price, max_price = price_range
        products = [p for p in products if min_price <= p['price'] <= max_price]

    if category:
        products = [p for p in products if category.lower() in p.get('description', '').lower()]

    if products:
        return random.choice(products)

    return None


def get_top_products(limit=3):
    top_products = order_service.get_top_products(limit)

    if not top_products:
        products = product_repository.get_all_products()
        return random.sample(products, min(limit, len(products))) if products else []
    return top_products
