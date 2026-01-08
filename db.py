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
        is_private INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Letters table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        title TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Breakup table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS breakup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        breakup_date DATE,
        no_contact_days INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Gratitude table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gratitude (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    return conn
