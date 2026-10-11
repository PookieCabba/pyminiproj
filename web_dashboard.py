"""
Streamlit Web Dashboard for Climate Intelligence
Continuously displays live database records, analytics visuals, and AI predictions.
"""
import streamlit as st
import pandas as pd
import sqlite3
import os
import time
import pickle
import requests
import random
from PIL import Image
from config import DB_PATH
from imd_engine import classify_heatwave

# Define directories
VISUAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "heatwave_rf_model.pkl")

# 1. Page Configuration
st.set_page_config(
    page_title="Climate Intelligence Web",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Data Loader Function (Cloud-friendly version that bypasses the socket server)
def fetch_live_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
        
    conn = sqlite3.connect(DB_PATH)
    
    # Fetch one live API reading directly from the web dashboard
    cities = [
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "region": "Coastal", "normal": 33.0},
        {"name": "Delhi", "lat": 28.7041, "lon": 77.1025, "region": "Plains", "normal": 38.0},
        {"name": "Shimla", "lat": 31.1048, "lon": 77.1734, "region": "Hilly", "normal": 24.0}
    ]
    city = random.choice(cities)
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current=temperature_2m"
        res = requests.get(url, timeout=5).json()
        live_temp = res['current']['temperature_2m']
        
        # Calculate IMD rules on the fly
        departure = round(live_temp - city['normal'], 2)
        severity = "Normal"
        if departure >= 6.4 or live_temp >= 47.0: severity = "Severe Heatwave"
        elif departure >= 4.5 or live_temp >= 35.0: severity = "Heatwave"
        
        # Insert into the cloud's temporary database
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO weather_records (location_name, region_type, max_temp, normal_temp, departure, severity, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (city['name'], city['region'], live_temp, city['normal'], departure, severity, 'Cloud API'))
        conn.commit()
    except:
        pass # If API fails, just load existing data
        
    # Return the updated database
    query = "SELECT timestamp, location_name, region_type, max_temp, departure, severity FROM weather_records ORDER BY timestamp DESC LIMIT 100"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 3. Sidebar Controls
st.sidebar.markdown("## 🌩️ KJSCE Climate Intelligence")
st.sidebar.title("System Controls")
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", min_value=2, max_value=30, value=5)

if st.sidebar.button("Manual Refresh"):
    st.rerun()

# 4. Main Dashboard Header
st.title("🌡️ Climate Intelligence: Heatwave Monitoring Platform")
st.markdown("Live meteorological monitoring and AI-driven early warning system.")

df = fetch_live_data()

if df.empty:
    st.warning("No live data found. Ensure your database is initialized.")
else:
    # 5. Top-Level Metrics (KPIs)
    latest = df.iloc[0]
    total_alerts = len(df[df['severity'].isin(['Heatwave', 'Severe Heatwave'])])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Node Update", latest['location_name'])
    col2.metric("Current Max Temp", f"{latest['max_temp']} °C", f"{latest['departure']} °C departure")
    col3.metric("Latest Severity", latest['severity'])
    col4.metric("Active Heatwave Alerts", total_alerts, delta_color="inverse")

    st.divider()

    # 6. Tabbed Interface Setup
    tab_live, tab_charts, tab_ai = st.tabs(["🔴 Live Feed", "📊 Analytics", "🧠 AI Forecast Engine"])

    # --- TAB 1: LIVE FEED ---
    with tab_live:
        st.subheader("Live IoT Sensor & API Feed")
        def highlight_severity(val):
            if val == 'Severe Heatwave': return 'background-color: #ff4c4c; color: white'
            elif val == 'Heatwave': return 'background-color: #ff9933; color: black'
            return ''

        styled_df = df.head(15).style.map(highlight_severity, subset=['severity'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # --- TAB 2: ANALYTICS ---
    with tab_charts:
        st.subheader("Spatio-Temporal Analytics")
        chart_col1, chart_col2 = st.columns(2)
        
        def load_and_display_chart(filename, column, title):
            filepath = os.path.join(VISUAL_DIR, filename)
            if os.path.exists(filepath):
                img = Image.open(filepath)
                column.image(img, caption=title, use_container_width=True)
            else:
                column.error(f"Chart '{filename}' not found. Run `data_analytics.py` locally and upload it.")

        with chart_col1:
            load_and_display_chart("pie_severity.png", st, "Alert Severity Distribution")
            load_and_display_chart("box_region.png", st, "Regional Temperature Variance")
            
        with chart_col2:
            load_and_display_chart("scatter_regression.png", st, "Normal vs Max Regression")
            load_and_display_chart("density_departure.png", st, "Departure Density Distribution")

    # --- TAB 3: AI FORECAST ENGINE ---
    with tab_ai:
        st.subheader("Predictive Heatwave Modeling")
        st.markdown("Enter localized meteorological parameters to generate an AI-driven temperature forecast.")
        
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as file:
                rf_model = pickle.load(file)
            
            with st.form("prediction_form"):
                input_col1, input_col2, input_col3 = st.columns(3)
                region_input = input_col1.selectbox("IMD Region Type", ["Plains", "Coastal", "Hilly"])
                normal_temp_input = input_col2.number_input("Baseline Normal Temp (°C)", min_value=15.0, max_value=4
