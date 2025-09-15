# db_handler.py
import pymongo
from pymongo import MongoClient
from datetime import datetime
import logging
import json
from config import MONGO_URI, DATABASE_NAME, WEATHER_COLLECTION, OUTFIT_COLLECTION, RECOMMENDATIONS_COLLECTION

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self):
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DATABASE_NAME]
            self.weather_collection = self.db[WEATHER_COLLECTION]
            self.outfit_collection = self.db[OUTFIT_COLLECTION]
            self.recommendations_collection = self.db[RECOMMENDATIONS_COLLECTION]
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def test_connection(self):
        """Test database connection."""
        try:
            # Test connection by pinging the server
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def insert_weather_data(self, weather_data):
        """Insert weather data into database."""
        try:
            # Add timestamp
            weather_data['timestamp'] = datetime.utcnow()
            result = self.weather_collection.insert_one(weather_data)
            logger.info(f"Weather data inserted with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting weather data: {e}")
            return None

    def insert_outfit_data(self, outfit_data):
        """Insert outfit data into database."""
        try:
            if isinstance(outfit_data, list):
                result = self.outfit_collection.insert_many(outfit_data)
                logger.info(f"Inserted {len(result.inserted_ids)} outfit records")
                return result.inserted_ids
            else:
                result = self.outfit_collection.insert_one(outfit_data)
                logger.info(f"Outfit data inserted with ID: {result.inserted_id}")
                return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting outfit data: {e}")
            return None

    def insert_recommendation(self, recommendation_data):
        """Insert recommendation into database."""
        try:
            # Add timestamp
            recommendation_data['timestamp'] = datetime.utcnow()
            result = self.recommendations_collection.insert_one(recommendation_data)
            logger.info(f"Recommendation inserted with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting recommendation: {e}")
            return None

    def get_weather_data(self, city=None, limit=10):
        """Retrieve weather data from database."""
        try:
            query = {}
            if city:
                query['name'] = city

            cursor = self.weather_collection.find(query).sort('timestamp', -1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error retrieving weather data: {e}")
            return []

    def get_suitable_outfits(self, temperature, humidity, weather_condition):
        """Get suitable outfits based on weather conditions."""
        try:
            # Build query for outfit matching
            query = {
                'temp_min': {'$lte': temperature},
                'temp_max': {'$gte': temperature},
                'humidity_min': {'$lte': humidity},
                'humidity_max': {'$gte': humidity}
            }

            # Filter by weather condition if specified
            if weather_condition:
                query['weather_conditions'] = weather_condition.lower()

            cursor = self.outfit_collection.find(query)
            outfits = list(cursor)

            # Sort by comfort rating (descending)
            outfits.sort(key=lambda x: x.get('comfort_rating', 0), reverse=True)

            return outfits[:10]  # Return top 10 matches
        except Exception as e:
            logger.error(f"Error getting suitable outfits: {e}")
            return []

    def get_recommendations_history(self, limit=10):
        """Get recommendation history."""
        try:
            cursor = self.recommendations_collection.find().sort('timestamp', -1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error retrieving recommendations history: {e}")
            return []

    def clear_collection(self, collection_name):
        """Clear a specific collection."""
        try:
            if collection_name == "weather":
                result = self.weather_collection.delete_many({})
            elif collection_name == "outfit":
                result = self.outfit_collection.delete_many({})
            elif collection_name == "recommendations":
                result = self.recommendations_collection.delete_many({})
            else:
                logger.error(f"Unknown collection: {collection_name}")
                return False

            logger.info(f"Cleared {result.deleted_count} documents from {collection_name} collection")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection {collection_name}: {e}")
            return False

    def get_collection_stats(self):
        """Get statistics about all collections."""
        try:
            stats = {
                'weather_count': self.weather_collection.count_documents({}),
                'outfit_count': self.outfit_collection.count_documents({}),
                'recommendations_count': self.recommendations_collection.count_documents({})
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    def close_connection(self):
        """Close database connection."""
        try:
            self.client.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

# Test the database handler
if __name__ == "__main__":
    db = DatabaseHandler()

    # Test connection
    if db.test_connection():
        print("✓ Database connection successful")

        # Get stats
        stats = db.get_collection_stats()
        print(f"Collection statistics: {stats}")
    else:
        print("✗ Database connection failed")

    db.close_connection()
