
import streamlit as st
from auth import register, login
from db import get_connection
from ai_model import analyze_sentiment
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

# ---------------- CONFIG ----------------
ADMIN_EMAIL = "prajwalwankhade202@gmail.com"

st.set_page_config(page_title="NextChapter", layout="centered")
st.markdown("""
<style>
/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #0b1220;
}

/* Sidebar button */
.sidebar-btn {
    width: 100%;
    padding: 14px;
    margin-bottom: 10px;
    border-radius: 12px;
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
    font-weight: 700;
    font-size: 15px;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s ease-in-out;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.sidebar-btn:hover {
    transform: scale(1.03);
    background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.sidebar-active {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: #052e16;
}
</style>
""", unsafe_allow_html=True)


# ---------------- GLOBAL STYLE ----------------
st.markdown("""
<style>
body { background:#0e1117; color:white; }
input, textarea, select {
    color:white !important;
    background:#1f2933 !important;
    border-radius:8px;
}
.card {
    background:#1f2933;
    padding:20px;
    border-radius:14px;
    box-shadow:0 6px 18px rgba(0,0,0,.4);
    margin-bottom:15px;
}
.title { font-size:32px; font-weight:800; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_email", None)
st.session_state.setdefault("page", "Login")


# ---------------- HEADER ----------------
st.markdown('<div class="title">🌱 NextChapter</div>', unsafe_allow_html=True)
st.caption("Your personal healing & reflection space")

# ---------------- SIDEBAR ----------------
def sidebar_btn(label, key):
    active = st.session_state.get("page") == label

    btn_style = """
        width:100%;
        padding:14px;
        margin-bottom:10px;
        border-radius:12px;
        background:linear-gradient(135deg, #2563eb, #3b82f6);
        color:white;
        font-weight:700;
        font-size:15px;
        text-align:center;
        box-shadow:0 4px 10px rgba(0,0,0,0.3);
    """

    if active:
        btn_style = btn_style.replace(
            "#2563eb, #3b82f6",
            "#22c55e, #16a34a"
        )

    # DESIGN BUTTON (visible)
    st.markdown(
        f"<div style='{btn_style}'>{label}</div>",
        unsafe_allow_html=True
    )

    # REAL BUTTON (invisible but clickable)
    clicked = st.button(
        label,
        key=key,
        help=label,
        use_container_width=True
    )

    if clicked:
        st.session_state.page = label
        st.rerun()


# ---------------- REGISTER ----------------
if page == "Register":
    st.subheader("Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        st.success("Registered ✅") if register(name,email,password) else st.error("Already exists ❌")

# ---------------- LOGIN ----------------
elif page == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login(email,password)
        if user:
            st.session_state.logged_in=True
            st.session_state.user_email=user[2]
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

# ---------------- DASHBOARD ----------------
elif page == "Dashboard":
    st.subheader("🌿 Mood Overview")

    conn=get_connection()
    cur=conn.cursor()
    cur.execute("""SELECT mood,note,is_private,created_at 
                   FROM journey WHERE user_email=? 
                   ORDER BY created_at DESC""",
                (st.session_state.user_email,))
    data=cur.fetchall()
    conn.close()

    if not data:
        st.info("No entries yet ✍️")
    else:
        df=pd.DataFrame(data,columns=["mood","note","private","date"])
        df["date"]=pd.to_datetime(df["date"]).dt.date

        dfp=df[(df["private"]==0)&(df["date"]>=date.today()-timedelta(days=6))]

        if not dfp.empty:
            score={"Sad 😔":1,"Low 😞":2,"Neutral 😐":3,"Positive 😊":4}
            dfp["score"]=dfp["mood"].map(score)

            fig,ax=plt.subplots(figsize=(7,3))
            ax.plot(dfp["date"],dfp["score"],marker="o",linewidth=2)
            ax.set_yticks([1,2,3,4])
            ax.set_yticklabels(score.keys())
            ax.set_title("Last 7 Days Mood")
            ax.grid(alpha=.3)
            st.pyplot(fig,clear_figure=True)

        mood_ai=analyze_sentiment(df.iloc[0]["note"])
        st.markdown(f"**🤖 Mood:** {mood_ai}")

        for m,n,p,d in data:
            st.markdown(f"""
            <div class="card">
                <b>{m} {'🔐' if p else ''}</b><br>
                <small>{d}</small><hr>{n}
            </div>
            """,unsafe_allow_html=True)

# ---------------- ADD JOURNEY ----------------
elif page == "Add Journey":
    st.subheader("📝 Add Entry")
    mood=st.selectbox("Mood",["Sad 😔","Low 😞","Neutral 😐","Positive 😊"])
    note=st.text_area("Write here")
    private=st.checkbox("Private 🔐")
    if st.button("Save"):
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("INSERT INTO journey (user_email,mood,note,is_private) VALUES (?,?,?,?)",
                    (st.session_state.user_email,mood,note,int(private)))
        conn.commit();conn.close()
        st.success("Saved 🌸")

# ---------------- ANALYZE ----------------
elif page == "Analyze":
    st.subheader("🤖 AI Analyzer")
    text=st.text_area("Paste thoughts")
    if st.button("Analyze"):
        st.success(analyze_sentiment(text))

# ---------------- LETTERS ----------------
elif page == "Letters":
    st.subheader("✉️ Unsent Letters")
    t=st.text_input("Title")
    c=st.text_area("Letter")
    if st.button("Save Letter"):
        conn=get_connection();cur=conn.cursor()
        cur.execute("INSERT INTO letters (user_email,title,content) VALUES (?,?,?)",
                    (st.session_state.user_email,t,c))
        conn.commit();conn.close()
        st.success("Saved")

    conn=get_connection();cur=conn.cursor()
    cur.execute("SELECT title,content,created_at FROM letters WHERE user_email=? ORDER BY created_at DESC",
                (st.session_state.user_email,))
    for t,c,d in cur.fetchall():
        st.markdown(f"<div class='card'><b>{t}</b><br>{c}</div>",unsafe_allow_html=True)
    conn.close()

# ---------------- BREAKUP ----------------
elif page == "Breakup Timeline":
    st.subheader("🕰️ Breakup Tracker")
    bd=st.date_input("Breakup Date")
    if st.button("Save"):
        days=(date.today()-bd).days
        conn=get_connection();cur=conn.cursor()
        cur.execute("INSERT INTO breakup (user_email,breakup_date,no_contact_days) VALUES (?,?,?)",
                    (st.session_state.user_email,bd,days))
        conn.commit();conn.close()
        st.success(f"{days} days strong 💪")

# ---------------- GRATITUDE ----------------
elif page == "Gratitude":
    st.subheader("🌸 Gratitude")
    n=st.text_area("One good thing")
    if st.button("Save"):
        conn=get_connection();cur=conn.cursor()
        cur.execute("INSERT INTO gratitude (user_email,note) VALUES (?,?)",
                    (st.session_state.user_email,n))
        conn.commit();conn.close()
        st.success("Saved 🌸")

# ---------------- ADMIN PANEL ----------------
elif page == "Admin":
    st.subheader("🛠 Admin Panel")

    conn=get_connection();cur=conn.cursor()
    cur.execute("SELECT id,name,email FROM users")
    users=cur.fetchall()

    cur.execute("SELECT mood FROM journey")
    moods=[m[0] for m in cur.fetchall()]
    score={"Sad 😔":1,"Low 😞":2,"Neutral 😐":3,"Positive 😊":4}
    avg=round(sum(score[m] for m in moods)/len(moods),2) if moods else 0
    conn.close()

    st.markdown(f"**Total Users:** {len(users)}")
    st.markdown(f"**Average Mood:** {avg}")

    for u in users:
        st.markdown(f"<div class='card'>{u[1]}<br>{u[2]}</div>",unsafe_allow_html=True)

# ---------------- LOGOUT ----------------
elif page == "Logout":
    st.session_state.logged_in=False
    st.session_state.user_email=None
    st.success("Logged out")
    st.rerun()
