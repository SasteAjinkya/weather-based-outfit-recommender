// Main Application JavaScript
class WeatherOutfitApp {
    constructor() {
        this.currentData = null;
        this.selectedRecords = new Set();
        this.heatmapChart = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateTime();
        this.checkConnection();
        
        // Update time every second
        setInterval(() => this.updateTime(), 1000);
    }

    setupEventListeners() {
        // Recommendation form
        document.getElementById('recommendationForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.getRecommendation();
        });

        // Recommendation tab buttons
        document.getElementById('viewHistoryBtn').addEventListener('click', () => this.showHistory());
        document.getElementById('clearResultsBtn').addEventListener('click', () => this.clearResults());
        document.getElementById('dbStatsBtn').addEventListener('click', () => this.showDbStats());

        // Collection tab buttons
        document.getElementById('loadDataBtn').addEventListener('click', () => this.loadCollectionData());
        document.getElementById('addRecordBtn').addEventListener('click', () => this.showAddRecordModal());
        document.getElementById('editRecordBtn').addEventListener('click', () => this.showEditRecordModal());
        document.getElementById('deleteRecordBtn').addEventListener('click', () => this.deleteSelectedRecords());

        // Analytics tab buttons
        document.getElementById('refreshHeatmapBtn').addEventListener('click', () => this.loadHeatmap());

        // Modal buttons
        document.getElementById('saveRecordBtn').addEventListener('click', () => this.saveRecord());

