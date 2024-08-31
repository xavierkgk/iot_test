import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from firebase_config import get_database
from fpdf import FPDF  # Import the FPDF library

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

def to_csv(df):
    """Convert DataFrame to CSV format."""
    return df.to_csv(index=False).encode('utf-8')

def to_pdf(df):
    """Convert DataFrame to PDF format."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title
    pdf.cell(200, 10, txt="Filtered Data", ln=True, align='C')

    # Add header
    header = df.columns.tolist()
    for col in header:
        pdf.cell(40, 10, txt=col, border=1)
    pdf.ln()

    # Add data rows
    for index, row in df.iterrows():
        for value in row:
            pdf.cell(40, 10, txt=str(value), border=1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin1')

# Streamlit app components
st.title("Streamlit IoT Dashboard Test")

collection_name = "iot_gateway_reading"
df = fetch_data(collection_name)

# Ensure the timestamp column is in datetime format with timezone info
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Convert the timestamp to GMT+8 and format it
df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Singapore')
df['formatted_timestamp'] = df['timestamp'].dt.strftime('%d/%m/%Y %H:%M')

# Create a container for the main page content
with st.container():
    # Add date range filter
    st.header("Filter by Date Range")
    start_date = st.date_input("Start date", df['timestamp'].min().date())
    end_date = st.date_input("End date", df['timestamp'].max().date())

    # Convert start_date and end_date to timezone-aware pd.Timestamp for comparison
    start_date = pd.Timestamp(start_date).tz_localize('Asia/Singapore')  # Make timezone-aware
    end_date = pd.Timestamp(end_date).tz_localize('Asia/Singapore') + pd.Timedelta(days=1)  # Make timezone-aware and add one day

    # Filter the DataFrame based on the selected date range
    filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] < end_date)]

    # Add sensor ID dropdown filter with "Select All" option
    st.header("Filter by Sensor ID")
    sensor_ids = df['sensorID'].unique()
    sensor_ids = sorted(sensor_ids)  # Sort sensor IDs for better user experience
    sensor_ids_with_all = ["All"] + list(sensor_ids)  # Add "All" option
    selected_sensor = st.selectbox("Select Sensor ID", options=sensor_ids_with_all)

    # Filter the DataFrame based on the selected sensor ID
    if selected_sensor != "All":
        filtered_df = filtered_df[filtered_df['sensorID'] == selected_sensor]

    # Check if filtered DataFrame is empty
    if filtered_df.empty:
        st.write("No data available for the selected filters.")
    else:
        # Show basic statistics in colorful box widgets
        st.header("Basic Statistics")
        
        # Compute statistics
        total_records = filtered_df.shape[0]
        mean_pressure = filtered_df['pressure'].mean()
        median_pressure = filtered_df['pressure'].median()
        std_pressure = filtered_df['pressure'].std()

        # Create colorful boxes for statistics using HTML/CSS
        st.markdown(
            f"""
            <style>
            .metric-container {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
            }}
            .metric-box {{
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                width: 23%;
            }}
            .metric-box h3 {{
                margin: 0;
                font-size: 16px;
                color: #333;
            }}
            .metric-box p {{
                margin: 5px 0 0;
                font-size: 24px;
                color: #007bff;
                font-weight: bold;
            }}
            </style>
            <div class="metric-container">
                <div class="metric-box">
                    <h3>Total Records</h3>
                    <p>{total_records}</p>
                </div>
                <div class="metric-box">
                    <h3>Mean Pressure</h3>
                    <p>{mean_pressure:.2f}</p>
                </div>
                <div class="metric-box">
                    <h3>Median Pressure</h3>
                    <p>{median_pressure:.2f}</p>
                </div>
                <div class="metric-box">
                    <h3>Standard Deviation</h3>
                    <p>{std_pressure:.2f}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Create an Altair chart for better visualization
        st.header(f"Pressure Readings Over Time - {'All Sensors' if selected_sensor == 'All' else selected_sensor}")
        
        # Altair line chart for multiple sensors
        chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X('timestamp:T', title='Timestamp', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('pressure:Q', title='Pressure'),
            color=alt.Color('sensorID:N', title='Sensor ID'),
            tooltip=['formatted_timestamp', 'sensorID', 'pressure']
        ).interactive().properties(
            width=800,
            height=400,
            title='Pressure Readings Over Time by Sensor'
        )
        
        st.altair_chart(chart)

        # Display the filtered data with the formatted timestamp
        st.dataframe(filtered_df[['formatted_timestamp', 'sensorID', 'pressure']])

        # Export Data
        st.header("Export Data")
        if st.button("Export CSV"):
            csv = to_csv(filtered_df[['formatted_timestamp', 'sensorID', 'pressure']])
            st.download_button(label="Download CSV", data=csv, file_name='filtered_data.csv', mime='text/csv')

        if st.button("Export PDF"):
            pdf = to_pdf(filtered_df[['formatted_timestamp', 'sensorID', 'pressure']])
            st.download_button(label="Download PDF", data=pdf, file_name='filtered_data.pdf', mime='application/pdf')
