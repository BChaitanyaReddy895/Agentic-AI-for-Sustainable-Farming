import os
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedWeatherAnalyst:
    """
    Enhanced weather analyst that uses real weather APIs and Llama 2 for intelligent forecasting
    """
    
    def __init__(self, openweather_api_key: Optional[str] = None):
        self.openweather_api_key = openweather_api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Initialize Llama 2 model for weather analysis
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "meta-llama/Llama-2-7b-chat-hf"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            logger.info(f"Loaded Llama 2 model on {self.device}")
        except Exception as e:
            logger.warning(f"Could not load Llama 2 model: {e}. Using fallback analysis.")
            self.model = None
            self.tokenizer = None
    
    def get_current_weather(self, lat: float = 12.9716, lon: float = 77.5946) -> Dict:
        """
        Get current weather data from OpenWeatherMap API
        Default coordinates are for Bangalore, India
        """
        if not self.openweather_api_key:
            logger.warning("No OpenWeatherMap API key provided. Using simulated data.")
            return self._get_simulated_weather()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'description': data['weather'][0]['description'],
                'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
                'clouds': data['clouds']['all'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return self._get_simulated_weather()
    
    def get_weather_forecast(self, lat: float = 12.9716, lon: float = 77.5946, days: int = 5) -> List[Dict]:
        """
        Get 5-day weather forecast from OpenWeatherMap API
        """
        if not self.openweather_api_key:
            logger.warning("No OpenWeatherMap API key provided. Using simulated data.")
            return self._get_simulated_forecast(days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            forecasts = []
            
            for item in data['list'][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecasts.append({
                    'datetime': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item['wind']['speed'],
                    'wind_direction': item['wind'].get('deg', 0),
                    'description': item['weather'][0]['description'],
                    'rain_probability': item.get('pop', 0) * 100,  # Probability of precipitation
                    'rain_volume': item.get('rain', {}).get('3h', 0),  # Rain volume for 3h
                    'clouds': item['clouds']['all']
                })
            
            return forecasts
            
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return self._get_simulated_forecast(days)
    
    def analyze_weather_with_llama(self, weather_data: Dict, crop_type: str = "wheat") -> str:
        """
        Use Llama 2 to analyze weather data and provide agricultural insights
        """
        if not self.model or not self.tokenizer:
            return self._get_fallback_analysis(weather_data, crop_type)
        
        try:
            # Prepare context for Llama 2
            context = f"""
            As an agricultural weather expert, analyze the following weather data for {crop_type} farming:
            
            Current Weather:
            - Temperature: {weather_data.get('temperature', 'N/A')}°C
            - Humidity: {weather_data.get('humidity', 'N/A')}%
            - Pressure: {weather_data.get('pressure', 'N/A')} hPa
            - Wind Speed: {weather_data.get('wind_speed', 'N/A')} m/s
            - Description: {weather_data.get('description', 'N/A')}
            - Visibility: {weather_data.get('visibility', 'N/A')} km
            - Cloud Cover: {weather_data.get('clouds', 'N/A')}%
            
            Provide specific agricultural recommendations for {crop_type} farming based on these conditions.
            Focus on:
            1. Crop growth implications
            2. Irrigation needs
            3. Pest and disease risks
            4. Harvest timing considerations
            5. Any weather warnings or alerts
            
            Keep the response concise and actionable for farmers.
            """
            
            # Tokenize and generate response
            inputs = self.tokenizer.encode(context, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 200,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the generated part (remove the input context)
            generated_text = response[len(context):].strip()
            
            return generated_text if generated_text else self._get_fallback_analysis(weather_data, crop_type)
            
        except Exception as e:
            logger.error(f"Error in Llama 2 analysis: {e}")
            return self._get_fallback_analysis(weather_data, crop_type)
    
    def forecast_agricultural_conditions(self, lat: float = 12.9716, lon: float = 77.5946, 
                                       crop_type: str = "wheat") -> Dict:
        """
        Main method to get comprehensive weather forecast with agricultural insights
        """
        try:
            # Get current weather
            current_weather = self.get_current_weather(lat, lon)
            
            # Get forecast
            forecast_data = self.get_weather_forecast(lat, lon, 5)
            
            # Analyze with Llama 2
            analysis = self.analyze_weather_with_llama(current_weather, crop_type)
            
            # Calculate agricultural metrics
            avg_temp = sum([day['temperature'] for day in forecast_data[:8]]) / min(8, len(forecast_data))
            total_rainfall = sum([day['rain_volume'] for day in forecast_data[:8]])
            avg_humidity = sum([day['humidity'] for day in forecast_data[:8]]) / min(8, len(forecast_data))
            
            # Determine agricultural conditions
            conditions = self._assess_agricultural_conditions(avg_temp, total_rainfall, avg_humidity, crop_type)
            
            return {
                'current_weather': current_weather,
                'forecast': forecast_data,
                'analysis': analysis,
                'agricultural_conditions': conditions,
                'metrics': {
                    'avg_temperature': round(avg_temp, 1),
                    'total_rainfall': round(total_rainfall, 1),
                    'avg_humidity': round(avg_humidity, 1)
                },
                'recommendations': self._generate_recommendations(conditions, crop_type)
            }
            
        except Exception as e:
            logger.error(f"Error in agricultural weather forecast: {e}")
            return self._get_fallback_forecast(crop_type)
    
    def _assess_agricultural_conditions(self, temp: float, rainfall: float, humidity: float, crop_type: str) -> Dict:
        """Assess agricultural conditions based on weather metrics"""
        conditions = {
            'temperature_status': 'optimal',
            'rainfall_status': 'adequate',
            'humidity_status': 'normal',
            'overall_risk': 'low'
        }
        
        # Temperature assessment
        if temp < 10 or temp > 35:
            conditions['temperature_status'] = 'extreme'
            conditions['overall_risk'] = 'high'
        elif temp < 15 or temp > 30:
            conditions['temperature_status'] = 'suboptimal'
            if conditions['overall_risk'] == 'low':
                conditions['overall_risk'] = 'medium'
        
        # Rainfall assessment
        if rainfall < 10:
            conditions['rainfall_status'] = 'insufficient'
            if conditions['overall_risk'] == 'low':
                conditions['overall_risk'] = 'medium'
        elif rainfall > 50:
            conditions['rainfall_status'] = 'excessive'
            if conditions['overall_risk'] == 'low':
                conditions['overall_risk'] = 'medium'
        
        # Humidity assessment
        if humidity < 30:
            conditions['humidity_status'] = 'low'
        elif humidity > 80:
            conditions['humidity_status'] = 'high'
            if conditions['overall_risk'] == 'low':
                conditions['overall_risk'] = 'medium'
        
        return conditions
    
    def _generate_recommendations(self, conditions: Dict, crop_type: str) -> List[str]:
        """Generate specific recommendations based on conditions"""
        recommendations = []
        
        if conditions['temperature_status'] == 'extreme':
            if conditions['temperature_status'] == 'extreme':
                recommendations.append("⚠️ Extreme temperature detected. Consider protective measures like shade nets or heating systems.")
        
        if conditions['rainfall_status'] == 'insufficient':
            recommendations.append("💧 Insufficient rainfall. Irrigation may be necessary.")
        elif conditions['rainfall_status'] == 'excessive':
            recommendations.append("🌧️ Excessive rainfall expected. Ensure proper drainage to prevent waterlogging.")
        
        if conditions['humidity_status'] == 'high':
            recommendations.append("🌫️ High humidity conditions. Monitor for fungal diseases and ensure good air circulation.")
        elif conditions['humidity_status'] == 'low':
            recommendations.append("🏜️ Low humidity conditions. Consider misting or increased irrigation frequency.")
        
        if conditions['overall_risk'] == 'high':
            recommendations.append("🚨 High risk conditions detected. Consult with agricultural experts before proceeding.")
        
        return recommendations
    
    def _get_simulated_weather(self) -> Dict:
        """Fallback simulated weather data"""
        return {
            'temperature': 25.0,
            'humidity': 65.0,
            'pressure': 1013.25,
            'wind_speed': 3.5,
            'wind_direction': 180,
            'description': 'partly cloudy',
            'visibility': 10.0,
            'clouds': 40,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_simulated_forecast(self, days: int) -> List[Dict]:
        """Fallback simulated forecast data"""
        forecasts = []
        base_temp = 25.0
        
        for i in range(days * 8):
            temp = base_temp + (i % 3 - 1) * 2  # Slight variation
            forecasts.append({
                'datetime': (datetime.now() + timedelta(hours=i*3)).strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': temp,
                'humidity': 60 + (i % 5) * 2,
                'pressure': 1013 + (i % 3 - 1) * 2,
                'wind_speed': 2 + (i % 4),
                'wind_direction': (i * 45) % 360,
                'description': 'partly cloudy',
                'rain_probability': 20 + (i % 3) * 10,
                'rain_volume': (i % 7) * 0.5,
                'clouds': 30 + (i % 4) * 10
            })
        
        return forecasts
    
    def _get_fallback_analysis(self, weather_data: Dict, crop_type: str) -> str:
        """Fallback analysis when Llama 2 is not available"""
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 65)
        
        analysis = f"Weather analysis for {crop_type} farming:\n"
        analysis += f"Current temperature: {temp}°C - "
        
        if temp < 15:
            analysis += "Cool conditions may slow growth.\n"
        elif temp > 30:
            analysis += "Hot conditions may stress plants.\n"
        else:
            analysis += "Optimal temperature range.\n"
        
        analysis += f"Humidity: {humidity}% - "
        if humidity > 80:
            analysis += "High humidity increases disease risk.\n"
        elif humidity < 30:
            analysis += "Low humidity may require more irrigation.\n"
        else:
            analysis += "Normal humidity levels.\n"
        
        return analysis
    
    def _get_fallback_forecast(self, crop_type: str) -> Dict:
        """Fallback forecast when API fails"""
        return {
            'current_weather': self._get_simulated_weather(),
            'forecast': self._get_simulated_forecast(5),
            'analysis': self._get_fallback_analysis(self._get_simulated_weather(), crop_type),
            'agricultural_conditions': {
                'temperature_status': 'optimal',
                'rainfall_status': 'adequate',
                'humidity_status': 'normal',
                'overall_risk': 'low'
            },
            'metrics': {
                'avg_temperature': 25.0,
                'total_rainfall': 15.0,
                'avg_humidity': 65.0
            },
            'recommendations': ["Monitor weather conditions regularly."]
        }
