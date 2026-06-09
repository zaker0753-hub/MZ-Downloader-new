import sqlite3
from datetime import datetime


conn = sqlite3.connect(
    "database/bot.db",
    check_same_thread=False
)

cursor = conn.cursor()


def create_tables():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        join_date TEXT,
        last_url TEXT    
    )
    """)
    
    conn.commit()


def save_url(user_id, url):

    cursor.execute("""
    UPDATE users
    SET last_url = ?
    WHERE user_id = ?
    """, (url, user_id))

    conn.commit()


def get_url(user_id):

    cursor.execute("""
    SELECT last_url
    FROM users
    WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    if result:
        return result[0]

    return None

def save_user(
    user_id,
    username,
    first_name
):

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (
        user_id,
        username,
        first_name,
        join_date,
        last_url
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        user_id,
        username,
        first_name,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        None
    ))

    conn.commit()


def users_count():

    cursor.execute("""
    SELECT COUNT(*)
    FROM users
    """)

    return cursor.fetchone()[0]


def get_all_users():
    cursor.execute(
        """
        SELECT user_id FROM users
        """
    )
    return cursor.fetchall()


def users_today():

    cursor.execute("""
    SELECT COUNT(*)
    FROM users
    WHERE DATE(join_date)=DATE('now')
    """)

    return cursor.fetchone()[0]