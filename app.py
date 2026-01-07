import streamlit as st
from auth import register, login
from db import get_connection
from ai_model import analyze_sentiment

st.set_page_config(page_title="NextChapter")

st.title("NextChapter – Step 2 ✅")

# -------- SESSION INIT --------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_email", None)

# DEBUG INFO
st.write("DEBUG ▶ logged_in:", st.session_state.logged_in)
st.write("DEBUG ▶ user_email:", st.session_state.user_email)

# -------- SIDEBAR --------
if st.session_state.logged_in:
    page = st.sidebar.radio("Menu", ["Dashboard", "Add Journey", "Analyze", "Admin", "Logout"])
else:
    page = st.sidebar.radio("Menu", ["Register", "Login"])

# -------- REGISTER --------
if page == "Register":
    st.subheader("Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        success = register(name, email, password)
        if success:
            st.success("Registered successfully ✅")
        else:
            st.error("Email already registered ❌ Please login")

# -------- LOGIN --------
if page == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_email = user[2]  # email index
            st.success("Login successful ✅")
        else:
            st.error("Invalid credentials ❌")

# -------- DASHBOARD --------
if page == "Dashboard":
    st.subheader("🌱 Your Healing Journey")
    if st.session_state.user_email:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT mood, note, created_at FROM journey WHERE user_email=? ORDER BY created_at DESC",
            (st.session_state.user_email,)
        )
        data = cur.fetchall()
        conn.close()

        if not data:
            st.info("No entries yet. Start writing today ✍️")
        else:
            for mood, note, date in data:
                st.markdown(f"### {mood}")
                st.caption(date)
                st.write(note)
                st.divider()

# -------- ADD JOURNEY --------
if page == "Add Journey":
    st.subheader("📝 Add Today's Feelings")
    mood = st.selectbox("How do you feel?", ["Sad 😔", "Low 😞", "Neutral 😐", "Positive 😊"])
    note = st.text_area("Write your thoughts")

    if st.button("Save"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO journey (user_email, mood, note) VALUES (?, ?, ?)",
            (st.session_state.user_email, mood, note)
        )
        conn.commit()
        conn.close()
        st.success("Saved successfully 🌸")

# -------- ANALYZE --------
if page == "Analyze":
    st.subheader("🤖 AI Mood Analyzer")
    text = st.text_area("Paste your thoughts")

    if st.button("Analyze"):
        result = analyze_sentiment(text)
        st.success(f"AI Result: {result}")
        # -------- ADMIN PAGE --------
st.subheader("🛠️ Admin: Registered Users")
conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT id, name, email FROM users ORDER BY id DESC")
users = cur.fetchall()
conn.close()

if users:
    for u in users:
        st.write(f"ID: {u[0]} | Name: {u[1]} | Email: {u[2]}")
else:
    st.info("No users registered yet.")


# -------- LOGOUT --------
if page == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.success("Logged out ✅")
