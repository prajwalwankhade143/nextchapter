from ai_model import analyze_sentiment
from db import get_connection
import datetime

# 👇 example user_id (database me jo hai)
user_id = 1

text = "I feel very lonely after breakup"

mood = analyze_sentiment(text)
print("Detected mood:", mood)

conn = get_connection()
cur = conn.cursor()

cur.execute(
    "INSERT INTO mood_logs (user_id, mood, note, log_date) VALUES (%s, %s, %s, %s)",
    (user_id, mood, text, datetime.date.today())
)

conn.commit()
conn.close()

print("✅ Mood saved in database")
