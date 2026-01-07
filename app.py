import streamlit as st
from auth import register, login

st.set_page_config(page_title="NextChapter", layout="centered")

st.title("💔 NextChapter")
st.write("Heal. Analyze. Move Forward.")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Create Account")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        register(name, email, password)
        st.success("Account created successfully!")

elif choice == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email, password)
        if user:
            st.success("Login successful!")
            st.write("Welcome to your healing journey 🌱")
        else:
            st.error("Invalid credentials")
