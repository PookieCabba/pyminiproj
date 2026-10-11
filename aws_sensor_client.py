"""
Module 5.3: Socket Programming (Client side)
Module 3: Exception Handling
Simulates an IoT Automated Weather Station (AWS) sending live data.
"""
import socket
import json
import time
import random
from config import SOCKET_HOST, SOCKET_PORT, REGION_TYPES

def generate_sensor_data() -> dict:
    """Simulates reading from physical IoT temperature and humidity sensors."""
    region = random.choice(REGION_TYPES)
    # Generate realistic maximum temperatures to trigger various IMD rules
    max_temp = round(random.uniform(25.0, 50.0), 2)
    # Normal temp baseline for the simulated day
    normal_temp = round(random.uniform(25.0, 35.0), 2) 
    
    return {
        "location_name": f"AWS_Node_{random.randint(1, 10)}",
        "region_type": region,
        "max_temp": max_temp,
        "normal_temp": normal_temp,
        "humidity": round(random.uniform(30.0, 80.0), 2),
        "source": "IoT_Socket"
    }

def start_aws_client():
    print(f"Starting IoT AWS Sensor Node. Attempting to connect to {SOCKET_HOST}:{SOCKET_PORT}...")
    
    while True:
        sensor_data = generate_sensor_data()
        payload = json.dumps(sensor_data).encode('utf-8')
        
        # Module 3: Exception Handling for network operations
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0) # Prevent hanging
                s.connect((SOCKET_HOST, SOCKET_PORT))
                s.sendall(payload)
                print(f"[SENT] Data from {sensor_data['location_name']}: {sensor_data['max_temp']}°C ({sensor_data['region_type']})")
                
        except ConnectionRefusedError:
            print("[ERROR] Connection refused. Is the server running? Retrying in 5s...")
        except socket.timeout:
            print("[ERROR] Connection timed out. Retrying...")
        except Exception as e:
            print(f"[CRITICAL ERROR] Network failure: {e}")
            
        # Wait before sending the next reading
        time.sleep(4)

if __name__ == "__main__":
    start_aws_client()