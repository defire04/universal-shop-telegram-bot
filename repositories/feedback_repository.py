from data.db import get_connection

def save_feedback(user_id, username, full_name, feedback_text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feedback (user_id, username, full_name, feedback_text)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, full_name, feedback_text))
    conn.commit()
    conn.close()
    return cur.lastrowid

def get_all_feedback():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM feedback
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_feedback_by_user_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM feedback
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_feedback_by_id(feedback_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM feedback
        WHERE id = ?
    """, (feedback_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_feedback_page(page: int, page_size: int):
    offset = page * page_size
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM feedback
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (page_size, offset))
    rows = cur.fetchall()
    conn.close()
    return rows




from data.db import get_connection

def save_feedback(user_id, username, full_name, feedback_text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feedback (user_id, username, full_name, feedback_text)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, full_name, feedback_text))
    conn.commit()
    conn.close()
    return cur.lastrowid

def get_all_feedback():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM feedback
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_feedback_page(page: int, page_size: int):
    offset = page * page_size
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM feedback
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (page_size, offset))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_feedback_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM feedback")
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0