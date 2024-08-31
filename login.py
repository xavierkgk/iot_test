import streamlit as st
import bcrypt
from firebase_config import get_user_data

def login(username, password):
    """Attempt to log in a user with username and password."""
    user_data = get_user_data(username)
    print(f"User data: {user_data}")  # Debugging statement
    if user_data:
        stored_password_hash = user_data.get('password')
        print(f"Stored password hash: {stored_password_hash}")  # Debugging statement
        if stored_password_hash:
            password_matches = bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8'))
            print(f"Password matches: {password_matches}")  # Debugging statement
            return password_matches
    return False

def main():
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            if login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Logged in successfully!")
                st.query_params.update({'page': 'main'})  # Redirect to main page
                st.rerun()  # Refresh the app after logging in
            else:
                st.error("Invalid credentials. Please try again.")

if __name__ == "__main__":
    main()
