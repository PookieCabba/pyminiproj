"""
Module 3 & Module 5 Implementation:
SQLite Relational Database integration and File Logging.
"""
import sqlite3
import os
from datetime import datetime
from config import DB_PATH, LOG_DIR

def init_db():
    """Initializes SQLite database tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table 1: Real-time & Historical Weather Records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            location_name TEXT NOT NULL,
            region_type TEXT NOT NULL,
            max_temp REAL NOT NULL,
            normal_temp REAL NOT NULL,
            departure REAL NOT NULL,
            humidity REAL,
            severity TEXT NOT NULL,
            source TEXT NOT NULL
        )
    ''')
    
    # Table 2: System Early Warnings / Alerts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS heatwave_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            location_name TEXT NOT NULL,
            severity TEXT NOT NULL,
            advisory_text TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_weather_record(data: dict):
    """Inserts a processed weather observation into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO weather_records 
        (location_name, region_type, max_temp, normal_temp, departure, humidity, severity, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['location_name'],
        data['region_type'],
        data['max_temp'],
        data['normal_temp'],
        data['departure'],
        data.get('humidity', 0.0),
        data['severity'],
        data.get('source', 'API')
    ))
    
    conn.commit()
    
    # If severe or heatwave, log to text file (Module 3 File Handling)
    if data['severity'] in ["Heatwave", "Severe Heatwave"]:
        log_alert_to_file(data)
        
    conn.close()

def log_alert_to_file(data: dict):
    """Appends heatwave alerts to a text file (Module 3)."""
    log_file = os.path.join(LOG_DIR, "alerts.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] WARNING: {data['severity']} in {data['location_name']} | Max Temp: {data['max_temp']}°C (Departure: +{data['departure']}°C)\n"
    
    with open(log_file, mode="a", encoding="utf-8") as f:
        f.write(log_entry)

def fetch_recent_records(limit: int = 50):
    """Fetches recent observations for analysis and plotting."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM weather_records ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")