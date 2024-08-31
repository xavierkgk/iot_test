import streamlit as st
import bcrypt
import pandas as pd
from firebase_config import get_database

# Initialize Firestore client
db = get_database()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def add_user(username, name, email, password, is_admin):
    """Add a new user to Firestore."""
    user_ref = db.collection('users').document(username)
    user_ref.set({
        'name': name,
        'email': email,
        'password': hash_password(password),  # Hash the password before storing
        'is_admin': is_admin
    })

def update_user(username, name=None, email=None, password=None, is_admin=None):
    """Update an existing user in Firestore."""
    user_ref = db.collection('users').document(username)
    updates = {}
    if name:
        updates['name'] = name
    if email:
        updates['email'] = email
    if password:
        updates['password'] = hash_password(password)  # Hash password if updating
    if is_admin is not None:
        updates['is_admin'] = is_admin
    user_ref.update(updates)

def remove_user(username):
    """Remove a user from Firestore."""
    db.collection('users').document(username).delete()

def get_users():
    """Retrieve all users from Firestore."""
    users_ref = db.collection('users')
    docs = users_ref.stream()
    users = []
    for doc in docs:
        user_data = doc.to_dict()
        user_data['username'] = doc.id
        users.append(user_data)
    return users

def main():
    st.title("User Manager")

    # Add User button as a popover
    with st.popover("➕ Add User", use_container_width=True):
        st.header("Add User")
        with st.form("add_user_form"):
            username = st.text_input("Username")
            name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            is_admin = st.checkbox("Admin")
            submit_button = st.form_submit_button("Add User")
            if submit_button:
                add_user(username, name, email, password, is_admin)
                st.success(f"User {username} added successfully!")
                st.rerun()  # Rerun the script to refresh the UI

    users = get_users()
    if users:
        # Create DataFrame from user list
        df = pd.DataFrame(users)
        df = df[['name', 'username', 'email', 'is_admin']]  # Select only desired columns

        st.write("## Users")
        for i, user in df.iterrows():
            cols = st.columns([3, 3, 3, 3, 1, 1])  # Adjust column widths
            cols[0].write(user['name'])
            cols[1].write(user['username'])
            cols[2].write(user['email'])
            cols[3].write(user['is_admin'])

            with cols[4]:
                # Update button as a popover with adjusted content
                with st.popover("✏️", use_container_width=True):
                    st.write(f"**Update User: {user['username']}**")
                    with st.form(f"update_user_form_{user['username']}"):
                        new_name = st.text_input("New Name", value=user['name'])
                        new_email = st.text_input("New Email", value=user['email'])
                        new_password = st.text_input("New Password", type="password")
                        new_is_admin = st.checkbox("Admin", value=user['is_admin'])
                        submit_button = st.form_submit_button("Update User")
                        if submit_button:
                            update_user(user['username'], new_name, new_email, new_password, new_is_admin)
                            st.success(f"User {user['username']} updated successfully!")
                            st.rerun()  # Rerun the script to refresh the UI

            with cols[5]:
                # Delete button as a popover with adjusted content
                with st.popover("🗑️", use_container_width=True):
                    st.write(f"**Delete User: {user['username']}**")
                    st.write("Are you sure you want to delete this user?")
                    confirm_delete = st.checkbox(f"Confirm delete {user['username']}")
                    if confirm_delete and st.button("Delete User", key=f"delete_{user['username']}"):
                        remove_user(user['username'])
                        st.success(f"User {user['username']} removed successfully!")
                        st.rerun()  # Rerun the script to refresh the UI

if __name__ == "__main__":
    main()
