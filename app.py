import streamlit as st
from auth import register, login
from ai_model import analyze_sentiment
from db import get_connection
from eda import load_user_moods, mood_count_chart
import datetime

st.set_page_config(page_title="NextChapter", page_icon="💔")

st.title("💔 NextChapter")
st.write("Heal after breakup. One day at a time.")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- REGISTER ----------------
if choice == "Register":
    st.subheader("Create New Account")

    name = st.text_input("Your Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if name and email and password:
            register(name, email, password)
            st.success("Account created successfully. Please login.")
        else:
            st.warning("Please fill all fields")

# ---------------- LOGIN ----------------
if choice == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email, password)

        if user:
            user_id = user[0]
            user_name = user[1]

            st.success(f"Welcome {user_name} 💙")

            # ---------- DASHBOARD ----------
            st.divider()
            st.subheader("📊 Your Healing Dashboard")

            if st.button("Show My Healing Journey"):
                df = load_user_moods(user_id)

                if df.empty:
                    st.info("No data yet. Start writing your feelings daily 🌱")
                else:
                    st.dataframe(df)
                    chart = mood_count_chart(df)
                    st.pyplot(chart)

            # ---------- MOOD INPUT ----------
            st.divider()
            st.subheader("How are you feeling today?")

            note = st.text_area(
                "Write your heart out here",
                placeholder="I feel lonely, angry, confused..."
            )

            if st.button("Analyze & Save"):
                if note.strip() != "":
                    mood = analyze_sentiment(note)

                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO mood_logs (user_id, mood, note, log_date) VALUES (%s,%s,%s,%s)",
                        (user_id, mood, note, datetime.date.today())
                    )
                    conn.commit()
                    conn.close()

                    st.success(f"Detected Mood: {mood}")
                else:
                    st.warning("Please write something")
        else:
            st.error("Invalid email or password")
