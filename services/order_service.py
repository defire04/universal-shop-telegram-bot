from repositories import order_repository
from services.product_service import get_product


def create_new_order_ext(user_id, cart_data, delivery_method, address, phone, comment, full_name, payment_method, payment_status='pending'):
    total_price = 0.0
    for pid, qty in cart_data.items():
        prod = get_product(pid)
        if prod:
            total_price += prod["price"] * qty

    oid = order_repository.create_order_ext(
        user_id, total_price,
        delivery_method, address,
        phone, comment, full_name,
        payment_method, payment_status
    )

    for pid, qty in cart_data.items():
        order_repository.add_order_item(oid, pid, qty)
    return oid


def get_all_orders():
    return order_repository.get_all_orders()


def get_user_orders(user_id):
    return order_repository.get_orders_by_user(user_id)


def get_stats():
    count = order_repository.get_orders_count()
    total = order_repository.get_total_revenue()
    return count, total


def get_orders_count():
    return order_repository.get_orders_count()


def get_orders_page(page, page_size):
    return order_repository.get_orders_page(page, page_size)


def get_items_for_order(order_id):
    return order_repository.get_items_for_order(order_id)


