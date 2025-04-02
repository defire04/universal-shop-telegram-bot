
from repositories import product_repository

def add_new_product(name, price, brand, photo_url):
    product_repository.create_product(name, price, brand, photo_url)

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