from flask import Flask, render_template, request, jsonify
from outfit_recommender import OutfitRecommender
from db_handler import DatabaseHandler
from bson import ObjectId
from datetime import datetime
import logging
from collections import defaultdict
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def serialize_doc(obj):
    """Recursively convert MongoDB documents so ObjectId and datetime are JSON serializable."""
    if isinstance(obj, list):
        return [serialize_doc(i) for i in obj]
    elif isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if isinstance(v, ObjectId):
                new_obj[k] = str(v)
            elif isinstance(v, datetime):
                new_obj[k] = v.isoformat()
            elif isinstance(v, (dict, list)):
                new_obj[k] = serialize_doc(v)
            else:
                new_obj[k] = v
        return new_obj
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

try:
    recommender = OutfitRecommender()
    db = DatabaseHandler()
    if not db.test_connection():
        logger.error("Failed to connect to MongoDB. Please check MONGO_URI in config.py")
        db = None
        recommender = None
    else:
        logger.info("MongoDB connection successful.")
except Exception as e:
    logger.exception(f"Exception during initialization: {e}")
    db = None
    recommender = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def get_recommendation():
    if recommender is None:
        return jsonify({'success': False, 'error': 'Database connection not established.'})
    try:
        data = request.get_json()
        city = data.get('city', '').strip()
        if not city:
            return jsonify({'success': False, 'error': 'Please enter a city name.'})
        result = recommender.get_weather_and_recommend(city)
        if result['success']:
            advice = recommender.get_weather_advice(result['weather'])
            result['advice'] = advice
        result_serialized = serialize_doc(result)
        return jsonify(result_serialized)
    except Exception as e:
        logger.exception(f"Error in /api/recommend: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/history')
def get_history():
    if db is None:
        return jsonify({'success': False, 'error': 'Database connection not established.'})
    try:
        history = db.get_recommendations_history(10)
        history_serialized = serialize_doc(history)
        return jsonify({'success': True, 'history': history_serialized})
    except Exception as e:
        logger.exception(f"Error in /api/history: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/db-stats')
def get_db_stats():
    if db is None:
        return jsonify({'success': False, 'error': 'Database connection not established.'})
    try:
        stats = db.get_collection_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.exception(f"Error in /api/db-stats: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/collections/<collection_name>')
def get_collection_data(collection_name):
    if db is None:
        return jsonify({'success': False, 'error': 'Database connection not established.'})
    try:
        if collection_name not in ['weather', 'outfit', 'recommendations']:
            return jsonify({'success': False, 'error': 'Invalid collection name.'})
        if collection_name == 'weather':
            data = db.get_weather_data(limit=50)
        elif collection_name == 'outfit':
            data = list(db.outfit_collection.find().limit(50))
        else:
            data = list(db.recommendations_collection.find().limit(50))
        data_serialized = serialize_doc(data)
        return jsonify({'success': True, 'data': data_serialized})
    except Exception as e:
        logger.exception(f"Error in /api/collections/{collection_name}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/collections/<collection_name>', methods=['POST'])
def add_record(collection_name):
    if db is None:
        return jsonify({'success': False, 'error': 'Database connection not established.'})
    try:
        if collection_name not in ['weather', 'outfit', 'recommendations']:
            return jsonify({'success': False, 'error': 'Invalid collection name.'})
        data = request.get_json()
        record = data.get('record', {})
        col = get_collection(collection_name)
        result = col.insert_one(record)
        return jsonify({'success': True, 'message': f'Record inserted with ID: {str(result.inserted_id)}'})
    except Exception as e:
        logger.exception(f"Error in add_record: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/collections/<collection_name>/<record_id>', methods=['PUT'])
def update_record(collection_name, record_id):
    if db is None:
        return jsonify({'success': False, 'error': 'Database connection not established.'})
    try:
        if collection_name not in ['weather', 'outfit', 'recommendations']:
            return jsonify({'success': False, 'error': 'Invalid collection name.'})
        data = request.get_json()
        record = data.get('record', {})
        if '_id' in record:
            del record['_id']
        col = get_collection(collection_name)
        result = col.update_one({'_id': ObjectId(record_id)}, {'$set': record})
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Record updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'No record found or no changes made'})
    except Exception as e:
        logger.exception(f"Error in update_record: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/collections/<collection_name>/<record_id>', methods=['DELETE'])
def delete_record(collection_name, record_id):
    if db is None:
        return jsonify({'success': False, 'error': 'Database connection not established.'})
    try:
        if collection_name not in ['weather', 'outfit', 'recommendations']:
            return jsonify({'success': False, 'error': 'Invalid collection name.'})
        col = get_collection(collection_name)
        result = col.delete_one({'_id': ObjectId(record_id)})
        if result.deleted_count > 0:
            return jsonify({'success': True, 'message': 'Record deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Record not found'})
    except Exception as e:
        logger.exception(f"Error in delete_record: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/visualization/heatmap')
def get_heatmap_data():
    if db is None:
        return jsonify({'success': False, 'error': 'Database connection not established.'})
    try:
        data = list(db.recommendations_collection.find().limit(200))
        if not data:
            return jsonify({'success': False, 'error': 'No recommendation data found.'})
        
        category_set = set()
        weather_set = set()
        counts = {}

        for rec in data:
            # Defensive Check 1: Ensure the record is a dictionary
            if not isinstance(rec, dict):
                logger.warning("Skipping malformed record (not a dict).")
                continue

            # Defensive Check 2: Ensure 'weather' field is a dictionary
            weather_data = rec.get('weather', {})
            if not isinstance(weather_data, dict):
                logger.warning(f"Skipping record with malformed 'weather' field (ID: {rec.get('_id')})")
                continue
            
            weather_cond = weather_data.get('weather_main', 'Unknown')
            weather_cond = weather_cond.capitalize() if weather_cond else 'Unknown'
            weather_set.add(weather_cond)

            # Defensive Check 3: Ensure 'recommended_outfits' is a list
            recommended_outfits = rec.get('recommended_outfits', [])
            if not isinstance(recommended_outfits, list):
                logger.warning(f"Skipping record with malformed 'recommended_outfits' field (ID: {rec.get('_id')})")
                continue

            for group in recommended_outfits:
                # Defensive Check 4: Ensure each 'group' is a dictionary
                if not isinstance(group, dict):
                    logger.warning(f"Skipping malformed outfit group in record (ID: {rec.get('_id')})")
                    continue
                
                items_list = group.get('items', [])
                if not isinstance(items_list, list):
                    logger.warning(f"Skipping malformed 'items' list in group (Record ID: {rec.get('_id')})")
                    continue

                for item in items_list:
                    # Defensive Check 5: Ensure each 'item' is a dictionary
                    if not isinstance(item, dict):
                        logger.warning(f"Skipping malformed item in group (Record ID: {rec.get('_id')})")
                        continue
                        
                    category = item.get('category', 'Unknown')
                    category = category.capitalize() if category else 'Unknown'
                    category_set.add(category)
                    
                    key = f"{category}|{weather_cond}"
                    counts[key] = counts.get(key, 0) + 1
        
        if not category_set or not weather_set:
            return jsonify({'success': False, 'error': 'Not enough data to generate heatmap.'})
        
        categories = sorted(list(category_set))
        weathers = sorted(list(weather_set))
        
        matrix_data = []
        for c in categories:
            row = [counts.get(f"{c}|{w}", 0) for w in weathers]
            matrix_data.append(row)
            
        return jsonify({
            'success': True,
            'categories': categories,
            'weathers': weathers,
            'data': matrix_data,
            'total_records': len(data)
        })

    except Exception as e:
        logger.exception(f"Error generating heatmap data: {e}")
        return jsonify({'success': False, 'error': str(e)})

def get_collection(collection_name):
    if collection_name == 'weather':
        return db.weather_collection
    elif collection_name == 'outfit':
        return db.outfit_collection
    else:
        return db.recommendations_collection

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
