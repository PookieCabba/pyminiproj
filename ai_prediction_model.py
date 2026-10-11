"""
Phase II: AI-Driven Heatwave Analytics and Prediction
Module 3: Working with Binary Files (Pickle)
Trains an ML model to forecast maximum temperature and saves it as a binary file.
"""
import sqlite3
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from config import DB_PATH
from imd_engine import classify_heatwave

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "heatwave_rf_model.pkl")

def train_and_save_model():
    print("Loading historical database records for AI training...")
    
    # 1. Load Data
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT normal_temp, humidity, max_temp FROM weather_records WHERE max_temp IS NOT NULL"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) < 20:
        print("[WARNING] Not enough data to train. Please let the live socket server run longer to gather more records.")
        return

    # 2. Feature Selection (X) and Target (y)
    # normal_temp acts as a proxy for region, combined with humidity to predict max_temp
    X = df[['normal_temp', 'humidity']]
    y = df['max_temp']
    
    # 3. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Initialize and Train Model
    print(f"Training Random Forest Regressor on {len(X_train)} records...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Evaluate Model
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    print(f"[METRICS] Mean Absolute Error: {mae:.2f}°C | Root Mean Squared Error: {rmse:.2f}°C")
    
    # 6. Save Model to Binary File (Module 3 requirement)
    with open(MODEL_PATH, 'wb') as file:
        pickle.dump(model, file)
    print(f"[SUCCESS] AI Model successfully saved as binary file at: {MODEL_PATH}")

def load_and_predict(normal_temp: float, humidity: float, region: str):
    """Loads the binary model and makes a prediction on new data."""
    if not os.path.exists(MODEL_PATH):
        print("[ERROR] Model binary not found. Run train_and_save_model() first.")
        return
        
    # Module 3: Reading Binary Files
    with open(MODEL_PATH, 'rb') as file:
        loaded_model = pickle.load(file)
        
    # Format input for prediction
    input_data = pd.DataFrame([[normal_temp, humidity]], columns=['normal_temp', 'humidity'])
    
    # Predict max temp
    predicted_max = loaded_model.predict(input_data)[0]
    
    # Pass predicted temp back through our IMD rules engine
    predicted_severity, predicted_departure = classify_heatwave(
        max_temp=predicted_max, 
        normal_temp=normal_temp, 
        region_type=region
    )
    
    print("\n--- AI PREDICTION RESULTS ---")
    print(f"Inputs         : Normal Temp: {normal_temp}°C | Humidity: {humidity}% | Region: {region}")
    print(f"Predicted Max  : {predicted_max:.2f}°C")
    print(f"Forecast Alert : {predicted_severity} (Departure: +{predicted_departure:.2f}°C)")
    print("-----------------------------\n")

if __name__ == "__main__":
    # 1. Train the model using the database you've been building
    train_and_save_model()
    
    # 2. Test a hypothetical future prediction
    # E.g., Tomorrow in Mumbai (Coastal, Normal: 33.0C, high humidity)
    load_and_predict(normal_temp=33.0, humidity=85.0, region="Coastal")