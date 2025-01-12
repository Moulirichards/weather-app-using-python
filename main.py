import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime
import os
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Dashboard")
        self.root.geometry("800x600")
        
        
        self.colors = {
            'bg': '#E8EEF6',
            'card': '#FFFFFF',
            'primary': '#2196F3',
            'secondary': '#64B5F6',
            'text': '#1E293B',
            'text_light': '#64748B'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # API configuration
        self.API_KEY = "d494c6744fc62dc97eefad0d7c6dbea3"
        self.BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
        
       
        self.configure_styles()
        self.setup_gui()

    def configure_styles(self):
       
        style = ttk.Style()
        
       
        style.configure(
            "Custom.TEntry",
            fieldbackground=self.colors['card'],
            borderwidth=0,
            relief="flat"
        )
        
        
        style.configure(
            "Custom.TButton",
            background=self.colors['primary'],
            foreground="black",
            padding=10,
            relief="flat"
        )
        
        style.map("Custom.TButton",
                 background=[('active', self.colors['secondary'])],
                 relief=[('pressed', 'flat')])
        
    def setup_gui(self):
        
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(padx=40, pady=30, fill="both", expand=True)
        
       
        title = tk.Label(
            main_container,
            text="Weather Dashboard",
            font=("Helvetica", 24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title.pack(pady=(0, 20))
        
        
        search_frame = tk.Frame(
            main_container,
            bg=self.colors['card'],
            relief="flat",
            bd=1
        )
        search_frame.pack(fill="x", padx=20, pady=10)
        
        
        search_inner = tk.Frame(search_frame, bg=self.colors['card'], padx=15, pady=15)
        search_inner.pack(fill="x")
        
       
        self.location_entry = ttk.Entry(
            search_inner,
            font=("Helvetica", 12),
            width=40,
            style="Custom.TEntry"
        )
        self.location_entry.pack(side="left", padx=(0, 10), ipady=5)
        self.location_entry.insert(0, "Enter city name...")
        
       
        self.location_entry.bind("<FocusIn>", self.on_entry_click)
        self.location_entry.bind("<FocusOut>", self.on_focus_out)
        self.location_entry.bind("<Return>", lambda e: self.fetch_weather())
        
        
        self.search_button = ttk.Button(
            search_inner,
            text="Search",
            style="Custom.TButton",
            command=self.fetch_weather
        )
        self.search_button.pack(side="left", padx=5)
        
        
        self.weather_card = tk.Frame(
            main_container,
            bg=self.colors['card'],
            relief="flat",
            bd=1
        )
        self.weather_card.pack(fill="both", expand=True, padx=20, pady=20)
        
      
        self.city_label = tk.Label(
            self.weather_card,
            text="No city selected",
            font=("Helvetica", 22, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        self.city_label.pack(pady=(20, 10))
        
        
        self.temp_label = tk.Label(
            self.weather_card,
            text="--°C",
            font=("Helvetica", 48),
            bg=self.colors['card'],
            fg=self.colors['primary']
        )
        self.temp_label.pack(pady=5)
        
     
        self.desc_label = tk.Label(
            self.weather_card,
            text="",
            font=("Helvetica", 14),
            bg=self.colors['card'],
            fg=self.colors['text_light']
        )
        self.desc_label.pack(pady=5)
        
        
        details_frame = tk.Frame(self.weather_card, bg=self.colors['card'])
        details_frame.pack(pady=20, padx=30)
        
       
        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(2, weight=1)
        
       
        self.create_detail_widget(details_frame, "💧 Humidity", "--%", 0)
        self.create_detail_widget(details_frame, "💨 Wind Speed", "-- m/s", 1)
        self.create_detail_widget(details_frame, "🌡️ Pressure", "-- hPa", 2)
        
        
        self.temp_unit = "C"
        self.temp_data = None
        self.toggle_button = ttk.Button(
            self.weather_card,
            text="Switch to °F",
            style="Custom.TButton",
            command=self.toggle_temperature_unit
        )
        self.toggle_button.pack(pady=20)

    def create_detail_widget(self, parent, title, initial_value, column):
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.grid(row=0, column=column, padx=15, pady=10, sticky="nsew")
        
        tk.Label(
            frame,
            text=title,
            font=("Helvetica", 12),
            bg=self.colors['card'],
            fg=self.colors['text_light']
        ).pack()
        
        label = tk.Label(
            frame,
            text=initial_value,
            font=("Helvetica", 14, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        label.pack(pady=5)
        
        setattr(self, f"{title.split()[1].lower()}_label", label)

    def on_entry_click(self, event):
        if self.location_entry.get() == "Enter city name...":
            self.location_entry.delete(0, "end")
            self.location_entry.config(foreground=self.colors['text'])

    def on_focus_out(self, event):
        if self.location_entry.get() == "":
            self.location_entry.insert(0, "Enter city name...")
            self.location_entry.config(foreground=self.colors['text_light'])

    def fetch_weather(self):
        city = self.location_entry.get().strip()
        
        if not city or city == "Enter city name...":
            messagebox.showwarning("Warning", "Please enter a city name")
            return
        
      
        self.search_button.configure(state='disabled')
        self.city_label.config(text="Loading...")
        self.root.update()
        
        try:
            params = {
                "q": city,
                "appid": self.API_KEY,
                "units": "metric"
            }
            
            response = requests.get(self.BASE_URL, params=params)
            data = response.json()
            
            if response.status_code == 200:
                self.update_weather_display(data)
            else:
                messagebox.showerror("Error", f"Error: {data.get('message', 'City not found')}")
                self.city_label.config(text="No city selected")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.city_label.config(text="No city selected")
        finally:
            self.search_button.configure(state='normal')

    def update_weather_display(self, data):
       
        self.temp_data = data['main']['temp']
        
       
        self.city_label.config(text=f"{data['name']}, {data['sys']['country']}")
        self.temp_label.config(text=f"{self.temp_data:.1f}°{self.temp_unit}")
        self.desc_label.config(text=data['weather'][0]['description'].capitalize())
        
       
        self.humidity_label.config(text=f"{data['main']['humidity']}%")
        self.wind_label.config(text=f"{data['wind']['speed']} m/s")
        self.pressure_label.config(text=f"{data['main']['pressure']} hPa")
        
       
        self.flash_update(self.temp_label)

    def flash_update(self, widget):
        original_bg = widget.cget("bg")
        widget.config(bg=self.colors['secondary'])
        self.root.after(200, lambda: widget.config(bg=original_bg))

    def toggle_temperature_unit(self):
        if self.temp_data is None:
            return
            
        if self.temp_unit == "C":
            self.temp_unit = "F"
            temp_f = (self.temp_data * 9/5) + 32
            self.temp_label.config(text=f"{temp_f:.1f}°F")
            self.toggle_button.config(text="Switch to °C")
        else:
            self.temp_unit = "C"
            self.temp_label.config(text=f"{self.temp_data:.1f}°C")
            self.toggle_button.config(text="Switch to °F")
        
        self.flash_update(self.temp_label)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()