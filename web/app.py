from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import requests
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'weather-app-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

NOMINATIM_SERVICE_URL = 'http://nominatim-service:5000'
METEO_SERVICE_URL = 'http://meteo-service:5000'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather', methods=['POST'])
def get_weather():
    data = request.json
    city = data.get('city', '')
    
    if not city:
        return jsonify({'error': 'City is required'}), 400
    
    # Step 1: Validate and format location name using Nominatim service
    try:
        nominatim_response = requests.post(
            f"{NOMINATIM_SERVICE_URL}/validate",
            json={'query': city}
        )
        nominatim_response.raise_for_status()
        location_data = nominatim_response.json()
        
        if 'error' in location_data:
            return jsonify({'error': location_data['error']}), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Nominatim service error: {str(e)}'}), 500
    
    # Step 2: Get weather data from Meteo service
    try:
        meteo_response = requests.post(
            f"{METEO_SERVICE_URL}/weather",
            json=location_data
        )
        meteo_response.raise_for_status()
        weather_data = meteo_response.json()
        
        # Emit weather data to connected clients through WebSocket
        socketio.emit('weather_update', weather_data)
        
        return jsonify(weather_data)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Meteo service error: {str(e)}'}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)