import streamlit as st
from auth import register, login
from db import get_connection
from ai_model import analyze_sentiment

# -------- CONFIG --------
ADMIN_EMAIL = "prajwalwankhade202@gmail.com"

st.set_page_config(
    page_title="NextChapter",
    layout="centered"
)

# -------- GLOBAL STYLE (NO WHITE BACKGROUND) --------
st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: #ffffff;
    }

    input, textarea, select {
        color: #ffffff !important;
        background-color: #1f2933 !important;
        border-radius: 8px;
    }

    label, .stTextLabel {
        color: #e5e7eb !important;
    }

    .card {
        background-color:#1f2933;
        padding:20px;
        border-radius:14px;
        box-shadow:0 6px 18px rgba(0,0,0,0.4);
        margin-bottom:15px;
        color:#ffffff;
    }

    .title {
        font-size:30px;
        font-weight:800;
        margin-bottom:5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------- SESSION INIT --------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_email", None)

# -------- HEADER --------
st.markdown('<div class="title">🌱 NextChapter</div>', unsafe_allow_html=True)
st.caption("Your personal healing & reflection space")

# -------- SIDEBAR --------
if st.session_state.logged_in:
    menu = ["Dashboard", "Add Journey", "Analyze", "Logout"]
    if st.session_state.user_email == ADMIN_EMAIL:
        menu.insert(3, "Admin")
    page = st.sidebar.radio("Menu", menu)
else:
    page = st.sidebar.radio("Menu", ["Register", "Login"])

# -------- REGISTER --------
if page == "Register":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if register(name, email, password):
            st.success("Registered successfully ✅")
        else:
            st.error("Email already registered ❌")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- LOGIN --------
if page == "Login":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_email = user[2]
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- DASHBOARD --------
# -------- DASHBOARD --------
if page == "Dashboard":
    import pandas as pd
    import matplotlib.pyplot as plt
    st.subheader("🌿 Your Journey")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT mood, note, created_at FROM journey WHERE user_email=? ORDER BY created_at DESC",
        (st.session_state.user_email,)
    )
    data = cur.fetchall()
    conn.close()

    if not data:
        st.info("No entries yet ✍️")
    else:
        # -------- Mood Graph & Healing Progress --------
        df = pd.DataFrame(data, columns=["mood", "note", "date"])
        df["date"] = pd.to_datetime(df["date"]).dt.date

        mood_map = {"Sad 😔": 1, "Low 😞": 2, "Neutral 😐": 3, "Positive 😊": 4}
        df["score"] = df["mood"].map(mood_map)

        df_plot = df.iloc[::-1]  # oldest first

        # Matplotlib Chart
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(df_plot["date"], df_plot["score"], marker="o", color="#4ade80", linewidth=2)
        ax.set_ylim(0,5)
        ax.set_yticks([1,2,3,4])
        ax.set_yticklabels(["Sad 😔","Low 😞","Neutral 😐","Positive 😊"])
        ax.set_title("🌿 Last 7 Days Mood", fontsize=16)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        # Healing Progress
        improvement = df["score"].iloc[-1] - df["score"].iloc[0]
        if improvement > 0:
            st.success(f"💪 You're improving! Mood +{improvement}")
        elif improvement < 0:
            st.warning(f"⚠️ Mood decreased {improvement}")
        else:
            st.info("😐 Mood stable")

        # -------- Streak Tracker --------
        df_dates = df["date"].drop_duplicates().sort_values(ascending=False)
        streak = 1
        for i in range(1, len(df_dates)):
            if (df_dates.iloc[i-1] - df_dates.iloc[i]).days == 1:
                streak += 1
            else:
                break
        st.info(f"🔥 Current Streak: {streak} day(s) in a row!")

        # -------- AI Advice / Coping --------
        last_note = df["note"].iloc[-1]
        from ai_model import analyze_sentiment
        mood_result = analyze_sentiment(last_note)
        suggestion_map = {
            "Sad 😔": "Try a short walk or write 3 things you’re grateful for 🌸",
            "Low 😞": "Take 5 deep breaths or listen to calming music 🎧",
            "Neutral 😐": "Keep journaling daily, small steps matter ✍️",
            "Positive 😊": "Great! Share your joy with someone today 🌟"
        }
        st.markdown(f"**🤖 Mood:** {mood_result}")
        st.markdown(f"**💡 Suggestion:** {suggestion_map[mood_result]}")

        # -------- List of Entries --------
        for mood, note, date in data:
            st.markdown(
                f"""
                <div class="card">
                    <b>{mood}</b><br>
                    <small>{date}</small>
                    <hr>
                    {note}
                </div>
                """,
                unsafe_allow_html=True
            )


# -------- ADD JOURNEY --------
st.subheader("📝 Add Today’s Feelings")
mood = st.selectbox(
    "Mood",
    ["Sad 😔", "Low 😞", "Neutral 😐", "Positive 😊"]
)
note = st.text_area("Your thoughts")

# ✅ Private Entry Checkbox
is_private = st.checkbox("Make this entry private 🔐")

if st.button("Save"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO journey (user_email, mood, note, is_private) VALUES (?, ?, ?, ?)",
        (st.session_state.user_email, mood, note, int(is_private))
    )
    conn.commit()
    conn.close()
    st.success("Saved successfully 🌸")



# -------- ANALYZE --------
if page == "Analyze":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 AI Mood Analyzer")
    text = st.text_area("Paste your thoughts")

    if st.button("Analyze"):
        result = analyze_sentiment(text)
        st.success(f"Result: {result}")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- ADMIN --------
if page == "Admin":
    st.subheader("🛠 Admin Panel – Users")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users ORDER BY id DESC")
    users = cur.fetchall()
    conn.close()

    if not users:
        st.info("No users found yet")
    else:
        for u in users:
            st.markdown(
                f"""
                <div class="card">
                    <b>ID:</b> {u[0]}<br>
                    <b>Name:</b> {u[1]}<br>
                    <b>Email:</b> {u[2]}
                </div>
                """,
                unsafe_allow_html=True
            )

# -------- LOGOUT --------
if page == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.success("Logged out ✅")
    st.rerun()
