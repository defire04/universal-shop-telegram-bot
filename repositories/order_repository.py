def get_all_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def create_order_ext(user_id, total_price, delivery_method, address, phone, comment, full_name, payment_method,
                     payment_status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO orders (user_id, total_price, delivery_method, address, phone, comment, full_name, payment_method, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, total_price, delivery_method, address, phone, comment, full_name, payment_method, payment_status)
    )

    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    return order_id


def add_order_item(order_id, product_id, quantity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO order_items (order_id, product_id, quantity)
        VALUES (?, ?, ?)
    """, (order_id, product_id, quantity))
    conn.commit()
    conn.close()


def get_orders_by_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_orders_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM orders")
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0


def get_total_revenue():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(total_price) as total FROM orders")
    row = cur.fetchone()
    conn.close()
    return row["total"] if row["total"] else 0.0


def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows


from data.db import get_connection


def get_orders_page(page: int, page_size: int):
    offset = page * page_size
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM orders
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (page_size, offset))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_items_for_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name AS product_name,
               p.price AS product_price,
               oi.quantity AS quantity
        FROM order_items AS oi
        JOIN products AS p ON p.id = oi.product_id
        WHERE oi.order_id = ?
    """, (order_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_top_products(limit=3):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.id, p.name, p.price, p.brand, p.photo_url, 
               SUM(oi.quantity) as total_ordered
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        GROUP BY p.id
        ORDER BY total_ordered DESC
        LIMIT ?
    """, (limit,))

    top_products = cur.fetchall()
    conn.close()

    return top_products