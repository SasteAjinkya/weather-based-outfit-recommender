# weather_api.py
import requests
import json
import logging
from datetime import datetime
from config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAPI:
    def __init__(self):
        """Initialize Weather API handler."""
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = OPENWEATHER_BASE_URL

        if self.api_key == "YOUR_API_KEY_HERE":
            logger.warning("Please set your OpenWeatherMap API key in config.py")

    def get_weather_data(self, city, units='metric'):
        """
        Fetch weather data for a given city.

        Args:
            city (str): City name
            units (str): Temperature units ('metric', 'imperial', 'kelvin')

        Returns:
            dict: Weather data or None if error
        """
        try:
            # Build API URL
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                weather_data = response.json()
                logger.info(f"Successfully fetched weather data for {city}")
                return weather_data
            elif response.status_code == 401:
                logger.error("Invalid API key. Please check your OpenWeatherMap API key.")
                return None
            elif response.status_code == 404:
                logger.error(f"City '{city}' not found.")
                return None
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching weather data: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing weather data JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather data: {e}")
            return None

    def parse_weather_data(self, raw_data):
        """
        Parse raw weather data into a cleaner format.

        Args:
            raw_data (dict): Raw weather data from API

        Returns:
            dict: Parsed weather data
        """
        try:
            if not raw_data:
                return None

            parsed_data = {
                'city': raw_data.get('name', 'Unknown'),
                'country': raw_data.get('sys', {}).get('country', 'Unknown'),
                'temperature': round(raw_data.get('main', {}).get('temp', 0), 1),
                'feels_like': round(raw_data.get('main', {}).get('feels_like', 0), 1),
                'humidity': raw_data.get('main', {}).get('humidity', 0),
                'pressure': raw_data.get('main', {}).get('pressure', 0),
                'weather_main': raw_data.get('weather', [{}])[0].get('main', 'Unknown'),
                'weather_description': raw_data.get('weather', [{}])[0].get('description', 'Unknown'),
                'wind_speed': raw_data.get('wind', {}).get('speed', 0),
                'wind_direction': raw_data.get('wind', {}).get('deg', 0),
                'cloudiness': raw_data.get('clouds', {}).get('all', 0),
                'visibility': raw_data.get('visibility', 0),
                'sunrise': datetime.fromtimestamp(raw_data.get('sys', {}).get('sunrise', 0)).strftime('%H:%M:%S'),
                'sunset': datetime.fromtimestamp(raw_data.get('sys', {}).get('sunset', 0)).strftime('%H:%M:%S'),
                'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'raw_data': raw_data  # Keep original data for reference
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing weather data: {e}")
            return None

    def get_weather_condition_category(self, weather_main):
        """
        Categorize weather condition for outfit matching.

        Args:
            weather_main (str): Main weather condition from API

        Returns:
            str: Categorized weather condition
        """
        weather_main = weather_main.lower()

        if weather_main in ['rain', 'drizzle']:
            return 'rain'
        elif weather_main in ['thunderstorm']:
            return 'thunderstorm'
        elif weather_main in ['snow']:
            return 'snow'
        elif weather_main in ['clear']:
            return 'clear'
        elif weather_main in ['clouds']:
            return 'clouds'
        elif weather_main in ['mist', 'fog', 'haze']:
            return 'clouds'
        else:
            return 'clear'  # Default fallback

    def test_api_connection(self):
        """Test API connection with a simple request."""
        try:
            test_data = self.get_weather_data('London')
            if test_data:
                logger.info("✓ Weather API connection successful")
                return True
            else:
                logger.error("✗ Weather API connection failed")
                return False
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False

# Test the weather API
if __name__ == "__main__":
    weather_api = WeatherAPI()

    # Test with a sample city
    if weather_api.api_key != "YOUR_API_KEY_HERE":
        print("Testing Weather API...")
        raw_data = weather_api.get_weather_data('Mumbai')

        if raw_data:
            parsed_data = weather_api.parse_weather_data(raw_data)
            if parsed_data:
                print("✓ Weather API test successful")
                print(f"Sample data: {parsed_data['city']}, {parsed_data['temperature']}°C, {parsed_data['weather_description']}")
            else:
                print("✗ Failed to parse weather data")
        else:
            print("✗ Failed to fetch weather data")
    else:
        print("⚠ Please set your OpenWeatherMap API key in config.py to test the API")
