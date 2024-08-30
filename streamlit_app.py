import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator
from io import BytesIO
from firebase_config import get_database  # Ensure this import matches the function definition

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

def to_excel(df):
    """Convert DataFrame to Excel format."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def save_plot_to_bytes(fig):
    """Save a plot to a BytesIO buffer."""
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

# Streamlit app components
st.title("Streamlit IoT Dashboard Test")

collection_name = "iot_gateway_reading"
df = fetch_data(collection_name)

# Ensure the timestamp column is in datetime format with timezone info
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Add date range filter
st.sidebar.header("Filter by Date Range")
start_date = st.sidebar.date_input("Start date", df['timestamp'].min().date())
end_date = st.sidebar.date_input("End date", df['timestamp'].max().date())

# Convert start_date and end_date to timezone-aware pd.Timestamp for comparison
start_date = pd.Timestamp(start_date).tz_localize('UTC')  # Make timezone-aware
end_date = pd.Timestamp(end_date).tz_localize('UTC') + pd.Timedelta(days=1)  # Make timezone-aware and add one day

# Filter the DataFrame based on the selected date range
filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] < end_date)]

# Add sensor ID dropdown filter with "Select All" option
st.sidebar.header("Filter by Sensor ID")
sensor_ids = df['sensorID'].unique()
sensor_ids = sorted(sensor_ids)  # Sort sensor IDs for better user experience
sensor_ids_with_all = ["All"] + list(sensor_ids)  # Add "All" option
selected_sensor = st.sidebar.selectbox("Select Sensor ID", options=sensor_ids_with_all)

# Filter the DataFrame based on the selected sensor ID
if selected_sensor == "All":
    # Show data for all sensors
    filtered_df = filtered_df
else:
    # Filter for the selected sensor ID
    filtered_df = filtered_df[filtered_df['sensorID'] == selected_sensor]

# Check if filtered DataFrame is empty
if filtered_df.empty:
    st.write("No data available for the selected filters.")
else:
    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plotting data for the selected sensorID or all sensors
    if selected_sensor == "All":
        for sensor_id in sensor_ids:
            sensor_data = filtered_df[filtered_df['sensorID'] == sensor_id]
            ax.plot(sensor_data['timestamp'], sensor_data['pressure'], label=sensor_id, marker='o')
    else:
        ax.plot(filtered_df['timestamp'], filtered_df['pressure'], label=selected_sensor, marker='o')

    # Formatting the x-axis with date and time
    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))

    # Adding labels and title
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Pressure')
    ax.set_title('Pressure Readings Over Time by Sensor')
    ax.legend(title='Sensor ID')
    ax.grid(True)

    # Rotate date labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Display plot in Streamlit
    st.pyplot(fig)
    st.dataframe(filtered_df)

    # Export Data
    st.sidebar.header("Export Data")
    if st.sidebar.button("Export CSV"):
        csv = to_csv(filtered_df)
        st.sidebar.download_button(label="Download CSV", data=csv, file_name='filtered_data.csv', mime='text/csv')

    if st.sidebar.button("Export Excel"):
        excel = to_excel(filtered_df)
        st.sidebar.download_button(label="Download Excel", data=excel, file_name='filtered_data.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # Export Plot
    if st.sidebar.button("Download Plot"):
        buf = save_plot_to_bytes(fig)
        st.sidebar.download_button(label="Download Plot", data=buf, file_name='plot.png', mime='image/png')
