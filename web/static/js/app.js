// Inicializuojame žemėlapį
const map = L.map('map-container').setView([55.1694, 23.8813], 7); // Lietuvos centras

// Pridedame OpenStreetMap sluoksnį
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Markerio kintamasis
let marker = null;

// Inicializuojame Socket.IO klientą
const socket = io();

// Klausomės naujų orų prognozės duomenų
socket.on('weather_update', (data) => {
    if (data.error) {
        showError(data.error);
        return;
    }
    
    updateWeatherData(data);
});

// DOM elementai
const cityInput = document.getElementById('city-input');
const searchBtn = document.getElementById('search-btn');
const errorMessage = document.getElementById('error-message');
const locationName = document.getElementById('location-name');
const weatherData = document.getElementById('weather-data');
const forecastContainer = document.getElementById('forecast-container');

// Užregistruojame įvykių klausytojus
searchBtn.addEventListener('click', searchCity);
cityInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        searchCity();
    }
});

// Funkcijos
function searchCity() {
    const city = cityInput.value.trim();
    
    if (!city) {
        showError('Įveskite miestą');
        return;
    }
    
    clearError();
    showLoading();
    
    // Kreipiamės į serverio API
    fetch('/api/weather', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ city: city })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
            hideLoading();
        } else {
            updateWeatherData(data);
            hideLoading();
        }
    })
    .catch(error => {
        showError('Serverio klaida, bandykite vėliau.');
        hideLoading();
        console.error('Error:', error);
    });
}

function updateWeatherData(data) {
    // Atnaujiname vietovės pavadinimą
    locationName.textContent = data.location.name;
    
    // Atnaujiname žemėlapį
    const lat = data.location.coordinates.latitude;
    const lon = data.location.coordinates.longitude;
    
    // Jei jau yra markeris, pašaliname jį
    if (marker) {
        map.removeLayer(marker);
    }
    
    // Sukuriame naują markerį
    marker = L.marker([lat, lon]).addTo(map);
    map.setView([lat, lon], 10);
    
    // Atnaujiname esamos dienos orų duomenis
    const currentWeather = data.forecastTimestamps[0];
    
    weatherData.innerHTML = `
        <div class="text-center">
            <h2>${currentWeather.airTemperature}°C</h2>
            <p>Kondensacija: ${currentWeather.conditionCode}</p>
            <p>Vėjo greitis: ${currentWeather.windSpeed} m/s</p>
            <p>Vėjo kryptis: ${getWindDirection(currentWeather.windDirection)}</p>
            <p>Debesuotumas: ${currentWeather.cloudCover}%</p>
        </div>
    `;
    
    // Atnaujiname prognozės duomenis
    updateForecast(data.forecastTimestamps);
}

function updateForecast(forecastData) {
    // Sugrupuojame prognozes pagal dienas
    const dailyForecasts = groupByDay(forecastData);
    
    // Atnaujiname prognozių konteinerį
    forecastContainer.innerHTML = '';
    
    // Pridedame kiekvienos dienos prognozes (ne daugiau kaip 3 dienas)
    Object.keys(dailyForecasts).slice(0, 3).forEach(date => {
        const dayData = dailyForecasts[date];
        const dayTemp = calculateDayAverageTemp(dayData);
        
        const dayForecastElement = document.createElement('div');
        dayForecastElement.className = 'card mb-2';
        dayForecastElement.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${formatDate(date)}</h5>
                <p class="card-text">Vid. temperatūra: ${dayTemp}°C</p>
            </div>
        `;
        
        forecastContainer.appendChild(dayForecastElement);
    });
}

function groupByDay(forecastData) {
    const days = {};
    
    forecastData.forEach(item => {
        const date = item.forecastTimeUtc.split(' ')[0]; // Išskiriame datą
        
        if (!days[date]) {
            days[date] = [];
        }
        
        days[date].push(item);
    });
    
    return days;
}

function calculateDayAverageTemp(dayData) {
    const sum = dayData.reduce((acc, item) => acc + item.airTemperature, 0);
    return (sum / dayData.length).toFixed(1);
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('lt-LT', { weekday: 'long', month: 'long', day: 'numeric' });
}

function getWindDirection(degrees) {
    const directions = ['Š', 'ŠR', 'R', 'PR', 'P', 'PV', 'V', 'ŠV'];
    const index = Math.round(degrees / 45) % 8;
    return directions[index];
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function clearError() {
    errorMessage.textContent = '';
    errorMessage.style.display = 'none';
}

function showLoading() {
    searchBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Ieškoma...';
    searchBtn.disabled = true;
}

function hideLoading() {
    searchBtn.innerHTML = 'Ieškoti';
    searchBtn.disabled = false;
}