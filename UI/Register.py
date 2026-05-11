import os
import requests
import streamlit as st
import time
API_BASE_URL = os.getenv("API_URL", "http://api:8000")
def register():
    st.title("Register New User") 
    user_name = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if not user_name or not password:
            st.error("Please enter both username and password")
            return None   
        try:
            register_url = f"{API_BASE_URL}/register"
            query_params = {
                "user_name": user_name,
                "password": password
            }
            with st.spinner("Creating account..."):
                response = requests.post(register_url, params=query_params)
                if response.status_code == 200:
                    st.success("User created successfully!")
                    st.json(response.json()) 
                    return response.json().get("user")
                else:
                    st.error(f"Failed to register: {response.status_code} - {response.text}")            
        except requests.exceptions.ConnectionError as e:
            st.error(f"Connection Error: {e}")

def login():
    st.title("Login")
    user_name = st.text_input("Username")
    password = st.text_input("Password", type="password")  
    if st.button("Login"):
        if not user_name or not password:
            st.error("Please enter both username and password")
            return None
        try:
            login_url = f"{API_BASE_URL}/login"
            query_params = {
                "user_name": user_name,
                "password": password
            }
            with st.spinner("Authenticating..."):
                response = requests.post(login_url, params=query_params)
                if response.status_code == 200:
                    user_data = response.json().get("user")
                    
                    st.success(f"Login successful Welcome {user_name}")
                    st.session_state.logged_in = True
                    st.session_state.user_info = {"name": user_name}
                    return user_data
                    
                else:
                    st.error("Wrong credentials or user not found.")
                    
        except requests.exceptions.ConnectionError as e:
            st.error(f"Connection Error: {e}")
