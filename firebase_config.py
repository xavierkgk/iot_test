import streamlit as st
import json
from google.oauth2 import service_account
from google.cloud import firestore

def initialize_firestore():
    # Load the JSON credentials from Streamlit secrets
    firestore_json = st.secrets["firebase"]["credentials"]
    key_dict = json.loads(firestore_json)
    
    # Create credentials and initialize Firestore client
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project=key_dict["project_id"])
    return db

def get_database():
    """Get Firestore database client."""
    return initialize_firestore()
