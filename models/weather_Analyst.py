import sqlite3
import pandas as pd
import joblib
import os
import numpy as np
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherAnalyst:

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'sustainable_farming.db'))
        self.db_path = db_path
        self.models_dir = os.path.dirname(__file__)
        self.model = None
        self.scaler = None
        
        # Load NEW retrained models (from 1/13/2026)
        model_path = os.path.join(self.models_dir, 'weather_analyst_model.pkl')
        scaler_path = os.path.join(self.models_dir, 'weather_analyst_scaler.pkl')
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            print("🌤️ Loading NEW retrained Weather Analyst model...")
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            print(f"✅ Loaded retrained model from {os.path.getmtime(model_path)}")
        else:
            print("⚠️ New models not found, falling back to training...")
            self._initialize_fallback()

        self.df = None

    def analyze_weather_impact(self, temperature=25, rainfall=500, humidity=60, location="Unknown"):
        """Analyze weather impact using NEW retrained model"""
        try:
            if self.model is None or self.scaler is None:
                return self._fallback_analysis(temperature, rainfall, humidity)
            
            # Prepare input data (3 features as used in retraining: temperature, rainfall, year)
            input_data = np.array([[temperature, rainfall, 2024]])
            
            # Scale the input
            input_scaled = self.scaler.transform(input_data)
            
            # Make prediction (predicts yield)
            yield_prediction = self.model.predict(input_scaled)[0]
            
            # Calculate weather score (0-10) based on predicted yield
            weather_score = min(10, max(0, yield_prediction / 2))  # Scale to 0-10
            
            # Determine risk level and forecast
            if yield_prediction > 8:
                risk_level = "Low"
                forecast = "Excellent conditions for farming"
            elif yield_prediction > 5:
                risk_level = "Moderate"
                forecast = "Good conditions with minor concerns"
            else:
                risk_level = "High"
                forecast = "Challenging conditions, take precautions"
            
            return {
                'weather_score': round(weather_score, 1),
                'forecast': forecast,
                'risk_level': risk_level,
                'predicted_yield_impact': round(yield_prediction, 2),
                'model_version': 'retrained_2026-01-13'
            }
            
        except Exception as e:
            print(f"Error in weather analysis: {e}")
            return self._fallback_analysis(temperature, rainfall, humidity)
    
    def _fallback_analysis(self, temperature, rainfall, humidity):
        """Fallback analysis when model fails"""
        # Simple rule-based analysis
        score = 5.0
        if 20 <= temperature <= 30: score += 1.5
        if 500 <= rainfall <= 1200: score += 1.5
        if 50 <= humidity <= 80: score += 1.0
        
        score = min(10, max(0, score))
        
        if score >= 7:
            risk = "Low"
            forecast = "Favorable weather conditions"
        elif score >= 4:
            risk = "Moderate" 
            forecast = "Average weather conditions"
        else:
            risk = "High"
            forecast = "Challenging weather conditions"
        
        return {
            'weather_score': round(score, 1),
            'forecast': forecast,
            'risk_level': risk,
            'predicted_yield_impact': score,
            'model_version': 'fallback'
        }
    
    def _initialize_fallback(self):
        """Initialize fallback when retrained models not found"""
        print("⚠️ Using fallback weather analysis")

    def get_weather_forecast(self, location="Unknown"):
        """Get weather forecast for location"""
        return {
            'location': location,
            'current': {
                'temperature': 25,
                'description': 'Partly cloudy',
                'wind_speed': 10,
                'humidity': 65,
                'pressure': 1013
            },
            'forecast': [
                {'date': 'Today', 'temperature': 25, 'description': 'Partly cloudy'},
                {'date': 'Tomorrow', 'temperature': 27, 'description': 'Sunny'},
                {'date': 'Day 3', 'temperature': 23, 'description': 'Light rain'},
                {'date': 'Day 4', 'temperature': 26, 'description': 'Clear'},
                {'date': 'Day 5', 'temperature': 28, 'description': 'Sunny'}
            ],
            'farming_advice': 'Weather conditions are generally favorable for crop growth. Monitor for any sudden changes in rainfall patterns.'
        }