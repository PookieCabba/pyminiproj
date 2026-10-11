"""
Global Configurations & IMD Threshold Criteria
"""
import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(BASE_DIR, "climateguard.db")

os.makedirs(LOG_DIR, exist_ok=True)

# IMD Regional Types
REGION_TYPES = ("Plains", "Coastal", "Hilly")

# IMD Departure & Absolute Threshold Constants (°C)
IMD_THRESHOLDS = {
    "Plains": {
        "normal_range": (30.0, 40.0),
        "heatwave_temp": 45.0,
        "severe_heatwave_temp": 47.0,
    },
    "Coastal": {
        "normal_range": (25.0, 35.0),
        "heatwave_temp": 35.0,
        "severe_heatwave_temp": 37.0,
    },
    "Hilly": {
        "normal_range": (20.0, 30.0),
        "heatwave_temp": 30.0,
        "severe_heatwave_temp": 35.0,
    }
}

DEPARTURE_HEATWAVE = 4.5
DEPARTURE_SEVERE_HEATWAVE = 6.4

# Network & Socket Defaults
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 65432