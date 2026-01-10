import sqlite3

conn = sqlite3.connect("sql/nextchapter.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS journey (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    mood TEXT,
    note TEXT,
    is_private INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("Journey table created successfully!")
