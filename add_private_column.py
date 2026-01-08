import sqlite3

conn = sqlite3.connect("nextchapter.db")
cur = conn.cursor()

# Column add karna (agar pehle se nahi hai)
try:
    cur.execute("ALTER TABLE journey ADD COLUMN is_private INTEGER DEFAULT 0")
    conn.commit()
    print("✅ is_private column added successfully")
except sqlite3.OperationalError:
    print("ℹ Column already exists")

conn.close()
