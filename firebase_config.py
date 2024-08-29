import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def get_firestore_credentials():
    """Retrieve Firestore credentials based on the environment."""
    if "STREAMLIT_ENV" in os.environ:
        # Running in Streamlit Cloud
        firestore_json = st.secrets["firebase"]["FIRESTORE_JSON"]
    else:
        # Running in local environment (e.g., Codespaces)
        firestore_json = os.environ.get("FIRESTORE_JSON")

    if not firestore_json:
        raise ValueError("Missing FIRESTORE_JSON environment variable")

    try:
        return json.loads(firestore_json)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid FIRESTORE_JSON format") from e

# Retrieve Firestore JSON secret
firestore_credentials = get_firestore_credentials()

# Initialize Firestore credentials and client
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(firestore_credentials)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    raise ValueError("Error initializing Firestore") from e

# Define a function to return the database client
def get_database():
    return db
