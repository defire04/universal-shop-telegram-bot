
from data.db import get_connection

def create_product(name, price, brand, description, photo_url):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (name, price, brand, description, photo_url)
        VALUES (?, ?, ?, ?, ?)
    """, (name, price, brand, description, photo_url))
    conn.commit()
    conn.close()

def get_all_brands():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT brand FROM products ORDER BY brand ASC")
    rows = cur.fetchall()
    conn.close()
    return [r["brand"] for r in rows]

def get_products_by_brand(brand):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE brand = ?", (brand,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_product_by_id(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id=?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row

def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def get_next_prev_product_ids(product_id, brand):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM products WHERE brand = ? ORDER BY name ASC", (brand,))
    product_ids = [row["id"] for row in cur.fetchall()]

    if product_id not in product_ids:
        conn.close()
        return None, None

    current_index = product_ids.index(product_id)

    next_id = product_ids[(current_index + 1) % len(product_ids)]
    prev_id = product_ids[(current_index - 1) % len(product_ids)]

    conn.close()
    return prev_id, next_id