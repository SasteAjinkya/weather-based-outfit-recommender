# main.py
"""
Weather-Based Outfit Recommendation System
Main application entry point

This system provides outfit recommendations based on current weather conditions.
It fetches weather data from OpenWeatherMap API, stores data in MongoDB,
and provides recommendations through a Tkinter GUI.
"""

import sys
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_outfit_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = [
        'tkinter', 'pymongo', 'requests', 'pandas'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        logger.error(f"Missing required modules: {missing_modules}")
        print("Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install missing modules using:")
        print("pip install pymongo requests pandas")
        return False

    return True

def setup_database():
    """Initialize database with outfit dataset."""
    try:
        from db_handler import DatabaseHandler
        import pandas as pd

        db = DatabaseHandler()

        # Check if outfit dataset exists in database
        stats = db.get_collection_stats()
        if stats.get('outfit_count', 0) == 0:
            logger.info("Loading outfit dataset into database...")

            # Load outfit dataset from CSV
            if os.path.exists('outfit_dataset.csv'):
                df = pd.read_csv('outfit_dataset.csv')

                # Convert DataFrame to list of dictionaries
                outfit_data = df.to_dict('records')

                # Convert weather_conditions from string to list
                for item in outfit_data:
                    if isinstance(item.get('weather_conditions'), str):
                        # Remove brackets and quotes, then split
                        conditions_str = item['weather_conditions'].strip('[]').replace("'", "")
                        item['weather_conditions'] = [cond.strip() for cond in conditions_str.split(',')]

                # Insert into database
                result = db.insert_outfit_data(outfit_data)
                if result:
                    logger.info(f"Successfully loaded {len(outfit_data)} outfit items into database")
                else:
                    logger.error("Failed to load outfit dataset into database")
            else:
                logger.warning("outfit_dataset.csv not found. Creating sample data...")
                # Create minimal sample data if CSV doesn't exist
                sample_data = [
                    {
                        "clothing_type": "T-Shirt",
                        "category": "Top",
                        "temp_min": 20,
                        "temp_max": 40,
                        "humidity_min": 0,
                        "humidity_max": 100,
                        "weather_conditions": ["clear", "clouds"],
                        "season": "summer",
                        "material": "cotton",
                        "comfort_rating": 9
                    },
                    {
                        "clothing_type": "Jeans",
                        "category": "Bottom",
                        "temp_min": 10,
                        "temp_max": 30,
                        "humidity_min": 0,
                        "humidity_max": 100,
                        "weather_conditions": ["clear", "clouds"],
                        "season": "all",
                        "material": "denim",
                        "comfort_rating": 8
                    }
                ]
                db.insert_outfit_data(sample_data)
                logger.info("Created sample outfit data")

        db.close_connection()
        return True

    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        return False

def check_configuration():
    """Check if configuration is properly set."""
    try:
        from config import OPENWEATHER_API_KEY, MONGO_URI

        if OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
            logger.warning("OpenWeatherMap API key not configured!")
            print("\n⚠ WARNING: OpenWeatherMap API key not configured!")
            print("Please follow these steps:")
            print("1. Go to https://openweathermap.org/api")
            print("2. Create a free account")
            print("3. Generate an API key")
            print("4. Edit config.py and replace 'YOUR_API_KEY_HERE' with your API key")
            print("\nThe application will still run, but weather data fetching will fail.")
            print("You can test the UI and database functionality without the API key.\n")

        return True

    except ImportError as e:
        logger.error(f"Configuration import error: {e}")
        return False

def main():
    """Main application function."""
    print("=" * 60)
    print("Weather-Based Outfit Recommendation System")
    print("=" * 60)
    print(f"Starting application at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        print("✗ Dependency check failed. Please install missing modules.")
        return False
    print("✓ All dependencies are available")

    # Step 2: Check configuration
    print("\n2. Checking configuration...")
    if not check_configuration():
        print("✗ Configuration check failed.")
        return False
    print("✓ Configuration checked")

    # Step 3: Setup database
    print("\n3. Setting up database...")
    if not setup_database():
        print("✗ Database setup failed. Please check MongoDB connection.")
        return False
    print("✓ Database setup completed")

    # Step 4: Start GUI application
    print("\n4. Starting GUI application...")
    try:
        from ui import WeatherOutfitUI

        app = WeatherOutfitUI()
        print("✓ GUI initialized successfully")
        print("\n" + "=" * 60)
        print("Application is ready!")
        print("Close the GUI window to exit the application.")
        print("=" * 60)

        app.run()

    except Exception as e:
        logger.error(f"Failed to start GUI: {e}")
        print(f"✗ Failed to start GUI: {e}")
        return False

    print(f"\nApplication closed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            logger.info("Application completed successfully")
        else:
            logger.error("Application failed to start")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(1)
