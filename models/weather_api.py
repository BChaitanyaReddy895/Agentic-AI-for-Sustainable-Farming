import requests

API_KEY = "8acd7401e3d1478a87596f7e00e76226"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_current_weather(city_name):
    """
    Fetch current weather data for a given city using OpenWeatherMap API.
    Returns a dictionary with temperature (Celsius) and rainfall (mm, if available).
    """
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if response.status_code != 200:
        raise Exception(f"Weather API error: {data.get('message', 'Unknown error')}")
    temp = data['main']['temp']
    # Rainfall may not always be present
    rain = data.get('rain', {}).get('1h', 0.0)
    return {
        'temperature': temp,
        'rainfall': rain
    } 
import requests

API_KEY = "8acd7401e3d1478a87596f7e00e76226"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_current_weather(city_name):
    """
    Fetch current weather data for a given city using OpenWeatherMap API.
    Returns a dictionary with temperature (Celsius) and rainfall (mm, if available).
    """
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if response.status_code != 200:
        raise Exception(f"Weather API error: {data.get('message', 'Unknown error')}")
    temp = data['main']['temp']
    # Rainfall may not always be present
    rain = data.get('rain', {}).get('1h', 0.0)
    return {
        'temperature': temp,
        'rainfall': rain
    } 