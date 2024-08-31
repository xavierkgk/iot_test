import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from firebase_config import get_database

def check_login():
    """Check if the user is logged in."""
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.session_state.page = 'login'
        st.rerun()  # Refresh the app to apply the session state change

def show_login_page():
    """Render the login page."""
    st.title("Login Page")
    st.write("Please log in to access the dashboard.")
    # Implement your login form here
    # For example:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Replace with your authentication logic
        if username == "admin" and password == "password":
            st.session_state['logged_in'] = True
            st.session_state.page = 'dashboard'
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

def fetch_latest_readings(collection_name):
    """Fetch the latest reading for each sensor from Firestore."""
    db = get_database()
    docs = db.collection(collection_name).order_by('timestamp', direction='DESCENDING').get()
    
    data = []
    seen_sensors = set()

    for doc in docs:
        record = doc.to_dict()
        sensor_id = record.get('sensorID')
        if sensor_id not in seen_sensors:
            data.append(record)
            seen_sensors.add(sensor_id)

    return pd.DataFrame(data) if data else pd.DataFrame()

def show_dashboard():
    """Render the main dashboard."""
    st.title("IoT Dashboard Overview")

    collection_name = "iot_gateway_reading"
    latest_df = fetch_latest_readings(collection_name)

    if not latest_df.empty:
        latest_df['timestamp'] = pd.to_datetime(latest_df['timestamp'], utc=True)
        latest_df['timestamp'] = latest_df['timestamp'].dt.tz_convert('Asia/Singapore')
        latest_df['formatted_timestamp'] = latest_df['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
        latest_df = latest_df.sort_values(by='sensorID')

        st.header("Latest Sensor/Regulator Readings")

        for sensor_id, group in latest_df.groupby('sensorID'):
            for _, row in group.iterrows():
                time_diff = datetime.now(timezone.utc) - row['timestamp']
                is_outdated = time_diff.total_seconds() > 5 * 60
                container_bg_color = "#f1948a" if is_outdated else "#85c1e9"
                flash_class = "flash-red" if is_outdated else ""

                st.markdown(
                    f"""
                    <div class="sensor-container {flash_class}" style="background-color: {container_bg_color};">
                        <div class="sensor-info">
                            <h3>{sensor_id}</h3>
                            <p><strong>Timestamp:</strong> {row["formatted_timestamp"]}</p>
                        </div>
                        <div class="sensor-reading">
                            <div class="reading-box">
                                <p><strong>Pressure:</strong> {row["pressure"]}</p>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(
            """
            <style>
            @keyframes flash {
                0% { background-color: #f1948a; }
                50% { background-color: #f5b7b1; }
                100% { background-color: #f1948a; }
            }
            .flash-red {
                animation: flash 1s infinite;
            }
            .sensor-container {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                align-items: center;
                background-color: #f5f5f5;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .sensor-info {
                flex: 1;
                min-width: 180px;
            }
            .sensor-reading {
                flex: 2;
                padding-left: 20px;
                min-width: 220px;
            }
            .reading-box {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
                background-color: #abebc6;
            }
            @media (max-width: 768px) {
                .sensor-container {
                    flex-direction: column;
                    padding: 15px;
                }
                .sensor-info, .sensor-reading {
                    flex: unset;
                    min-width: 100%;
                    padding-left: 0;
                }
                .reading-box {
                    padding: 8px;
                    margin: 5px 0;
                }
                h3 {
                    font-size: 1.2rem;
                }
                p {
                    font-size: 0.9rem;
                }
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.write("No data available.")

def main():
    """Main function to handle the application flow."""
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'

    if st.session_state.page == 'login':
        show_login_page()
    else:
        check_login()
        show_dashboard()

if __name__ == "__main__":
    main()
