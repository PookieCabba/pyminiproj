"""
Module 5.3: Socket Programming (Live API Client)
Module 3: Exception Handling
Fetches live data from Open-Meteo and sends it to the ClimateGuard server.
"""
import socket
import json
import time
import requests
from config import SOCKET_HOST, SOCKET_PORT

# Indian cities mapped to IMD region types and their baseline normal temperatures
CITIES = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "region": "Coastal", "normal_temp": 33.0},
    "Delhi": {"lat": 28.7041, "lon": 77.1025, "region": "Plains", "normal_temp": 38.0},
    "Shimla": {"lat": 31.1048, "lon": 77.1734, "region": "Hilly", "normal_temp": 24.0},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "region": "Coastal", "normal_temp": 34.0},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873, "region": "Plains", "normal_temp": 39.0},
    "Srinagar": {"lat": 34.0837, "lon": 74.7973, "region": "Hilly", "normal_temp": 22.0}
}

def fetch_live_weather(city_name: str, details: dict) -> dict:
    """Fetches real-time temperature and humidity using Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": details["lat"],
        "longitude": details["lon"],
        "current": ["temperature_2m", "relative_humidity_2m"]
    }
    
    # Module 3: Exception handling for API requests
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current_data = data.get("current", {})
        live_temp = current_data.get("temperature_2m", details["normal_temp"])
        live_humidity = current_data.get("relative_humidity_2m", 50.0)
        
        return {
            "location_name": city_name,
            "region_type": details["region"],
            "max_temp": live_temp,
            "normal_temp": details["normal_temp"], 
            "humidity": live_humidity,
            "source": "Open-Meteo API"
        }
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] Failed to fetch data for {city_name}: {e}")
        return None

def start_live_client():
    print(f"Starting Live API Client. Pushing data to {SOCKET_HOST}:{SOCKET_PORT}...")
    
    while True:
        for city, details in CITIES.items():
            weather_data = fetch_live_weather(city, details)
            
            if weather_data:
                payload = json.dumps(weather_data).encode('utf-8')
                
                # Module 3 & 5.3: Socket exception handling
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(5.0)
                        s.connect((SOCKET_HOST, SOCKET_PORT))
                        s.sendall(payload)
                        print(f"[LIVE STREAM] Sent {city}: {weather_data['max_temp']}°C (Normal: {weather_data['normal_temp']}°C)")
                except (ConnectionRefusedError, socket.timeout):
                    print("[ERROR] Connection to Server failed. Is aws_socket_server.py running?")
            
            # Wait 5 seconds before checking the next city
            time.sleep(5)

if __name__ == "__main__":
    start_live_client()