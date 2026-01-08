import streamlit as st

from auth import register, login
from db import get_connection
from ai_model import analyze_sentiment
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# -------- CONFIG --------
ADMIN_EMAIL = "prajwalwankhade202@gmail.com"

st.set_page_config(
    page_title="NextChapter",
    layout="centered"
)

# -------- GLOBAL STYLE (DARK MODE) --------
st.markdown("""
<style>
body { background-color: #0e1117; color: #ffffff; }
input, textarea, select { color: #ffffff !important; background-color: #1f2933 !important; border-radius: 8px; }
label, .stTextLabel { color: #e5e7eb !important; }
.card { background-color:#1f2933; padding:20px; border-radius:14px; box-shadow:0 6px 18px rgba(0,0,0,0.4); margin-bottom:15px; color:#ffffff; }
.title { font-size:30px; font-weight:800; margin-bottom:5px; }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #0b1220;
}

/* Radio buttons container */
div[role="radiogroup"] > label {
    background-color: #1f2933;
    padding: 12px 16px;
    margin-bottom: 10px;
    border-radius: 12px;
    color: #e5e7eb !important;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    border: 1px solid #2d3748;
}

/* Hover effect */
div[role="radiogroup"] > label:hover {
    background-color: #2563eb;
    color: #ffffff !important;
    transform: scale(1.02);
}

/* Selected menu item */
div[role="radiogroup"] > label[data-checked="true"] {
    background-color: #22c55e !important;
    color: #0f172a !important;
    box-shadow: 0 4px 12px rgba(34,197,94,0.4);
}
</style>
""", unsafe_allow_html=True)


# -------- SESSION INIT --------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_email", None)
st.session_state.setdefault("page", "Register")  # default page

# -------- HEADER --------
st.markdown('<div class="title">🌱 NextChapter</div>', unsafe_allow_html=True)
st.caption("Your personal healing & reflection space")

# -------- SIDEBAR MENU --------
# -------- SIDEBAR MENU --------
with st.sidebar:
    st.markdown("## 📍 Menu")

    def sidebar_button(label, key):
        active = st.session_state.get("page") == label
        btn_class = "sidebar-btn sidebar-active" if active else "sidebar-btn"

        clicked = st.markdown(
            f"<div class='{btn_class}'>{label}</div>",
            unsafe_allow_html=True
        )

        if st.button(label, key=key, use_container_width=True):
            st.session_state.page = label

    # -------- NOT LOGGED IN --------
    if not st.session_state.logged_in:
        sidebar_button("Register", "reg")
        sidebar_button("Login", "login")

    # -------- LOGGED IN --------
    else:
        sidebar_button("Dashboard", "dash")
        sidebar_button("Add Journey", "add")
        sidebar_button("Analyze", "ana")
        sidebar_button("Letters", "let")
        sidebar_button("Breakup Timeline", "time")
        sidebar_button("Gratitude", "grat")

        if st.session_state.user_email == ADMIN_EMAIL:
            sidebar_button("Admin", "admin")

        sidebar_button("Logout", "logout")

# 🔹 Fix: page variable ko sidebar ke **baad** set karein
page = st.session_state.get("page", "Login")




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
elif page == "Login":
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
            st.session_state.page = "Dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials ❌")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- DASHBOARD --------
elif page == "Dashboard":
    st.subheader("🌿 Your Journey")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT mood, note, is_private, created_at FROM journey WHERE user_email=? ORDER BY created_at DESC",
        (st.session_state.user_email,)
    )
    data = cur.fetchall()
    conn.close()

    if not data:
        st.info("No entries yet ✍️")
    else:
        df = pd.DataFrame(data, columns=["mood","note","is_private","date"])
        df["date"] = pd.to_datetime(df["date"]).dt.date

        # Only public entries for chart/streak
        df_public = df[df["is_private"]==0].copy()
        if not df_public.empty:
            mood_map = {"Sad 😔":1,"Low 😞":2,"Neutral 😐":3,"Positive 😊":4}
            df_public["score"] = df_public["mood"].map(mood_map)
            df_plot = df_public.iloc[::-1]

            # Mood Chart
            fig, ax = plt.subplots(figsize=(6,3))
            ax.plot(df_plot["date"], df_plot["score"], marker="o", color="#4ade80", linewidth=2)
            ax.set_ylim(0,5)
            ax.set_yticks([1,2,3,4])
            ax.set_yticklabels(["Sad 😔","Low 😞","Neutral 😐","Positive 😊"])
            ax.set_title("🌿 Last 7 Days Mood", fontsize=16)
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)

            # Streak Tracker
            df_dates = df_public["date"].drop_duplicates().sort_values(ascending=False)
            streak = 1
            for i in range(1, len(df_dates)):
                if (df_dates.iloc[i-1]-df_dates.iloc[i]).days==1:
                    streak+=1
                else:
                    break
            st.info(f"🔥 Current Streak: {streak} day(s) in a row!")

        # AI Advice from last note
        last_note = df["note"].iloc[0]  # include private note
        mood_result = analyze_sentiment(last_note)
        suggestion_map = {
            "Sad 😔":"Try a short walk or write 3 things you’re grateful for 🌸",
            "Low 😞":"Take 5 deep breaths or listen to calming music 🎧",
            "Neutral 😐":"Keep journaling daily, small steps matter ✍️",
            "Positive 😊":"Great! Share your joy with someone today 🌟"
        }
        st.markdown(f"**🤖 Mood:** {mood_result}")
        st.markdown(f"**💡 Suggestion:** {suggestion_map[mood_result]}")

        # All entries list
        for mood,note,is_private,date_val in data:
            private_tag = "🔐" if is_private else ""
            st.markdown(f"""
                <div class="card">
                    <b>{mood} {private_tag}</b><br>
                    <small>{date_val}</small>
                    <hr>
                    {note}
                </div>
            """, unsafe_allow_html=True)

