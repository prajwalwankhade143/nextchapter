from db import get_connection
import hashlib
import sqlite3

def register(name, email, password):
    conn = get_connection()
    cur = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    try:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_pw)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login(email, password):
    conn = get_connection()
    cur = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    cur.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hashed_pw)
    )
    user = cur.fetchone()
    conn.close()
    return user
