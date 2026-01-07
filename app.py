import streamlit as st

st.title("🔥 NEXTCHAPTER TEST APP")
st.success("Agar ye dikh raha hai to deploy SUCCESS hai")
st.write("Time:", st.time_input("now"))

import streamlit as st

st.set_page_config(page_title="NextChapter")

st.title("NextChapter – Step 1 ✅")

# session init
st.session_state.setdefault("logged_in", False)

st.write("LOGIN STATE ▶", st.session_state.logged_in)

if not st.session_state.logged_in:
    if st.button("Fake Login"):
        st.session_state.logged_in = True
        st.rerun()
else:
    st.success("🎉 You are LOGGED IN")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

