import sqlite3
import pandas as pd
import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

class SustainabilityExpert:
    def __init__(self, db_path='Models/database/sustainable_farming.db'):
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'sustainable_farming.db'))
        self.models_dir = os.path.dirname(__file__)
        self.model = None
        self.scaler = None
        
        # Load NEW retrained models (from 1/13/2026)
        model_path = os.path.join(self.models_dir, 'sustainability_expert_model.pkl')
        scaler_path = os.path.join(self.models_dir, 'sustainability_expert_scaler.pkl')
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            print("🌱 Loading NEW retrained Sustainability Expert model...")
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            print(f"✅ Loaded retrained model from {os.path.getmtime(model_path)}")
        else:
            print("⚠️ New models not found, falling back to training...")
            self._initialize_fallback()

    def assess_sustainability(self, fertilizer_usage=100, organic_matter=3.0, ph=6.5, nitrogen=40, phosphorus=25):
        """Assess sustainability using NEW retrained model"""
        try:
            if self.model is None or self.scaler is None:
                return self._fallback_assessment(fertilizer_usage, organic_matter, ph)
            
            # Prepare input data (5 features as used in retraining)
            input_data = np.array([[fertilizer_usage, organic_matter, ph, nitrogen, phosphorus]])
            
            # Scale the input
            input_scaled = self.scaler.transform(input_data)
            
            # Make prediction (sustainability score 0-10)
            sustainability_score = self.model.predict(input_scaled)[0]
            
            # Ensure score is within bounds
            sustainability_score = min(10, max(0, sustainability_score))
            
            # Determine environmental impact and recommendations
            if sustainability_score >= 8:
                impact = "Very Low"
                recommendations = "Excellent sustainable practices. Continue current approach."
            elif sustainability_score >= 6:
                impact = "Low"
                recommendations = "Good practices. Consider reducing fertilizer usage slightly."
            elif sustainability_score >= 4:
                impact = "Moderate"
                recommendations = "Increase organic matter and reduce chemical inputs."
            else:
                impact = "High"
                recommendations = "Significant improvements needed. Focus on organic farming practices."
            
            return {
                'sustainability_score': round(sustainability_score, 1),
                'environmental_impact': impact,
                'recommendations': recommendations,
                'carbon_footprint': self._calculate_carbon_footprint(fertilizer_usage),
                'model_version': 'retrained_2026-01-13'
            }
            
        except Exception as e:
            print(f"Error in sustainability assessment: {e}")
            return self._fallback_assessment(fertilizer_usage, organic_matter, ph)
    
    def _calculate_carbon_footprint(self, fertilizer_usage):
        """Calculate approximate carbon footprint"""
        # Simple calculation: higher fertilizer = higher carbon footprint
        carbon_score = max(0, 10 - (fertilizer_usage / 20))
        if carbon_score >= 8:
            return "Very Low"
        elif carbon_score >= 6:
            return "Low"
        elif carbon_score >= 4:
            return "Moderate"
        else:
            return "High"
    
    def _fallback_assessment(self, fertilizer_usage, organic_matter, ph):
        """Fallback assessment when model fails"""
        # Simple rule-based assessment
        score = 5.0
        
        if fertilizer_usage < 80: score += 1.5
        elif fertilizer_usage > 150: score -= 1.5
        
        if organic_matter > 3.5: score += 1.0
        elif organic_matter < 2.0: score -= 1.0
        
        if 6.0 <= ph <= 7.5: score += 0.5
        
        score = min(10, max(0, score))
        
        if score >= 7:
            impact = "Low"
            rec = "Good sustainable practices"
        elif score >= 4:
            impact = "Moderate"
            rec = "Room for improvement in sustainability"
        else:
            impact = "High"
            rec = "Focus on sustainable farming practices"
        
        return {
            'sustainability_score': round(score, 1),
            'environmental_impact': impact,
            'recommendations': rec,
            'carbon_footprint': self._calculate_carbon_footprint(fertilizer_usage),
            'model_version': 'fallback'
        }
    
    def _initialize_fallback(self):
        """Initialize fallback when retrained models not found"""
        print("⚠️ Using fallback sustainability analysis")

    def get_best_practices(self):
        """Get sustainability best practices"""
        return {
            'practices': [
                'Use organic fertilizers and compost',
                'Implement crop rotation systems',
                'Practice water conservation techniques',
                'Reduce chemical pesticide usage',
                'Maintain soil health through cover crops',
                'Use precision agriculture techniques'
            ],
            'benefits': [
                'Reduced environmental impact',
                'Lower carbon footprint',
                'Improved soil health',
                'Better water conservation',
                'Enhanced biodiversity',
                'Long-term cost savings'
            ]
        }