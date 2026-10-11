"""
Module 3: File Handling & Exceptions
Module 1: Strings & format()
Generates an official stakeholder advisory report based on recorded anomalies.
"""
import sqlite3
import os
from datetime import datetime
from config import DB_PATH

REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

def generate_advisory_report():
    print("Scanning database for heatwave anomalies...")
    
    # Module 3: Exception handling for database reading
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Fetch only Severe Heatwaves and Heatwaves
        cursor.execute('''
            SELECT timestamp, location_name, region_type, max_temp, departure, severity 
            FROM weather_records 
            WHERE severity IN ('Heatwave', 'Severe Heatwave')
            ORDER BY timestamp DESC
        ''')
        alerts = cursor.fetchall()
        conn.close()
        
    except sqlite3.Error as e:
        print(f"[CRITICAL] Database error during report generation: {e}")
        return

    if not alerts:
        print("No heatwave alerts found. System normal.")
        return

    # Module 1: String formatting & File Handling prep
    report_filename = f"Heatwave_Advisory_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_path = os.path.join(REPORT_DIR, report_filename)
    
    header = """====================================================
      CLIMATEGUARD: OFFICIAL HEATWAVE ADVISORY
====================================================
Generated On: {}
Total Alerts: {}
----------------------------------------------------
"""
    
    advisory_template = """
[{timestamp}] ALERT IN {location} ({region} Region)
----------------------------------------------------
Severity Category : {severity}
Maximum Temp      : {temp} C
Departure         : +{departure} C from Normal

>> RECOMMENDED ACTION:
{action}
----------------------------------------------------
"""

    # Module 3: File Handling - Writing Text Files
    try:
        with open(report_path, 'w', encoding='utf-8') as file:
            # Write Header (Module 1: format)
            file.write(header.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(alerts)))
            
            for alert in alerts:
                timestamp, location, region, max_temp, departure, severity = alert
                
                # Determine action based on severity
                if severity == "Severe Heatwave":
                    action = "URGENT: Issue immediate public warnings. Prepare medical facilities for heat-stroke cases. Halt outdoor labor."
                else:
                    action = "WARNING: Issue public advisories. Ensure hydration stations are active. Advise vulnerable populations to stay indoors."
                
                # Write individual advisory blocks
                file.write(advisory_template.format(
                    timestamp=timestamp,
                    location=location,
                    region=region,
                    severity=severity,
                    temp=max_temp,
                    departure=departure,
                    action=action
                ))
                
        print(f"\n[SUCCESS] Stakeholder Advisory Report successfully generated at:\n{report_path}")
        
    except IOError as e:
        print(f"[ERROR] Failed to write report file: {e}")

if __name__ == "__main__":
    generate_advisory_report()