# -------- ADD JOURNEY --------
elif page == "Add Journey":
    st.subheader("📝 Add Today’s Feelings")
    mood = st.selectbox("Mood", ["Sad 😔","Low 😞","Neutral 😐","Positive 😊"])
    note = st.text_area("Your thoughts")
    is_private = st.checkbox("Make this entry private 🔐")
    if st.button("Save"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO journey (user_email,mood,note,is_private) VALUES (?,?,?,?)",
            (st.session_state.user_email,mood,note,int(is_private))
        )
        conn.commit()
        conn.close()
        st.success("Saved successfully 🌸")

# -------- ANALYZE --------
elif page == "Analyze":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 AI Mood Analyzer")
    text = st.text_area("Paste your thoughts")
    if st.button("Analyze"):
        result = analyze_sentiment(text)
        st.success(f"Result: {result}")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- LETTERS --------
elif page == "Letters":
    st.subheader("✉️ Letters You’ll Never Send")
    title = st.text_input("Title")
    content = st.text_area("Write your letter here")
    if st.button("Save Letter"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO letters (user_email,title,content) VALUES (?,?,?)",
                    (st.session_state.user_email,title,content))
        conn.commit()
        conn.close()
        st.success("Letter saved (Private 🌱)")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, content, created_at FROM letters WHERE user_email=? ORDER BY created_at DESC",
                (st.session_state.user_email,))
    letters = cur.fetchall()
    conn.close()
    for t,c,d in letters:
        st.markdown(f"""
            <div class="card">
                <b>{t}</b><br>
                <small>{d}</small>
                <hr>
                {c}
            </div>
        """, unsafe_allow_html=True)

# -------- BREAKUP TIMELINE --------
elif page == "Breakup Timeline":
    st.subheader("🕰️ Breakup Timeline")
    breakup_date = st.date_input("Breakup Date")
    if st.button("Save Breakup Date"):
        conn = get_connection()
        cur = conn.cursor()
        days = (date.today()-breakup_date).days
        cur.execute("INSERT INTO breakup (user_email,breakup_date,no_contact_days) VALUES (?,?,?)",
                    (st.session_state.user_email,breakup_date,days))
        conn.commit()
        conn.close()
        st.success(f"Saved! You survived {days} day(s) 💪")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT breakup_date,no_contact_days FROM breakup WHERE user_email=? ORDER BY created_at DESC",
                (st.session_state.user_email,))
    timeline = cur.fetchall()
    conn.close()
    for bd,days_val in timeline:
        st.markdown(f"""
            <div class="card">
                <b>Breakup Date:</b> {bd} <br>
                <b>No-Contact Days:</b> {days_val} day(s)
            </div>
        """, unsafe_allow_html=True)

# -------- GRATITUDE --------
elif page == "Gratitude":
    st.subheader("🌸 Gratitude Mode")
    note = st.text_area("One good thing today")
    if st.button("Save Gratitude"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO gratitude (user_email,note) VALUES (?,?)",
                    (st.session_state.user_email,note))
        conn.commit()
        conn.close()
        st.success("Saved 🌸")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT note, created_at FROM gratitude WHERE user_email=? ORDER BY created_at DESC",
                (st.session_state.user_email,))
    notes = cur.fetchall()
    conn.close()
    for n,d in notes:
        st.markdown(f"""
            <div class="card">
                <small>{d}</small>
                <hr>
                {n}
            </div>
        """, unsafe_allow_html=True)

# -------- ADMIN --------
elif page == "Admin":
    st.subheader("🛠 Admin Panel – Users / Stats")
    conn = get_connection()
    cur = conn.cursor()

    # Users
    cur.execute("SELECT id,name,email FROM users ORDER BY id DESC")
    users = cur.fetchall()
    total_users = len(users)

    # Active today
    cur.execute("SELECT COUNT(DISTINCT user_email) FROM journey WHERE DATE(created_at)=DATE('now')")
    active_today = cur.fetchone()[0]

    # Avg mood score
    cur.execute("SELECT mood FROM journey")
    moods = cur.fetchall()
    score_map = {"Sad 😔":1,"Low 😞":2,"Neutral 😐":3,"Positive 😊":4}
    scores = [score_map[m[0]] for m in moods]
    avg_mood = round(sum(scores)/len(scores),2) if scores else 0

    conn.close()

    st.markdown(f"**Total Users:** {total_users}")
    st.markdown(f"**Active Today:** {active_today}")
    st.markdown(f"**Average Mood Score:** {avg_mood}")

    if not users:
        st.info("No users found yet")
    else:
        for u in users:
            st.markdown(f"""
                <div class="card">
                    <b>ID:</b> {u[0]}<br>
                    <b>Name:</b> {u[1]}<br>
                    <b>Email:</b> {u[2]}
                </div>
            """, unsafe_allow_html=True)

# -------- LOGOUT --------
elif page == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.success("Logged out ✅")
    st.rerun()