        // Tab change events
        document.querySelectorAll('button[data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const target = e.target.getAttribute('data-bs-target');
                if (target === '#analytics') {
                    // Delay to ensure canvas is visible
                    setTimeout(() => this.loadHeatmap(), 100);
                }
            });
        });
    }

    // Utility Methods
    updateTime() {
        const now = new Date();
        document.getElementById('currentTime').textContent = now.toLocaleTimeString();
    }

    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('statusText');
        const timestamp = new Date().toLocaleTimeString();
        statusElement.textContent = `${timestamp} - ${message}`;
        
        // Update status color based on type
        statusElement.className = `text-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'muted'}`;
    }

    async checkConnection() {
        try {
            const response = await fetch('/api/db-stats');
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('connection-status').innerHTML = 
                    '<i class="fas fa-circle me-1"></i>Connected';
                document.getElementById('connection-status').className = 'badge bg-success';
                this.updateStatus('Database connected successfully', 'success');
            } else {
                throw new Error('Database connection failed');
            }
        } catch (error) {
            document.getElementById('connection-status').innerHTML = 
                '<i class="fas fa-circle me-1"></i>Disconnected';
            document.getElementById('connection-status').className = 'badge bg-danger';
            this.updateStatus('Database connection failed', 'error');
        }
    }

    // Recommendation Methods
    async getRecommendation() {
        const city = document.getElementById('cityInput').value.trim();
        if (!city) {
            this.showAlert('Please enter a city name', 'warning');
            return;
        }

        const loadingIndicator = document.getElementById('loadingIndicator');
        const getBtn = document.getElementById('getRecommendationBtn');
        
        // Show loading state
        loadingIndicator.style.display = 'block';
        getBtn.disabled = true;
        this.updateStatus('Fetching weather data and generating recommendations...', 'info');

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city })
            });

            const data = await response.json();
            
            if (data.success) {
                this.displayWeatherInfo(data.weather);
                this.displayRecommendations(data.outfits, data.advice);
                this.updateStatus(`Generated ${data.outfits.length} outfit recommendations`, 'success');
            } else {
                this.displayError(data.error);
                this.updateStatus(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            this.displayError(`Network error: ${error.message}`);
            this.updateStatus(`Error: ${error.message}`, 'error');
        } finally {
            loadingIndicator.style.display = 'none';
            getBtn.disabled = false;
        }
    }

    displayWeatherInfo(weather) {
        const weatherInfo = document.getElementById('weatherInfo');
        
        weatherInfo.innerHTML = `
            <div class="row align-items-center">
                <div class="col-auto">
                    <div class="weather-icon">
                        <i class="fas fa-${this.getWeatherIcon(weather.weather_main)}"></i>
                    </div>
                </div>
                <div class="col">
                    <h5 class="mb-1">${weather.city}, ${weather.country}</h5>
                    <p class="mb-1">
                        <strong>${weather.temperature}°C</strong> 
                        <span class="text-muted">(feels like ${weather.feels_like}°C)</span>
                    </p>
                    <p class="mb-0 text-muted">
                        ${weather.weather_description} • Humidity: ${weather.humidity}%
                    </p>
                </div>
            </div>
        `;
    }

    displayRecommendations(outfits, advice) {
        const resultsDiv = document.getElementById('recommendationResults');
        
        if (!outfits || outfits.length === 0) {
            resultsDiv.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-info-circle fa-2x text-muted mb-3"></i>
                    <p class="text-muted">No suitable outfits found for current weather conditions.</p>
                    <p class="text-muted">Try adding more clothing items to the database.</p>
                </div>
            `;
            return;
        }

        let html = '';
        
        if (advice) {
            html += `
                <div class="alert alert-info glass-card">
                    <h6><i class="fas fa-lightbulb me-2"></i>Weather Advice</h6>
                    <p class="mb-0">${advice}</p>
                </div>
            `;
        }

        outfits.forEach(group => {
            html += `
                <div class="outfit-group">
                    <h6 class="mb-3"><i class="fas fa-tags me-2"></i>${group.outfit_type}</h6>
                    <div class="row g-2">
            `;
            
            group.items.forEach(item => {
                html += `
                    <div class="col-md-6">
                        <div class="outfit-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <strong>${item.clothing_type}</strong>
                                    <span class="badge bg-secondary ms-2">${item.category}</span>
                                </div>
                                <div class="text-end">
                                    <div class="text-warning">
                                        ${'★'.repeat(Math.floor(item.comfort_rating / 2))}
                                    </div>
                                    <small class="text-muted">${item.comfort_rating}/10</small>
                                </div>
                            </div>
                            <small class="text-muted d-block mt-1">
                                Material: ${item.material || 'N/A'} • 
                                Temp: ${item.temp_min}°C - ${item.temp_max}°C
                            </small>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });

        resultsDiv.innerHTML = html;
    }

    displayError(error) {
        const weatherInfo = document.getElementById('weatherInfo');
        const resultsDiv = document.getElementById('recommendationResults');
        
        weatherInfo.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>Error fetching weather data
            </div>
        `;
        
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <h6>Error: ${error}</h6>
                <p class="mb-0">Please check:</p>
                <ul class="mb-0">
                    <li>Internet connection</li>
                    <li>City name spelling</li>
                    <li>API key configuration</li>
                    <li>Database connection</li>
                </ul>
            </div>
        `;
    }

    getWeatherIcon(condition) {
        const iconMap = {
            'clear': 'sun',
            'clouds': 'cloud',
            'rain': 'cloud-rain',
            'drizzle': 'cloud-drizzle',
            'thunderstorm': 'bolt',
            'snow': 'snowflake',
            'mist': 'smog',
            'fog': 'smog'
        };
        return iconMap[condition.toLowerCase()] || 'cloud';
    }

    async showHistory() {
        const modal = new bootstrap.Modal(document.getElementById('historyModal'));
        const historyContent = document.getElementById('historyContent');
        
        // Show loading
        historyContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        modal.show();

        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            if (data.success && data.history.length > 0) {
                let html = '<div class="list-group list-group-flush">';
                
                data.history.forEach((record, index) => {
                    const timestamp = new Date(record.timestamp).toLocaleString();
                    const weather = record.weather || {};
                    
                    html += `
                        <div class="list-group-item glass-card mb-2">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${index + 1}. ${record.city || 'Unknown City'}</h6>
                                    <p class="mb-1">
                                        Weather: ${weather.temperature || 'N/A'}°C, 
                                        ${weather.weather_description || 'N/A'}
                                    </p>
                                    <small class="text-muted">
                                        Recommendations: ${record.recommendation_count || 0} outfit groups
                                    </small>
                                </div>
                                <small class="text-muted">${timestamp}</small>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                historyContent.innerHTML = html;
            } else {
                historyContent.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-history fa-2x text-muted mb-3"></i>
                        <p class="text-muted">No recommendation history found.</p>
                    </div>
                `;
            }
        } catch (error) {
            historyContent.innerHTML = `
                <div class="alert alert-danger">
                    Error loading history: ${error.message}
                </div>
            `;
        }
    }

    clearResults() {
        document.getElementById('weatherInfo').innerHTML = 
            '<p class="text-muted">Enter a city and click \'Get Recommendation\' to see weather information</p>';
        document.getElementById('recommendationResults').innerHTML = 
            '<p class="text-muted">Your outfit recommendations will appear here</p>';
        this.updateStatus('Results cleared', 'info');
    }

    async showDbStats() {
        try {
            const response = await fetch('/api/db-stats');
            const data = await response.json();
            
            if (data.success) {
                const stats = data.stats;
                const message = `Database Statistics:\n\nWeather records: ${stats.weather_count || 0}\nOutfit items: ${stats.outfit_count || 0}\nRecommendations: ${stats.recommendations_count || 0}`;
                alert(message);
            } else {
                alert('Failed to load database statistics');
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    // Collection Methods
    async loadCollectionData() {
        const collection = document.getElementById('collectionSelect').value;
        const loadBtn = document.getElementById('loadDataBtn');
        const statusDiv = document.getElementById('collectionStatus');
        const tableBody = document.querySelector('#collectionTable tbody');
        const tableHead = document.querySelector('#collectionTable thead');
        
        loadBtn.disabled = true;
        statusDiv.textContent = 'Loading data...';
        this.selectedRecords.clear();

        try {
            const response = await fetch(`/api/collections/${collection}`);
            const data = await response.json();
            
            if (data.success && data.data.length > 0) {
                this.currentData = data.data;
                this.renderTable(data.data);
                statusDiv.textContent = `Loaded ${data.data.length} records from '${collection}' collection.`;
            } else {
                tableHead.innerHTML = '';
                tableBody.innerHTML = '<tr><td colspan="100%" class="text-center text-muted">No data found</td></tr>';
                statusDiv.textContent = 'No data found.';
            }
        } catch (error) {
            statusDiv.textContent = `Error loading data: ${error.message}`;
        } finally {
            loadBtn.disabled = false;
        }
    }

    renderTable(data) {
        const tableHead = document.querySelector('#collectionTable thead');
        const tableBody = document.querySelector('#collectionTable tbody');
        
        if (data.length === 0) return;
        
        // Get columns from first record
        const columns = Object.keys(data[0]);
        
        // Create header
        let headerHtml = '<tr><th><input type="checkbox" id="selectAll"></th>';
        columns.forEach(col => {
            headerHtml += `<th>${col}</th>`;
        });
        headerHtml += '</tr>';
        tableHead.innerHTML = headerHtml;
        
        // Create body
        let bodyHtml = '';
        data.forEach((record, index) => {
            bodyHtml += `<tr><td><input type="checkbox" class="record-checkbox" data-index="${index}"></td>`;
            columns.forEach(col => {
                let value = record[col];
                if (typeof value === 'string' && value.length > 50) {
                    value = value.substring(0, 50) + '...';
                }
                bodyHtml += `<td>${value || ''}</td>`;
            });
            bodyHtml += '</tr>';
        });
        tableBody.innerHTML = bodyHtml;
        
        // Setup checkbox listeners
        document.getElementById('selectAll').addEventListener('change', (e) => {
            document.querySelectorAll('.record-checkbox').forEach(cb => {
                cb.checked = e.target.checked;
                if (e.target.checked) {
                    this.selectedRecords.add(parseInt(cb.dataset.index));
                } else {
                    this.selectedRecords.delete(parseInt(cb.dataset.index));
                }
            });
        });
        
        document.querySelectorAll('.record-checkbox').forEach(cb => {
            cb.addEventListener('change', (e) => {
                const index = parseInt(e.target.dataset.index);
                if (e.target.checked) {
                    this.selectedRecords.add(index);
                } else {
                    this.selectedRecords.delete(index);
                }
            });
        });
    }

    // CRUD Operations
    showAddRecordModal() {
        const modal = new bootstrap.Modal(document.getElementById('recordModal'));
        document.getElementById('recordModalTitle').textContent = 'Add Record';
        document.getElementById('recordFields').innerHTML = `
            <div class="mb-3">
                <label class="form-label">Field Name</label>
                <input type="text" class="form-control glass-input" id="fieldName" placeholder="Enter field name">
            </div>
            <div class="mb-3">
                <label class="form-label">Field Value</label>
                <input type="text" class="form-control glass-input" id="fieldValue" placeholder="Enter field value">
            </div>
            <button type="button" class="btn btn-secondary btn-sm" onclick="app.addMoreFields()">
                <i class="fas fa-plus me-1"></i>Add More Fields
            </button>
            <div id="additionalFields"></div>
        `;
        modal.show();
    }

    showEditRecordModal() {
        if (this.selectedRecords.size !== 1) {
            alert('Please select exactly one record to edit');
            return;
        }
        
        const index = Array.from(this.selectedRecords)[0];
        const record = this.currentData[index];
        
        const modal = new bootstrap.Modal(document.getElementById('recordModal'));
        document.getElementById('recordModalTitle').textContent = 'Edit Record';
        
        let fieldsHtml = '';
        Object.entries(record).forEach(([key, value]) => {
            const readonly = key === '_id' ? 'readonly' : '';
            fieldsHtml += `
                <div class="mb-3">
                    <label class="form-label">${key}</label>
                    <input type="text" class="form-control glass-input" name="${key}" value="${value}" ${readonly}>
                </div>
            `;
        });
        
        document.getElementById('recordFields').innerHTML = fieldsHtml;
        modal.show();
    }

    async saveRecord() {
        const collection = document.getElementById('collectionSelect').value;
        const form = document.getElementById('recordForm');
        const formData = new FormData(form);
        
        const record = {};
        for (let [key, value] of formData.entries()) {
            if (key && value) {
                record[key] = value;
            }
        }
        
        // If no form data, try to get from individual inputs (for add record)
        if (Object.keys(record).length === 0) {
            const fieldName = document.getElementById('fieldName')?.value;
            const fieldValue = document.getElementById('fieldValue')?.value;
            if (fieldName && fieldValue) {
                record[fieldName] = fieldValue;
            }
        }
        
        try {
            let response;
            if (document.getElementById('recordModalTitle').textContent === 'Add Record') {
                response = await fetch(`/api/collections/${collection}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ record })
                });
            } else {
                const index = Array.from(this.selectedRecords)[0];
                const recordId = this.currentData[index]._id;
                response = await fetch(`/api/collections/${collection}/${recordId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ record })
                });
            }
            
            const result = await response.json();
            if (result.success) {
                bootstrap.Modal.getInstance(document.getElementById('recordModal')).hide();
                this.loadCollectionData();
                this.showAlert(result.message, 'success');
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert(`Error: ${error.message}`, 'danger');
        }
    }

    async deleteSelectedRecords() {
        if (this.selectedRecords.size === 0) {
            alert('Please select records to delete');
            return;
        }
        
        if (!confirm(`Delete ${this.selectedRecords.size} selected record(s)?`)) {
            return;
        }
        
        const collection = document.getElementById('collectionSelect').value;
        
        try {
            for (let index of this.selectedRecords) {
                const recordId = this.currentData[index]._id;
                await fetch(`/api/collections/${collection}/${recordId}`, {
                    method: 'DELETE'
                });
            }
            
            this.selectedRecords.clear();
            this.loadCollectionData();
            this.showAlert('Records deleted successfully', 'success');
        } catch (error) {
            this.showAlert(`Error deleting records: ${error.message}`, 'danger');
        }
    }

    // Analytics Methods
    async loadHeatmap() {
        const refreshBtn = document.getElementById('refreshHeatmapBtn');
        const statusDiv = document.getElementById('heatmapStatus');
        const ctx = document.getElementById('heatmapChart');
        
        if (!ctx) return; // Canvas not available
        
        refreshBtn.disabled = true;
        statusDiv.textContent = 'Loading heatmap...';

        try {
            const response = await fetch('/api/visualization/heatmap');
            const data = await response.json();
            
            if (data.success) {
                this.renderHeatmap(ctx, data);
                statusDiv.textContent = `Loaded heatmap for ${data.total_records} recommendations.`;
            } else {
                statusDiv.textContent = data.error;
            }
        } catch (error) {
            statusDiv.textContent = `Error loading heatmap: ${error.message}`;
        } finally {
            refreshBtn.disabled = false;
        }
    }

    renderHeatmap(ctx, data) {
        // Destroy existing chart
        if (this.heatmapChart) {
            this.heatmapChart.destroy();
        }
        
        // Prepare data for Chart.js
        const datasets = [];
        const colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)'
        ];
        
        data.categories.forEach((category, i) => {
            const rowData = data.data[i];
            const dataPoints = rowData.map((value, j) => ({
                x: j,
                y: i,
                v: value
            }));
            
            datasets.push({
                label: category,
                data: dataPoints,
                backgroundColor: colors[i % colors.length],
                borderColor: colors[i % colors.length].replace('0.8', '1'),
                borderWidth: 1
            });
        });
        
        this.heatmapChart = new Chart(ctx, {
            type: 'scatter',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Outfit Category Popularity by Weather Condition'
                    },
                    legend: {
                        display: true,
                        position: 'right'
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Weather Conditions'
                        },
                        ticks: {
                            callback: function(value) {
                                return data.weathers[Math.round(value)] || '';
                            }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Clothing Categories'
                        },
                        ticks: {
                            callback: function(value) {
                                return data.categories[Math.round(value)] || '';
                            }
                        }
                    }
                }
            }
        });
    }

    // Utility Methods
    showAlert(message, type) {
        // Create a temporary alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    addMoreFields() {
        const container = document.getElementById('additionalFields');
        const fieldCount = container.children.length;
        
        const fieldHtml = `
            <div class="row g-2 mb-2">
                <div class="col-6">
                    <input type="text" class="form-control glass-input" placeholder="Field name" id="fieldName${fieldCount}">
                </div>
                <div class="col-6">
                    <input type="text" class="form-control glass-input" placeholder="Field value" id="fieldValue${fieldCount}">
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', fieldHtml);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WeatherOutfitApp();
});