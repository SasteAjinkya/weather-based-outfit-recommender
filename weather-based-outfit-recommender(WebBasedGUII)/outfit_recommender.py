# outfit_recommender.py
import logging
from datetime import datetime
from db_handler import DatabaseHandler
from weather_api import WeatherAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutfitRecommender:
    def __init__(self):
        """Initialize the outfit recommender system."""
        self.db = DatabaseHandler()
        self.weather_api = WeatherAPI()

    def get_weather_and_recommend(self, city):
        """
        Get weather data and generate outfit recommendations.

        Args:
            city (str): City name

        Returns:
            dict: Complete recommendation data
        """
        try:
            # Step 1: Fetch weather data
            logger.info(f"Fetching weather data for {city}")
            raw_weather = self.weather_api.get_weather_data(city)

            if not raw_weather:
                return {
                    'success': False,
                    'error': f'Could not fetch weather data for {city}',
                    'weather': None,
                    'outfits': []
                }

            # Step 2: Parse weather data
            weather_data = self.weather_api.parse_weather_data(raw_weather)

            if not weather_data:
                return {
                    'success': False,
                    'error': 'Could not parse weather data',
                    'weather': None,
                    'outfits': []
                }

            # Step 3: Store weather data in database
            self.db.insert_weather_data(weather_data)

            # Step 4: Get outfit recommendations
            outfits = self.recommend_outfits(
                temperature=weather_data['temperature'],
                humidity=weather_data['humidity'],
                weather_condition=weather_data['weather_main']
            )

            # Step 5: Create recommendation record
            recommendation_data = {
                'city': city,
                'weather': weather_data,
                'recommended_outfits': outfits,
                'recommendation_count': len(outfits)
            }

            # Step 6: Store recommendation in database
            self.db.insert_recommendation(recommendation_data)

            return {
                'success': True,
                'weather': weather_data,
                'outfits': outfits,
                'recommendation_data': recommendation_data
            }

        except Exception as e:
            logger.error(f"Error in get_weather_and_recommend: {e}")
            return {
                'success': False,
                'error': str(e),
                'weather': None,
                'outfits': []
            }

    def recommend_outfits(self, temperature, humidity, weather_condition):
        """
        Recommend outfits based on weather conditions.

        Args:
            temperature (float): Temperature in Celsius
            humidity (int): Humidity percentage
            weather_condition (str): Weather condition

        Returns:
            list: List of recommended outfits
        """
        try:
            # Get weather condition category for matching
            weather_category = self.weather_api.get_weather_condition_category(weather_condition)

            # Get suitable outfits from database
            outfits = self.db.get_suitable_outfits(temperature, humidity, weather_category)

            if not outfits:
                logger.warning(f"No outfits found for T:{temperature}°C, H:{humidity}%, W:{weather_category}")
                return []

            # Group outfits by category for a complete outfit
            outfit_by_category = {}
            for outfit in outfits:
                category = outfit['category']
                if category not in outfit_by_category:
                    outfit_by_category[category] = []
                outfit_by_category[category].append(outfit)

            # Build recommended outfit combinations
            recommendations = []

            # Ensure we have essential categories
            essential_categories = ['Top', 'Bottom', 'Footwear']

            # Create outfit combinations
            if all(cat in outfit_by_category for cat in essential_categories):
                # Complete outfit recommendation
                complete_outfit = {
                    'outfit_type': 'Complete Outfit',
                    'items': []
                }

                # Add top-rated item from each essential category
                for cat in essential_categories:
                    if outfit_by_category[cat]:
                        best_item = max(outfit_by_category[cat], key=lambda x: x.get('comfort_rating', 0))
                        complete_outfit['items'].append(best_item)

                # Add outerwear if needed (cold or rainy weather)
                if temperature < 15 or weather_category in ['rain', 'snow']:
                    if 'Outerwear' in outfit_by_category:
                        best_outerwear = max(outfit_by_category['Outerwear'], key=lambda x: x.get('comfort_rating', 0))
                        complete_outfit['items'].append(best_outerwear)

                # Add accessories based on weather
                if 'Accessory' in outfit_by_category:
                    for accessory in outfit_by_category['Accessory'][:2]:  # Max 2 accessories
                        complete_outfit['items'].append(accessory)

                recommendations.append(complete_outfit)

            # Also provide individual category recommendations
            for category, items in outfit_by_category.items():
                if items:
                    category_rec = {
                        'outfit_type': f'{category} Recommendations',
                        'items': items[:3]  # Top 3 in each category
                    }
                    recommendations.append(category_rec)

            return recommendations

        except Exception as e:
            logger.error(f"Error recommending outfits: {e}")
            return []

    def get_outfit_summary(self, recommendations):
        """
        Generate a text summary of outfit recommendations.

        Args:
            recommendations (list): List of outfit recommendations

        Returns:
            str: Text summary
        """
        try:
            if not recommendations:
                return "No outfit recommendations available."

            summary_parts = []

            for rec in recommendations:
                if rec['outfit_type'] == 'Complete Outfit':
                    outfit_names = [item['clothing_type'] for item in rec['items']]
                    summary_parts.append(f"Complete Outfit: {', '.join(outfit_names)}")
                    break  # Show only the complete outfit in summary

            if not summary_parts:
                # If no complete outfit, show top items from each category
                for rec in recommendations[:3]:  # Show first 3 categories
                    if rec['items']:
                        top_item = rec['items'][0]['clothing_type']
                        summary_parts.append(f"{rec['outfit_type']}: {top_item}")

            return "\n".join(summary_parts)

        except Exception as e:
            logger.error(f"Error generating outfit summary: {e}")
            return "Error generating outfit summary."

    def get_weather_advice(self, weather_data):
        """
        Generate weather-specific advice.

        Args:
            weather_data (dict): Weather data

        Returns:
            str: Weather advice
        """
        try:
            advice = []

            temp = weather_data['temperature']
            humidity = weather_data['humidity']
            condition = weather_data['weather_main'].lower()

            # Temperature advice
            if temp < 0:
                advice.append("Very cold! Dress in layers and cover exposed skin.")
            elif temp < 10:
                advice.append("Cold weather. Wear warm clothing and consider layers.")
            elif temp < 20:
                advice.append("Cool weather. Light layers recommended.")
            elif temp < 30:
                advice.append("Comfortable temperature. Light clothing is fine.")
            else:
                advice.append("Hot weather! Stay cool with light, breathable fabrics.")

            # Humidity advice
            if humidity > 80:
                advice.append("High humidity. Choose breathable, moisture-wicking materials.")
            elif humidity < 30:
                advice.append("Low humidity. Consider moisturizing and stay hydrated.")

            # Weather condition advice
            if condition in ['rain', 'drizzle']:
                advice.append("Rainy weather. Don't forget waterproof clothing and umbrella!")
            elif condition == 'snow':
                advice.append("Snowy conditions. Wear waterproof boots and warm layers.")
            elif condition == 'thunderstorm':
                advice.append("Thunderstorm expected. Stay indoors if possible, carry rain gear.")
            elif condition == 'clear' and temp > 25:
                advice.append("Sunny and warm. Consider sun protection (hat, sunglasses).")

            return " ".join(advice)

        except Exception as e:
            logger.error(f"Error generating weather advice: {e}")
            return "Stay comfortable and dress appropriately for the weather!"

    def close(self):
        """Close database connection."""
        self.db.close_connection()

# Test the outfit recommender
if __name__ == "__main__":
    recommender = OutfitRecommender()

    # Test with a sample city
    print("Testing Outfit Recommender...")
    result = recommender.get_weather_and_recommend('Mumbai')

    if result['success']:
        print("✓ Outfit recommendation test successful")
        weather = result['weather']
        print(f"Weather: {weather['city']}, {weather['temperature']}°C, {weather['weather_description']}")
        print(f"Outfit recommendations: {len(result['outfits'])} categories found")

        # Show summary
        summary = recommender.get_outfit_summary(result['outfits'])
        print(f"Summary: {summary}")

        # Show advice
        advice = recommender.get_weather_advice(weather)
        print(f"Advice: {advice}")
    else:
        print(f"✗ Test failed: {result.get('error', 'Unknown error')}")

    recommender.close()
