from flask import Flask, request, jsonify
import requests
import json
import os
import time
from urllib.parse import quote

app = Flask(__name__)

# Nominatim API URL
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"

# Cache duomenų
location_cache = {}
CACHE_TIMEOUT = 3600  # 1 valanda

def is_cache_valid(query):
    """Patikrinti ar turime galiojančius cache duomenis"""
    if query in location_cache:
        if time.time() - location_cache[query]["timestamp"] < CACHE_TIMEOUT:
            return True
    return False

@app.route('/validate', methods=['POST'])
def validate_location():
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Reikalinga užklausa'}), 400
    
    query = data['query'].strip()
    
    # Pridedame Lietuvos kontekstą, jei nėra nurodyta
    if "lietuva" not in query.lower() and "lithuania" not in query.lower():
        search_query = f"{query}, Lithuania"
    else:
        search_query = query
    
    # Jei turime galiojančius duomenis cache, gražiname juos
    cache_key = search_query.lower()
    if is_cache_valid(cache_key):
        return jsonify(location_cache[cache_key]["data"])
    
    try:
        # Formatuojame ir paruošiame URL
        params = {
            'q': search_query,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1,
            'accept-language': 'lt'
        }
        
        # Pridedame User-Agent antraštę, nes to reikalauja Nominatim API
        headers = {
            'User-Agent': 'WeatherMapApp/1.0'
        }
        
        # Siunčiame užklausą į Nominatim API
        response = requests.get(NOMINATIM_API_URL, params=params, headers=headers)
        response.raise_for_status()
        
        # Tikriname ar gautas atsakymas
        data = response.json()
        
        if not data:
            return jsonify({'error': f'Vietovė "{query}" nerasta'}), 404
        
        # Apdorojame gautus duomenis
        location = data[0]
        
        # Paruošiame vietovės pavadinimą, kuris bus naudojamas meteo.lt API
        place_name = location.get('name')
        if not place_name:
            # Jei neturime tiesioginio vietovės pavadinimo, bandome išgauti iš adreso detalių
            address = location.get('address', {})
            if 'city' in address:
                place_name = address['city']
            elif 'town' in address:
                place_name = address['town']
            elif 'village' in address:
                place_name = address['village']
            else:
                place_name = address.get('county', query)
        
        # Suformuojame rezultatą
        result = {
            'place_name': place_name,
            'coordinates': {
                'latitude': float(location['lat']),
                'longitude': float(location['lon'])
            },
            'display_name': location['display_name'],
            'type': location['type']
        }
        
        # Įdedame duomenis į cache
        location_cache[cache_key] = {
            "data": result,
            "timestamp": time.time()
        }
        
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Klaida kreipiantis į Nominatim API: {str(e)}'}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Klaida apdorojant Nominatim API atsakymą'}), 500
    except Exception as e:
        return jsonify({'error': f'Nenumatyta klaida: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)