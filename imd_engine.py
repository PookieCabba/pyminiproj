"""
Module 1 & Module 2 Implementation:
Data structures, functional logic, decorators, and custom exceptions.
"""
import time
import functools
from typing import Dict, Any, Tuple
from config import IMD_THRESHOLDS, DEPARTURE_HEATWAVE, DEPARTURE_SEVERE_HEATWAVE

class IMDDataException(Exception):
    """Custom exception for invalid temperature input data."""
    pass

def log_execution_time(func):
    """Decorator to log function execution time (Module 2: Decorators)."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[LOG] Executed {func.__name__} in {(end_time - start_time):.4f}s")
        return result
    return wrapper

@log_execution_time
def classify_heatwave(
    max_temp: float, 
    normal_temp: float, 
    region_type: str = "Plains", 
    *args, 
    **kwargs
) -> Tuple[str, float]:
    """
    Evaluates temperature against IMD guidelines (Module 2: Control Flow & Arguments).
    Returns (Severity Level, Departure from Normal).
    """
    if region_type not in IMD_THRESHOLDS:
        raise IMDDataException(f"Invalid Region Type: '{region_type}'. Must be one of {list(IMD_THRESHOLDS.keys())}")
    
    if max_temp < -50.0 or max_temp > 60.0:
        raise IMDDataException(f"Out of bounds temperature reading: {max_temp}°C")

    departure = round(max_temp - normal_temp, 2)
    limits = IMD_THRESHOLDS[region_type]
    
    severity = "Normal"

    # Evaluation logic
    is_severe_by_dept = departure >= DEPARTURE_SEVERE_HEATWAVE
    is_severe_by_abs = max_temp >= limits["severe_heatwave_temp"]
    
    is_hw_by_dept = departure >= DEPARTURE_HEATWAVE
    is_hw_by_abs = max_temp >= limits["heatwave_temp"]

    if is_severe_by_dept or is_severe_by_abs:
        severity = "Severe Heatwave"
    elif is_hw_by_dept or is_hw_by_abs:
        severity = "Heatwave"
    elif departure >= 3.0:
        severity = "Warm Night / Elevated Heat"

    return severity, departure

def process_batch_observations(records: list) -> list:
    """
    Processes batch weather records using map and filter (Module 2).
    """
    # Filter out invalid records using lambda
    valid_records = list(filter(lambda r: r.get("max_temp") is not None, records))
    
    # Process classification using map
    processed = list(map(
        lambda r: {
            **r,
            **dict(zip(["severity", "departure"], classify_heatwave(r["max_temp"], r["normal_temp"], r.get("region_type", "Plains"))))
        },
        valid_records
    ))
    return processed