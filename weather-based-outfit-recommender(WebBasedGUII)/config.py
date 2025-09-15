# config.py
import os

# OpenWeatherMap API Configuration
OPENWEATHER_API_KEY = "Your Api Key"  # Replace with your actual API key
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "weather_outfit_db"

# Collections
WEATHER_COLLECTION = "weather_data"
OUTFIT_COLLECTION = "outfit_dataset"
RECOMMENDATIONS_COLLECTION = "recommendations"

# UI Configuration
APP_TITLE = "Weather-Based Outfit Recommendation System"
WINDOW_SIZE = "800x600"

# Temperature conversion
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9
