"""
Module 4: Pandas, NumPy, Matplotlib, and Seaborn Integration
Extracts data from SQLite, performs statistical analysis, and generates plots.
"""
import sqlite3
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from config import DB_PATH

# Use 'Agg' backend to save plots as images without opening GUI windows yet
import matplotlib
matplotlib.use('Agg')

VISUAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")
os.makedirs(VISUAL_DIR, exist_ok=True)

def load_data() -> pd.DataFrame:
    """Reads SQL database into a Pandas DataFrame and cleans it."""
    conn = sqlite3.connect(DB_PATH)
    # Read directly into a DataFrame
    query = "SELECT * FROM weather_records ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("[WARNING] No data in database. Ensure your server and client are running.")
        return df

    # Convert timestamp string to datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def generate_statistics(df: pd.DataFrame):
    """
    Demonstrates statistical functions: describe(), mean(), and CSV writing.
    """
    print("\n--- Summary Statistics (describe) ---")
    print(df[['max_temp', 'departure', 'humidity']].describe())

    print("\n--- Mean Temperature by Region (groupby & mean) ---")
    print(df.groupby('region_type')['max_temp'].mean())

    # Exporting DataFrame to CSV (Module 4 Syllabus requirement)
    csv_path = os.path.join(VISUAL_DIR, "heatwave_summary.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n[INFO] Data exported successfully to {csv_path}")

def generate_plots(df: pd.DataFrame):
    """
    Generates required plots (Line, Box, Scatter with Regression, Density, Pie).
    """
    # 1. Line Plot: Temperature Trends over time
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x='timestamp', y='max_temp', hue='location_name', marker='o')
    plt.title('Live Maximum Temperature Trends')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUAL_DIR, "line_trend.png"))
    plt.close()

    # 2. Box Plot: Distribution of Temperatures by Region
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x='region_type', y='max_temp', palette='Set2')
    plt.title('Temperature Distribution by Region (Boxplot)')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUAL_DIR, "box_region.png"))
    plt.close()

    # 3. Scatter Plot with Regression (lmplot)
    # Shows relationship between normal expected temp and actual max temp
    plt.figure(figsize=(8, 5))
    sns.regplot(data=df, x='normal_temp', y='max_temp', scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.title('Normal vs Actual Max Temperature (Regression)')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUAL_DIR, "scatter_regression.png"))
    plt.close()

    # 4. Density / Histogram Plot for Departures
    plt.figure(figsize=(8, 5))
    sns.histplot(df['departure'], kde=True, color='orange', bins=15)
    plt.title('Density Distribution of Temperature Departures')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUAL_DIR, "density_departure.png"))
    plt.close()

    # 5. Pie Chart: Severity Proportions using Matplotlib
    plt.figure(figsize=(6, 6))
    severity_counts = df['severity'].value_counts()
    colors = ['#66b3ff', '#ff9999', '#ffcc99', '#ff6666']
    plt.pie(severity_counts, labels=severity_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title('Proportion of Alert Severities')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUAL_DIR, "pie_severity.png"))
    plt.close()

    print(f"[INFO] All analytical plots successfully generated in '{VISUAL_DIR}' folder.")

def run_analytics_pipeline():
    df = load_data()
    if not df.empty:
        # Regex application (Module 4 Syllabus requirement): Filter cities starting with 'M' or 'D'
        filtered_df = df[df['location_name'].str.contains(r'^[MD]', regex=True, na=False)]
        print(f"\n[INFO] Regex Filtered Data (Cities starting with M or D): {len(filtered_df)} records.")
        
        generate_statistics(df)
        generate_plots(df)

if __name__ == "__main__":
    run_analytics_pipeline()