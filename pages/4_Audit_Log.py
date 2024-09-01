import streamlit as st
from login import is_logged_in, login as authenticate_user

def show_login_page():
    """Render the login page."""
    st.title("Login Page")
    st.write("Please log in to access the audit logs.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            if authenticate_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state.page = 'audit_log'
                st.rerun()  # Refresh the app after logging in
            else:
                st.error("Invalid credentials. Please try again.")

def show_audit_log():
    """Render the audit log page."""
    st.title("Audit Log")
    st.write("This is where audit logs will be displayed.")

def main():
    """Main function to handle the application flow."""
    if not is_logged_in():
        show_login_page()
    else:
        show_audit_log()

if __name__ == "__main__":
    main()
