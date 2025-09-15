# Weather-Based Outfit Recommendation System

A Python-based application that provides outfit recommendations based on real-time weather conditions. The system fetches weather data from OpenWeatherMap API, stores data in MongoDB, and provides an intuitive Tkinter GUI for users.

## Features

- **Real-time Weather Data**: Fetches current weather conditions using OpenWeatherMap API
- **Intelligent Outfit Recommendations**: Suggests clothing based on temperature, humidity, and weather conditions
- **MongoDB Integration**: Stores weather data, outfit database, and recommendation history
- **User-friendly GUI**: Clean Tkinter interface for easy interaction
- **Modular Design**: Clean separation of concerns with separate modules for different functionalities
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Handling**: Robust error handling throughout the application

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Tkinter GUI   │    │  OpenWeatherMap  │    │    MongoDB      │
│     (ui.py)     │    │       API        │    │   Database      │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          │                      │                       │
    ┌─────▼──────────────────────▼───────────────────────▼─────┐
    │              Main Application Logic                      │
    │  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐   │
    │  │ Weather API │ │ Outfit       │ │ Database        │   │
    │  │ Handler     │ │ Recommender  │ │ Handler         │   │
    │  └─────────────┘ └──────────────┘ └─────────────────┘   │
    └──────────────────────────────────────────────────────────┘
```

## Installation and Setup

### Prerequisites

1. **Python 3.7+**: Make sure Python is installed on your system
2. **MongoDB**: Install and run MongoDB locally or use MongoDB Atlas
3. **OpenWeatherMap API Key**: Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)

### Step 1: Clone/Download the Project

Download all the project files to a folder on your computer.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pymongo requests pandas
```

### Step 3: MongoDB Setup

#### Option A: Local MongoDB
1. Install MongoDB Community Edition from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Start MongoDB service:
   - **Windows**: Start "MongoDB" service from Services
   - **Mac**: `brew services start mongodb-community`
   - **Linux**: `sudo systemctl start mongod`

#### Option B: MongoDB Atlas (Cloud)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster
3. Get your connection string
4. Update `MONGO_URI` in `config.py`

### Step 4: API Key Configuration

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Create a free account
3. Generate an API key
4. Open `config.py` and replace `YOUR_API_KEY_HERE` with your actual API key:

```python
OPENWEATHER_API_KEY = "your_actual_api_key_here"
```

### Step 5: Run the Application

```bash
python main.py
```

## File Structure

```
weather-outfit-system/
│
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── db_handler.py          # Database operations
├── weather_api.py         # Weather API handling
├── outfit_recommender.py  # Core recommendation logic
├── ui.py                  # Tkinter GUI interface
├── outfit_dataset.csv     # Clothing dataset
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
└── weather_outfit_app.log # Application log file (created at runtime)
```

## How to Use

1. **Start the Application**: Run `python main.py`
2. **Enter City Name**: Type a city name in the input field
3. **Get Recommendation**: Click "Get Recommendation" or press Enter
4. **View Results**: See weather information and outfit suggestions
5. **Additional Features**:
   - **View History**: See previous recommendations
   - **Clear Results**: Clear the current display
   - **Database Stats**: View database statistics

## Database Collections

The system creates three MongoDB collections:

### 1. weather_data
Stores raw weather API responses with timestamps.

```json
{
  "city": "Mumbai",
  "temperature": 28.5,
  "humidity": 75,
  "weather_description": "partly cloudy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. outfit_dataset
Contains clothing items with weather suitability criteria.

```json
{
  "clothing_type": "T-Shirt",
  "category": "Top",
  "temp_min": 20,
  "temp_max": 40,
  "humidity_min": 0,
  "humidity_max": 100,
  "weather_conditions": ["clear", "clouds"],
  "material": "cotton",
  "comfort_rating": 9
}
```

### 3. recommendations
Stores user queries and generated recommendations.

```json
{
  "city": "Mumbai",
  "weather": {...},
  "recommended_outfits": [...],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Outfit Recommendation Logic

The system recommends outfits based on:

1. **Temperature Range**: Each clothing item has min/max temperature suitability
2. **Humidity Levels**: Considers humidity for material recommendations
3. **Weather Conditions**: Matches weather (rain, snow, clear, clouds) with appropriate clothing
4. **Comfort Rating**: Prioritizes higher-rated items
5. **Completeness**: Ensures recommendations include essential categories (Top, Bottom, Footwear)

### Temperature Guidelines

- **< 0°C**: Heavy winter clothing, thermal layers
- **0-10°C**: Winter clothing, warm layers
- **10-20°C**: Light jackets, long sleeves
- **20-30°C**: Comfortable clothing, light fabrics
- **> 30°C**: Minimal, breathable clothing

## Troubleshooting

### Common Issues

1. **"Database connection failed"**
   - Ensure MongoDB is running
   - Check connection string in `config.py`
   - For Atlas: Check network access and credentials

2. **"Invalid API key"**
   - Verify your OpenWeatherMap API key in `config.py`
   - Ensure the API key is active (may take 10 minutes to 2 hours after creation)

3. **"City not found"**
   - Check city name spelling
   - Try using city, country format (e.g., "London, UK")

4. **"No outfit recommendations"**
   - Check if outfit dataset is loaded in database
   - Verify database connection
   - Try different weather conditions

### Log Files

Check `weather_outfit_app.log` for detailed error information and application behavior.

## Extending the System

### Adding New Clothing Items

1. **Database Method**: Add items directly to MongoDB
2. **CSV Method**: Update `outfit_dataset.csv` and restart the application
3. **GUI Method**: Create an admin interface (future enhancement)

### Adding New Weather Sources

1. Create a new API handler similar to `weather_api.py`
2. Update the recommender to use multiple sources
3. Modify the configuration to support multiple APIs

### Customizing UI

The Tkinter interface can be customized by modifying `ui.py`:
- Change colors, fonts, and layout
- Add new features like weather charts
- Implement different themes

## API Rate Limits

**OpenWeatherMap Free Tier**:
- 60 calls/minute
- 1,000 calls/day
- No historical data

For higher usage, consider upgrading to a paid plan.

