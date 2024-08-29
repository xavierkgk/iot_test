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
            print("Retrieved JSON from Streamlit secrets:", firestore_json)  # Debugging line
    except Exception as e:
        # st.secrets is not configured or not available
        pass

    # Fallback to environment variable
    if firestore_json is None:
        firestore_json = os.environ.get("FIRESTORE_JSON")
        source = "environment variable"
        print("Retrieved JSON from environment variable:", firestore_json)  # Debugging line

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
