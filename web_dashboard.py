"""
Streamlit Web Dashboard for ClimateGuard
Continuously displays live database records, analytics visuals, and AI predictions.
"""
import streamlit as st
import pandas as pd
import sqlite3
import os
import time
import pickle
from PIL import Image
from config import DB_PATH
from imd_engine import classify_heatwave

# Define directories
VISUAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "heatwave_rf_model.pkl")

# 1. Page Configuration
st.set_page_config(
    page_title="Climate Intelligence",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Data Loader Function 
def fetch_live_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT timestamp, location_name, region_type, max_temp, departure, severity FROM weather_records ORDER BY timestamp DESC LIMIT 100"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 3. Sidebar Controls
st.sidebar.markdown("## 🌩️ Climate Intelligence")
st.sidebar.title("System Controls")
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", min_value=2, max_value=30, value=5)

if st.sidebar.button("Manual Refresh"):
    st.rerun()

# 4. Main Dashboard Header
st.title("🌡️ Climate Intelligence: Heatwave Intelligence Platform")
st.markdown("Live meteorological monitoring and AI-driven early warning system.")

df = fetch_live_data()

if df.empty:
    st.warning("No live data found. Ensure your `aws_socket_server.py` and `live_weather_client.py` are running.")
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
                column.error(f"Chart '{filename}' not found. Run `data_analytics.py` first.")

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
            # Load the binary pickle file (Module 3)
            with open(MODEL_PATH, 'rb') as file:
                rf_model = pickle.load(file)
            
            with st.form("prediction_form"):
                input_col1, input_col2, input_col3 = st.columns(3)
                region_input = input_col1.selectbox("IMD Region Type", ["Plains", "Coastal", "Hilly"])
                normal_temp_input = input_col2.number_input("Baseline Normal Temp (°C)", min_value=15.0, max_value=45.0, value=33.0, step=0.5)
                humidity_input = input_col3.number_input("Relative Humidity (%)", min_value=10.0, max_value=100.0, value=65.0, step=1.0)
                
                submit_prediction = st.form_submit_button("Generate Forecast", type="primary")
                
                if submit_prediction:
                    # 1. Format input for the model
                    input_data = pd.DataFrame([[normal_temp_input, humidity_input]], columns=['normal_temp', 'humidity'])
                    
                    # 2. Predict the max temperature
                    pred_max = rf_model.predict(input_data)[0]
                    
                    # 3. Classify the prediction using our IMD engine logic
                    predicted_severity, predicted_departure = classify_heatwave(
                        max_temp=pred_max, 
                        normal_temp=normal_temp_input, 
                        region_type=region_input
                    )
                    
                    # 4. Display Results
                    st.divider()
                    st.metric("Predicted Maximum Temperature", f"{pred_max:.2f} °C", f"+{predicted_departure:.2f} °C departure")
                    
                    if predicted_severity in ["Severe Heatwave", "Heatwave"]:
                        st.error(f"🚨 ALERT TRIGGERED: Expected {predicted_severity} conditions for this region based on predicted parameters.")
                    elif predicted_severity == "Warm Night / Elevated Heat":
                        st.warning("⚠️ WARNING: Elevated heat levels detected, approaching heatwave conditions.")
                    else:
                        st.success("✅ Forecast normal. No extreme heat conditions expected.")
        else:
            st.error("Model binary not found. Please run `ai_prediction_model.py` in your terminal to train and save the model first.")

# 7. Auto-Refresh Logic (Only applies outside of active form interactions)
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()