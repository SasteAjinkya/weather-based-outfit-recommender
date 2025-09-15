# test_system.py - System testing script
"""
Simple test script to verify all components are working correctly.
Run this after setting up the system to check functionality.
"""

import sys
import traceback
from datetime import datetime

def test_imports():
    """Test if all modules can be imported."""
    print("Testing imports...")

    try:
        import config
        import db_handler
        import weather_api
        import outfit_recommender
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database connection and operations."""
    print("\nTesting database connection...")

    try:
        from db_handler import DatabaseHandler

        db = DatabaseHandler()

        # Test connection
        if not db.test_connection():
            print("✗ Database connection failed")
            return False

        # Test basic operations
        stats = db.get_collection_stats()
        print(f"✓ Database connected. Collections: {stats}")

        db.close_connection()
        return True

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_weather_api():
    """Test weather API connection."""
    print("\nTesting weather API...")

    try:
        from weather_api import WeatherAPI
        from config import OPENWEATHER_API_KEY

        if OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
            print("⚠ API key not configured, skipping weather API test")
            return True

        weather_api = WeatherAPI()

        # Test with a known city
        result = weather_api.get_weather_data('London')

        if result:
            parsed = weather_api.parse_weather_data(result)
            if parsed:
                print(f"✓ Weather API test successful: {parsed['city']}, {parsed['temperature']}°C")
                return True
            else:
                print("✗ Weather data parsing failed")
                return False
        else:
            print("✗ Weather API request failed")
            return False

    except Exception as e:
        print(f"✗ Weather API test failed: {e}")
        return False

def test_outfit_recommendation():
    """Test outfit recommendation system."""
    print("\nTesting outfit recommendation system...")

    try:
        from outfit_recommender import OutfitRecommender
        from config import OPENWEATHER_API_KEY

        recommender = OutfitRecommender()

        if OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
            print("⚠ API key not configured, testing with mock data")

            # Test with direct parameters
            outfits = recommender.recommend_outfits(
                temperature=25,
                humidity=60,
                weather_condition='clear'
            )

            if outfits:
                print(f"✓ Outfit recommendation test successful: {len(outfits)} recommendations")
                return True
            else:
                print("✗ No outfit recommendations generated")
                return False
        else:
            # Test with real API call
            result = recommender.get_weather_and_recommend('Mumbai')

            if result['success']:
                print(f"✓ Full system test successful: {len(result['outfits'])} outfit groups")
                return True
            else:
                print(f"✗ System test failed: {result.get('error', 'Unknown error')}")
                return False

        recommender.close()

    except Exception as e:
        print(f"✗ Outfit recommendation test failed: {e}")
        traceback.print_exc()
        return False

def test_gui():
    """Test if GUI can be initialized (without actually showing it)."""
    print("\nTesting GUI components...")

    try:
        import tkinter as tk

        # Test basic tkinter functionality
        root = tk.Tk()
        root.withdraw()  # Hide the window

        # Try importing UI components
        from ui import WeatherOutfitUI

        root.destroy()
        print("✓ GUI components test successful")
        return True

    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Weather-Based Outfit Recommendation System")
    print("System Test Script")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Module Imports", test_imports),
        ("Database Connection", test_database),
        ("Weather API", test_weather_api),
        ("Outfit Recommendation", test_outfit_recommendation),
        ("GUI Components", test_gui)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1

    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("You can now run: python main.py")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the setup.")
        print("Common solutions:")
        print("- Ensure MongoDB is running")
        print("- Set your OpenWeatherMap API key in config.py")
        print("- Install all dependencies: pip install -r requirements.txt")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)
