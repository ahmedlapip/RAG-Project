import streamlit as st
#from src.controllers.UserController import UserController
import os
import requests
#from Processing import processing
from Register import register, login

st.title("RAG Project UI")
def main():
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Login":
        user = login()
        if user:
            st.write(f"Welcome {user['user_name']}!")
            st.write("Your related projects:")
            for project in user.get("projects", []):
                st.write(f"- {project}")
    elif choice == "Register":
        user=register()
        if user:
            st.write(f"User {user['user_name']} registered successfully! Please login now.")
if __name__ == "__main__":
    main()
