from flask import Flask, request, jsonify
import requests
import json
import os
import time
from urllib.parse import quote

app = Flask(__name__)

# meteo.lt API URL
METEO_API_BASE_URL = "https://api.meteo.lt/v1"

# Cache duomenų
weather_cache = {}
CACHE_TIMEOUT = 600  # 10 minučių

def is_cache_valid(location_code):
    """Patikrinti ar turime galiojančius cache duomenis"""
    if location_code in weather_cache:
        if time.time() - weather_cache[location_code]["timestamp"] < CACHE_TIMEOUT:
            return True
    return False

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.json
    
    if not data or 'place_name' not in data:
        return jsonify({'error': 'Reikalingas vietovės pavadinimas'}), 400
    
    place_name = data['place_name']
    
    # Jei turime galiojančius duomenis cache, gražiname juos
    cache_key = place_name.lower()
    if is_cache_valid(cache_key):
        return jsonify(weather_cache[cache_key]["data"])
    
    try:
        # Formatuojame užklausą meteo.lt API
        formatted_place = quote(place_name)
        url = f"{METEO_API_BASE_URL}/places/{formatted_place}/forecasts/long-term"
        
        # Atliekame užklausą į meteo.lt API
        response = requests.get(url)
        
        # Tikriname ar gautas atsakymas
        if response.status_code == 404:
            return jsonify({'error': f'Vietovė "{place_name}" nerasta'}), 404
        elif response.status_code != 200:
            return jsonify({'error': f'Meteo.lt API klaida: {response.status_code}'}), response.status_code
        
        # Apdorojame gautus duomenis
        weather_data = response.json()
        
        # Papildomai pridedame lokacijos duomenis
        if data.get('coordinates'):
            weather_data['location'] = {
                'name': place_name,
                'coordinates': data['coordinates']
            }
        else:
            weather_data['location'] = {
                'name': place_name,
                'coordinates': {
                    'latitude': weather_data.get('place', {}).get('coordinates', {}).get('latitude', 0),
                    'longitude': weather_data.get('place', {}).get('coordinates', {}).get('longitude', 0)
                }
            }
        
        # Įdedame duomenis į cache
        weather_cache[cache_key] = {
            "data": weather_data,
            "timestamp": time.time()
        }
        
        return jsonify(weather_data)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Klaida kreipiantis į meteo.lt API: {str(e)}'}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Klaida apdorojant meteo.lt API atsakymą'}), 500
    except Exception as e:
        return jsonify({'error': f'Nenumatyta klaida: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)