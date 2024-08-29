import streamlit as st
import pandas as pd
from firebase_config import get_database

def fetch_data(collection_name):
    """Fetches data from a Firestore collection.

    Args:
        collection_name (str): The name of the Firestore collection.

    Returns:
        pandas.DataFrame: A DataFrame containing the fetched data.
    """
    db = get_database()
    docs = db.collection(collection_name).get()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data) if data else pd.DataFrame()

# Streamlit app components
st.title("Streamlit IoT Dashboard Test")

collection_name = "iot_gateway_reading"
df = fetch_data(collection_name)

st.dataframe(df)

# ... other app components using data or functionality
