import sqlite3

def get_connection():
    conn = sqlite3.connect("nextchapter.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    return conn
