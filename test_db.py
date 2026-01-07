from db import get_connection

conn = get_connection()

if conn.is_connected():
    print("✅ Database connected successfully")
else:
    print("❌ Connection failed")
