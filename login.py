# login.py
import streamlit as st
import bcrypt
from firebase_config import get_user_data

def login(username, password):
    """Attempt to log in a user with username and password."""
    user_data = get_user_data(username)
    if not user_data:
        return False

    stored_password_hash = user_data.get('password')
    if not stored_password_hash:
        return False

    password_bytes = password.encode('utf-8')
    stored_hash_bytes = stored_password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, stored_hash_bytes)

def is_logged_in():
    """Check if the user is logged in."""
    return 'logged_in' in st.session_state and st.session_state['logged_in']
