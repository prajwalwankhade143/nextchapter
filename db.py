import sqlite3

def get_connection():
    conn = sqlite3.connect("nextchapter.db", check_same_thread=False)
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # Journey table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS journey (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        mood TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    return conn
