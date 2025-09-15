# Weather-Based Outfit Recommendation System - Web Version

## Project Structure
```
/your-project-folder/
│
├── app.py                 # Flask web application
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Premium Apple-like styling
│   ├── js/
│   │   └── app.js        # Frontend JavaScript functionality
│   ├── images/           # Place weather icons here
│   └── icons/            # Additional icons
│
├── db_handler.py         # Your existing database handler
├── outfit_recommender.py # Your existing recommendation logic
├── config.py            # Your existing configuration
└── main.py              # Your existing main file (for desktop version)
```

## Installation & Setup

### 1. Install Required Python Packages
```bash
pip install flask flask-cors
```

### 2. Run the Web Application
```bash
python app.py
```

### 3. Access the Application
Open your browser and navigate to: `http://localhost:5000`

## Features

### ✨ Premium UI Design
- **Glassmorphism Design**: Modern glass-like elements with blur effects
- **Apple-inspired Colors**: Premium color palette matching Apple's design language
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Smooth Animations**: Subtle transitions and hover effects

### 🌟 Core Functionality (Preserved from Desktop Version)

#### Tab 1: Outfit Recommendation
- City input with weather data fetching
- Real-time weather information display
- Outfit recommendations with ratings and details
- Weather advice based on conditions
- View recommendation history
- Clear results functionality
- Database statistics

#### Tab 2: Collection Data Viewer (CRUD Operations)
- View collections: Weather, Outfit, Recommendations
- **Create**: Add new records to any collection
- **Read**: Browse and search through records
- **Update**: Edit existing records
- **Delete**: Remove selected records
- Responsive data table with sorting
- Bulk operations support

#### Tab 3: Visual Analytics
- Interactive heatmap visualization
- Outfit category popularity by weather condition
- Real-time data refresh
- Chart.js integration for smooth rendering

### 🔧 Technical Features
- **RESTful API**: Clean API endpoints for all operations
- **Real-time Updates**: Asynchronous operations with loading indicators
- **Error Handling**: Comprehensive error messages and user feedback
- **Data Validation**: Input validation and sanitization
- **Cross-browser Compatibility**: Works on all modern browsers

## API Endpoints

### Outfit Recommendations
- `POST /api/recommend` - Get outfit recommendations for a city
- `GET /api/history` - Get recommendation history
- `GET /api/db-stats` - Get database statistics

### Collection Management
- `GET /api/collections/<collection_name>` - Get collection data
- `POST /api/collections/<collection_name>` - Add new record
- `PUT /api/collections/<collection_name>/<record_id>` - Update record
- `DELETE /api/collections/<collection_name>/<record_id>` - Delete record

### Analytics
- `GET /api/visualization/heatmap` - Get heatmap data for visualization

## Customization

### Colors & Styling
Edit `static/css/style.css` to customize:
- Color schemes
- Glass effect intensity
- Border radius and shadows
- Typography and spacing

### Functionality
Edit `static/js/app.js` to add:
- New interactive features
- Additional chart types
- Custom data processing
- Enhanced user interactions

### Backend Logic
The Flask app (`app.py`) uses your existing:
- `db_handler.py` for database operations
- `outfit_recommender.py` for recommendation logic
- `config.py` for configuration settings

## Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Mobile Responsiveness
The interface automatically adapts to different screen sizes:
- **Desktop**: Full three-column layout with side panels
- **Tablet**: Stacked layout with collapsible sections  
- **Mobile**: Single-column layout with touch-friendly controls

## Notes
- Ensure MongoDB is running and accessible
- Configure your OpenWeatherMap API key in `config.py`
- Place weather icon files (sun.png, rain.png, etc.) in `static/images/`
- The web version maintains 100% feature parity with your desktop Tkinter application