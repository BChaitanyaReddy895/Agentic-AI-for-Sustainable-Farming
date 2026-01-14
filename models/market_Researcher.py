import sqlite3
import pandas as pd
import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

class MarketResearcher:
    def __init__(self, db_path="Models/database/sustainable_farming.db"):
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'sustainable_farming.db'))
        self.models_dir = os.path.dirname(__file__)
        self.model = None
        self.scaler = None
        
        # Load NEW retrained models (from 1/13/2026)
        model_path = os.path.join(self.models_dir, 'market_researcher_model.pkl')
        scaler_path = os.path.join(self.models_dir, 'market_researcher_scaler.pkl')
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            print("💰 Loading NEW retrained Market Researcher model...")
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            print(f"✅ Loaded retrained model from {os.path.getmtime(model_path)}")
        else:
            print("⚠️ New models not found, falling back to training...")
            self._initialize_fallback()

    def forecast_market_trends(self, crop='wheat', area=100, production=500, year=2024):
        """Forecast market trends using NEW retrained model"""
        try:
            if self.model is None or self.scaler is None:
                return self._fallback_forecast(crop)
            
            # Prepare input data (5 features as used in retraining)
            input_data = np.array([[area, production, production/area, year, 150]])  # area, production, yield, year, fertilizer
            
            # Scale the input
            input_scaled = self.scaler.transform(input_data)
            
            # Make prediction
            price_prediction = self.model.predict(input_scaled)[0]
            
            # Calculate market score (0-10)
            market_score = min(10, max(0, (price_prediction / 1000) * 2))  # Scale to 0-10
            
            # Determine trend based on prediction
            if price_prediction > 2000:
                trend = "Rising"
                demand = "High"
            elif price_prediction > 1000:
                trend = "Stable"
                demand = "Moderate"
            else:
                trend = "Declining"
                demand = "Low"
            
            return {
                'market_score': round(market_score, 1),
                'price_trend': trend,
                'demand_forecast': demand,
                'predicted_price': round(price_prediction, 2),
                'model_version': 'retrained_2026-01-13'
            }
            
        except Exception as e:
            print(f"Error in market forecast: {e}")
            return self._fallback_forecast(crop)
    
    def _fallback_forecast(self, crop):
        """Fallback forecast when model fails"""
        return {
            'market_score': 6.5,
            'price_trend': 'Stable',
            'demand_forecast': 'Moderate',
            'predicted_price': 1500,
            'model_version': 'fallback'
        }
    
    def _initialize_fallback(self):
        """Initialize fallback when retrained models not found"""
        print("⚠️ Using fallback market analysis")

    def get_market_insights(self, location="India"):
        """Get general market insights"""
        return {
            'crop_prices': [
                {'crop': 'Wheat', 'price': 2500, 'change': 5.2},
                {'crop': 'Rice', 'price': 3200, 'change': -2.1},
                {'crop': 'Corn', 'price': 1800, 'change': 3.8},
                {'crop': 'Soybean', 'price': 4500, 'change': 7.5}
            ],
            'demand_trends': [
                {'crop': 'Wheat', 'level': 'High', 'forecast': 'Growing'},
                {'crop': 'Rice', 'level': 'Moderate', 'forecast': 'Stable'},
                {'crop': 'Corn', 'level': 'High', 'forecast': 'Growing'},
                {'crop': 'Soybean', 'level': 'Low', 'forecast': 'Declining'}
            ],
            'market_insights': [
                'Wheat prices expected to rise due to increased export demand',
                'Rice market stabilizing after monsoon season',
                'Corn demand growing in livestock sector',
                'Soybean prices volatile due to global trade tensions'
            ]
        }