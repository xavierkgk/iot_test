import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def get_firestore_credentials():
    """Retrieve Firestore credentials from Streamlit secrets or environment variables."""
    firestore_json = None

    # Attempt to retrieve from Streamlit secrets
    try:
        if (
            hasattr(st, "secrets") and
            "firebase" in st.secrets and
            "FIRESTORE_JSON" in st.secrets["firebase"]
        ):
            firestore_json = st.secrets["firebase"]["FIRESTORE_JSON"]
            source = "Streamlit secrets"
    except Exception as e:
        # st.secrets is not configured or not available
        pass

    # Fallback to environment variable
    if firestore_json is None:
        firestore_json = os.environ.get("FIRESTORE_JSON")
        source = "environment variable"

    if not firestore_json:
        raise ValueError(
            "Firestore credentials not found. Please set them in Streamlit secrets or as an environment variable."
        )

    # Parse the JSON string into a dictionary
    try:
        firestore_credentials = json.loads(firestore_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid FIRESTORE_JSON format from {source}") from e

    return firestore_credentials

def initialize_firestore():
    """Initialize Firestore client."""
    try:
        firestore_credentials = get_firestore_credentials()

        if not firebase_admin._apps:
            cred = credentials.Certificate(firestore_credentials)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db

    except Exception as e:
        raise ValueError(f"Error initializing Firestore: {e}") from e

# Initialize Firestore client
db = initialize_firestore()

def get_database():
    """Get Firestore database client."""
    return db
