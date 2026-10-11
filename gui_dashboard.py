"""
Module 5.1 & Self-Learning: Tkinter GUI, Canvas, Events, and PIL
Builds the ClimateGuard Heatwave Watch System Dashboard.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sqlite3
from config import DB_PATH

VISUAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")

class ClimateGuardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KJS-CES-01: ClimateGuard Heatwave Dashboard")
        self.root.geometry("900x650")
        
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Tab 1 & 2 Setup
        self.tab_monitor = ttk.Frame(self.notebook)
        self.tab_analytics = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_monitor, text="Live Monitor & Alerts")
        self.notebook.add(self.tab_analytics, text="Analytics Charts")
        
        self.build_monitor_tab()
        self.build_analytics_tab()

    def build_monitor_tab(self):
        """Creates layouts, form components, and Canvas shapes (Module 5.1)."""
        # --- Top Section: Canvas (Self-learning: Shapes, Lines, Moving Objects) ---
        self.canvas = tk.Canvas(self.tab_monitor, width=860, height=100, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Create different shapes & lines
        self.canvas.create_oval(10, 10, 90, 90, fill="red", outline="white")
        self.canvas.create_text(50, 50, text="ALERT", fill="white", font=("Arial", 12, "bold"))
        self.canvas.create_line(100, 50, 850, 50, fill="yellow", dash=(4, 4)) # Dashed line
        
        # Moving Object setup
        self.moving_text = self.canvas.create_text(850, 30, text=">>> SYSTEM ACTIVE: Monitoring Live Weather Nodes <<<", fill="cyan", font=("Courier", 14), anchor="w")
        self.animate_canvas()
        
        # --- Middle Section: Data Treeview (Form Components) ---
        columns = ("Time", "Location", "Region", "Max Temp", "Departure", "Severity")
        self.tree = ttk.Treeview(self.tab_monitor, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")
        self.tree.pack(pady=10)
        
        # --- Bottom Section: Buttons & Events ---
        btn_frame = ttk.Frame(self.tab_monitor)
        btn_frame.pack(pady=10)
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh Live Data", command=self.load_db_data)
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        alert_btn = ttk.Button(btn_frame, text="Trigger Test Alert", command=self.show_dialog)
        alert_btn.pack(side=tk.LEFT, padx=10)
        
        self.load_db_data() # Initial load

    def build_analytics_tab(self):
        """Loads images in Tkinter using PIL (Self-learning topic)."""
        controls_frame = ttk.Frame(self.tab_analytics)
        controls_frame.pack(side=tk.TOP, fill='x', pady=10)
        
        # Event creation for loading different charts
        ttk.Button(controls_frame, text="Line Trend", command=lambda: self.display_image("line_trend.png")).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Boxplot", command=lambda: self.display_image("box_region.png")).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Regression", command=lambda: self.display_image("scatter_regression.png")).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Severity Pie", command=lambda: self.display_image("pie_severity.png")).pack(side=tk.LEFT, padx=5)
        
        self.img_label = ttk.Label(self.tab_analytics)
        self.img_label.pack(expand=True, pady=10)
        self.display_image("pie_severity.png") # Default image

    def animate_canvas(self):
        """Moves text horizontally across the canvas (Self-learning: Moving objects)."""
        self.canvas.move(self.moving_text, -2, 0) # Move left by 2 pixels
        x_coords = self.canvas.coords(self.moving_text)
        
        # Reset position if it scrolls off screen
        if x_coords[0] < -400:
            self.canvas.coords(self.moving_text, 860, 30)
            
        self.root.after(30, self.animate_canvas) # Loop every 30ms

    def load_db_data(self):
        """Fetches data from SQLite and populates the Treeview."""
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, location_name, region_type, max_temp, departure, severity FROM weather_records ORDER BY timestamp DESC LIMIT 15")
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except sqlite3.OperationalError:
            print("Database not found or empty.")

    def show_dialog(self):
        """Triggers a Dialog Box (Module 5.1)."""
        messagebox.showwarning("Heatwave Alert", "Severe Heatwave detected in Region!\nInitiating Early Warning Protocol.")

    def display_image(self, filename):
        """Reads and loads images using PIL (Self-learning topic)."""
        img_path = os.path.join(VISUAL_DIR, filename)
        if os.path.exists(img_path):
            # PIL Image open
            img = Image.open(img_path)
            # Resize for dashboard fit
            img = img.resize((700, 450), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.photo)
        else:
            messagebox.showerror("Error", f"Image {filename} not found. Run data_analytics.py first.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClimateGuardApp(root)
    root.mainloop()