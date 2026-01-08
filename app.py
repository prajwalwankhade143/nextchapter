import streamlit as st
st.markdown(
    """
    <style>
    /* Fix input text visibility only */
    input, textarea, select {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* Fix labels */
    label, .stTextLabel {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


from auth import register, login
from db import get_connection
from ai_model import analyze_sentiment

# -------- CONFIG --------
ADMIN_EMAIL = "prajwalwankhade202@gmail.com"

st.set_page_config(
    page_title="NextChapter",
    layout="centered"
)

# -------- SESSION INIT --------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_email", None)

# -------- HEADER --------
st.markdown("""
<style>
.card {
    background-color:#f9f9f9;
    padding:20px;
    border-radius:12px;
    box-shadow:0 4px 10px rgba(0,0,0,0.08);
    margin-bottom:15px;
}
.title {
    font-size:28px;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

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
if page == "Dashboard":
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
        for mood, note, date in data:
            st.markdown(f"""
            <div class="card">
                <b>{mood}</b><br>
                <small>{date}</small>
                <hr>
                {note}
            </div>
            """, unsafe_allow_html=True)

# -------- ADD JOURNEY --------
if page == "Add Journey":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Add Today’s Feelings")
    mood = st.selectbox(
        "Mood",
        ["Sad 😔", "Low 😞", "Neutral 😐", "Positive 😊"]
    )
    note = st.text_area("Your thoughts")

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
    st.markdown('</div>', unsafe_allow_html=True)

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

    for u in users:
        st.markdown(f"""
        <div class="card">
            <b>ID:</b> {u[0]}<br>
            <b>Name:</b> {u[1]}<br>
            <b>Email:</b> {u[2]}
        </div>
        """, unsafe_allow_html=True)

# -------- LOGOUT --------
if page == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.success("Logged out ✅")
    st.rerun()
