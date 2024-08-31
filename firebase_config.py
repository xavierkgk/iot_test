import streamlit as st
import json
from google.oauth2 import service_account
from google.cloud import firestore

def initialize_firestore():
    # Load Firestore JSON credentials from Streamlit secrets
    firestore_json = st.secrets["firebase"]["credentials"]
    key_dict = json.loads(firestore_json)
    
    # Create credentials and initialize Firestore client
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project=key_dict["project_id"])
    return db

def get_database():
    """Get Firestore database client."""
    return initialize_firestore()

def get_user_data(username):
    """Fetch user data from Firestore based on username."""
    db = get_database()
    users_ref = db.collection('users')  # Ensure you have a 'users' collection
    user_doc = users_ref.document(username).get()
    return user_doc.to_dict() if user_doc.exists else None
