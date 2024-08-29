import os
import json
from firebase_admin import credentials, initialize_app
from firebase_admin import firestore

# Retrieve Firestore JSON secret from environment variable
firestore_json = os.environ.get("FIRESTORE_JSON")

if not firestore_json:
    raise ValueError("Missing FIRESTORE_JSON environment variable")

# Parse the JSON string into a dictionary
firestore_credentials = json.loads(firestore_json)

# Initialize Firestore credentials and client
try:
    app = initialize_app(credentials.Certificate(firestore_credentials))
except ValueError:
    # If the app is already initialized, do nothing
    pass

db = firestore.client()

# Define a function to return the database client
def get_database():
    return db
