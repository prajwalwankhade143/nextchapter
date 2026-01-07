import streamlit as st

st.title("NextChapter – Step 1 ✅ TEST")

# SESSION INIT
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.write("LOGIN STATE ▶", st.session_state.logged_in)

# LOGIN BUTTON
if not st.session_state.logged_in:
    if st.button("Fake Login"):
        st.session_state.logged_in = True
        st.success("Login success ✅")
else:
    st.success("🎉 You are LOGGED IN")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out ✅")
