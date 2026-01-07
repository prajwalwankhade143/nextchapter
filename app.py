import streamlit as st
from auth import register, login

st.set_page_config(page_title="NextChapter")

st.title("NextChapter")

choice = st.sidebar.selectbox("Menu", ["Register", "Login"])

if choice == "Register":
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        register(name, email, password)
        st.success("Registered successfully")

if choice == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email, password)
        if user:
            st.success("Login successful")
        else:
            st.error("Invalid credentials")
