import pandas as pd
import matplotlib.pyplot as plt
from db import get_connection

def load_user_moods(user_id):
    conn = get_connection()
    query = """
        SELECT log_date, mood
        FROM mood_logs
        WHERE user_id = %s
        ORDER BY log_date
    """
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    return df

def mood_count_chart(df):
    mood_counts = df['mood'].value_counts()

    plt.figure()
    mood_counts.plot(kind='bar')
    plt.xlabel("Mood")
    plt.ylabel("Days Count")
    plt.title("Your Mood Distribution")
    plt.tight_layout()

    return plt
