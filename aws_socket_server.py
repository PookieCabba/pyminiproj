"""
Module 5.3: Socket Programming (Server side)
Integrates Module 1 & 2 (IMD Engine) and Module 5 (Database).
"""
import socket
import json
from config import SOCKET_HOST, SOCKET_PORT
from imd_engine import classify_heatwave, IMDDataException
from database import insert_weather_record

def start_socket_server():
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Prevent "Address already in use" errors during testing
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SOCKET_HOST, SOCKET_PORT))
        server_socket.listen(5)
        
        print(f"ClimateGuard AWS Server listening on {SOCKET_HOST}:{SOCKET_PORT}...")
        
        while True:
            try:
                # Accept incoming connection from the IoT client
                conn, addr = server_socket.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        continue
                        
                    # Decode JSON payload
                    raw_data = json.loads(data.decode('utf-8'))
                    
                    # Process data through IMD logic (Module 2)
                    severity, departure = classify_heatwave(
                        max_temp=raw_data['max_temp'],
                        normal_temp=raw_data['normal_temp'],
                        region_type=raw_data['region_type']
                    )
                    
                    # Enrich dictionary with processed results
                    raw_data['severity'] = severity
                    raw_data['departure'] = departure
                    
                    # Store in SQLite (Module 5.2)
                    insert_weather_record(raw_data)
                    print(f"[PROCESSED] {raw_data['location_name']} | Temp: {raw_data['max_temp']}°C | Alert: {severity}")
                    
            except json.JSONDecodeError:
                print("[ERROR] Received malformed JSON data.")
            except IMDDataException as ie:
                print(f"[DATA ERROR] Validation failed: {ie}")
            except Exception as e:
                print(f"[SERVER ERROR] Unexpected fault: {e}")

if __name__ == "__main__":
    start_socket_server()