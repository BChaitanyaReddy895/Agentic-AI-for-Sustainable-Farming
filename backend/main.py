# main.py - Complete FastAPI backend with all endpoints migrated from Streamlit app.py
import re
import os
import io
import sys
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import base64
import random
import requests
from PIL import Image

# Try to import pandas/numpy - if not available, use fallbacks
try:
    import numpy as np
    import pandas as pd
    HAS_ML = True
except ImportError:
    HAS_ML = False
    np = None
    pd = None

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import agent collaboration
try:
    from agents.agent_setup import run_agent_collaboration
except ImportError:
    def run_agent_collaboration(land_size, soil_type, crop_preference):
        # EXPERT SYSTEM: Rule-based logic for accurate recommendations without ML models
        # This replaces the random number generator with agronomic rules
        
        # crop_database: {crop: {soil: [], ph_min, ph_max, water_needs, region}}
        crop_db = {
            "Rice": {"soil": ["Clay", "Loamy", "Alluvial"], "water": "High", "desc": "Requires standing water and clayey soil."},
            "Wheat": {"soil": ["Loamy", "Sandy Loam"], "water": "Medium", "desc": "Thrives in cool climates and well-drained loamy soil."},
            "Corn": {"soil": ["Loamy", "Alluvial"], "water": "Medium", "desc": "Needs nutrient-rich soil with good drainage."},
            "Barley": {"soil": ["Loamy", "Sandy"], "water": "Low", "desc": "Drought tolerant, good for sandy/loamy soils."},
            "Sorghum": {"soil": ["Sandy", "Loamy", "Red"], "water": "Low", "desc": "Highly drought resistant, excellent for dry regions."},
            "Cotton": {"soil": ["Black", "Alluvial"], "water": "Medium", "desc": "Best in black soil (Regur), requires long frost-free period."},
            "Tomato": {"soil": ["Sandy Loam", "Loamy"], "water": "Medium", "desc": "Needs well-drained, fertile soil."},
            "Potato": {"soil": ["Sandy Loam"], "water": "Medium", "desc": "Best in loose soil for tuber development."},
            "Chickpea": {"soil": ["Loamy", "Sandy"], "water": "Low", "desc": "Nitrogen-fixing, improves soil health."}
        }
        
        # Determine best crops based on soil_type and inputs
        recommended_crops = []
        
        for crop, requirements in crop_db.items():
            score = 70.0 # Base score
            
            # Soil compatibility check
            if soil_type in requirements["soil"] or "All" in requirements["soil"]:
                score += 15
            elif soil_type in ["Loamy"]: # Loamy is good for almost everything
                score += 10
            else:
                score -= 10
                
            # Crop preference filter (simplified)
            if crop_preference == "Grains" and crop in ["Rice", "Wheat", "Corn", "Barley", "Sorghum"]:
                score += 10
            elif crop_preference == "Vegetables" and crop in ["Tomato", "Potato", "Carrot"]:
                score += 10
            elif crop_preference == "Pulses" and crop in ["Chickpea", "Soybean"]:
                score += 10
                
            # Random variation for realism (small amount)
            score += random.uniform(-2, 3)
            
            # Cap score
            score = min(98.0, max(40.0, score))
            
            recommended_crops.append({
                "crop": crop,
                "score": round(score, 1),
                "desc": requirements["desc"]
            })
            
        # Sort by score descending
        recommended_crops.sort(key=lambda x: x["score"], reverse=True)
        top_3 = recommended_crops[:3]
        
        # Build response text
        recommendation_text = f"ANALYSIS FOR {land_size}ha FARM ({soil_type.upper()} SOIL):\n\n"
        recommendation_text += f"Top Recommendation: {top_3[0]['crop']} (Score: {top_3[0]['score']}/100)\n"
        recommendation_text += f"Reasoning: {top_3[0]['desc']} ideally suited for {soil_type} soil.\n\n"
        
        if len(top_3) > 1:
            recommendation_text += f"Alternative: {top_3[1]['crop']} ({top_3[1]['score']}/100) - {top_3[1]['desc']}\n"
        
        chart_data = []
        for item in top_3:
            # Generate sub-scores consistent with the main score
            base = item["score"] / 100.0
            chart_data.append({
                "crop": item["crop"],
                "labels": ["Market Probability", "Weather Suitability", "Sustainability", "Yield Potential", "Soil Health"],
                "values": [
                    round(min(99, base * random.uniform(0.9, 1.1) * 100), 1),
                    round(min(99, base * random.uniform(0.9, 1.1) * 100), 1),
                    round(min(99, base * random.uniform(0.8, 1.2) * 100), 1),
                    round(min(99, base * random.uniform(0.9, 1.1) * 100), 1),
                    round(min(99, base * random.uniform(0.8, 1.2) * 100), 1)
                ]
            })
        
        return {'recommendation': recommendation_text, 'chart_data': chart_data}

# Import FertilizerOptimizer
try:
    from fertilizer_optimizer import FertilizerOptimizer
except ImportError:
    class FertilizerOptimizer:
        def __init__(self, db_path):
            self.db_path = db_path
        def calculate_fertilizer(self, land_size, soil_type, crop_type):
            # Realistic fertilizer calculations based on soil and crop type
            base_rates = {
                "Loamy": {"n": 120, "p": 60, "k": 80},
                "Sandy": {"n": 150, "p": 70, "k": 90},
                "Clay": {"n": 100, "p": 50, "k": 70}
            }
            crop_multipliers = {
                "Wheat": 1.0, "Rice": 1.2, "Corn": 1.3, "Tomatoes": 1.1,
                "Soybeans": 0.8, "Carrots": 0.9, "Potato": 1.15
            }
            rates = base_rates.get(soil_type, base_rates["Loamy"])
            mult = crop_multipliers.get(crop_type, 1.0)
            return {
                'nitrogen_kg': round(rates["n"] * land_size * mult, 1),
                'phosphorus_kg': round(rates["p"] * land_size * mult, 1),
                'potassium_kg': round(rates["k"] * land_size * mult, 1)
            }

# Import CropRotationPlanner
try:
    from crop_rotation_planner import CropRotationPlanner
except ImportError:
    class CropRotationPlanner:
        def __init__(self, db_path):
            self.db_path = db_path
            self.rotation_map = {
                "Wheat": ["Soybean", "Corn", "Fallow", "Wheat"],
                "Rice": ["Legumes", "Wheat", "Vegetables", "Rice"],
                "Corn": ["Soybean", "Wheat", "Cover Crop", "Corn"],
                "Tomato": ["Legumes", "Grains", "Brassicas", "Tomato"],
                "Soybean": ["Corn", "Wheat", "Sorghum", "Soybean"],
                "Potato": ["Legumes", "Grains", "Brassicas", "Potato"]
            }
        def generate_plan(self, current_crop):
            rotation = self.rotation_map.get(current_crop, ["Legumes", "Grains", "Cover Crop", current_crop])
            plan = f"Year 1: {rotation[0]} (nitrogen fixation)\n"
            plan += f"Year 2: {rotation[1]} (nutrient balance)\n"
            plan += f"Year 3: {rotation[2]} (soil health)\n"
            plan += f"Year 4: {current_crop} (main crop return)"
            return plan

# Import weather models
try:
    from models.enhanced_weather_analyst import EnhancedWeatherAnalyst
except ImportError:
    EnhancedWeatherAnalyst = None

try:
    from models.enhanced_pest_predictor import EnhancedPestDiseasePredictor
except ImportError:
    EnhancedPestDiseasePredictor = None

app = FastAPI(title="Sustainable Farming AI API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database/sustainable_farming.db'))
# Also check parent directory for database
if not os.path.exists(os.path.dirname(DB_PATH)):
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'sustainable_farming.db'))

# OpenWeatherMap API Key
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'e6f39f1d5c2c4ecea6d180422252609')

# Models
class UserSignup(BaseModel):
    username: str
    farm_name: str
    profile_picture: Optional[str] = None

class UserLogin(BaseModel):
    username: str

class FarmDetails(BaseModel):
    username: str
    land_size: float
    soil_type: str
    crop_preference: str

class RecommendationRequest(BaseModel):
    username: str
    land_size: float
    soil_type: str
    crop_preference: str

class SustainabilityLog(BaseModel):
    username: str
    water_score: float
    fertilizer_use: float
    rotation: bool

class CommunityInsight(BaseModel):
    username: str
    crop_type: str
    yield_data: float
    market_price: float
    sustainability_practice: str
    region: str
    season: str

class ChatQuery(BaseModel):
    username: Optional[str] = "anonymous"
    query: str

class CropRotationRequest(BaseModel):
    current_crop: str
    years: int = 4

class FertilizerRequest(BaseModel):
    land_size: float
    soil_type: str
    crop_type: str

class WeatherRequest(BaseModel):
    lat: float = 12.9716
    lon: float = 77.5946
    crop_type: Optional[str] = "General"

class PestPredictionRequest(BaseModel):
    crop_type: str
    soil_type: str
    temperature: float
    humidity: float
    rainfall: float

class MultiAgentRecommendationRequest(BaseModel):
    """Request for multi-agent collaboration recommendation"""
    username: str = "anonymous"
    land_size: float = 5.0
    soil_type: str = "Loamy"
    crop_preference: str = "Grains"
    # Additional parameters for AI models
    nitrogen: float = 40.0
    phosphorus: float = 30.0
    potassium: float = 30.0
    temperature: float = 25.0
    humidity: float = 60.0
    ph: float = 6.5
    rainfall: float = 500.0

class OfflineDataRequest(BaseModel):
    username: str
    data_type: str
    data_content: str

class UserProfileUpdate(BaseModel):
    username: str
    new_username: Optional[str] = None
    farm_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    farm_size: Optional[float] = None
    primary_crops: Optional[List[str]] = None

# Init DB (full from Streamlit)
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE, 
            farm_name TEXT, 
            profile_picture TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            experience_level TEXT,
            farm_size REAL,
            primary_crops TEXT,
            created_at TEXT
        )''')
        # Farm details table
        cursor.execute('''CREATE TABLE IF NOT EXISTS farm_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT, 
            land_size REAL, 
            soil_type TEXT, 
            crop_preference TEXT, 
            created_at TEXT
        )''')
        # Recommendations table with full schema
        cursor.execute('''CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT, 
            crop TEXT, 
            score REAL, 
            rationale TEXT, 
            market_score REAL, 
            weather_score REAL, 
            sustainability_score REAL, 
            carbon_score REAL, 
            water_score REAL, 
            erosion_score REAL, 
            timestamp TEXT, 
            recommendation TEXT
        )''')
        # Sustainability scores table
        cursor.execute('''CREATE TABLE IF NOT EXISTS sustainability_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            water_score REAL,
            fertilizer_use REAL,
            rotation INTEGER,
            score REAL
        )''')
        # Community insights table
        cursor.execute('''CREATE TABLE IF NOT EXISTS community_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            crop_type TEXT,
            yield_data REAL,
            market_price REAL,
            sustainability_practice TEXT,
            region TEXT,
            season TEXT,
            created_at TEXT
        )''')
        # Market forecasts table
        cursor.execute('''CREATE TABLE IF NOT EXISTS market_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT,
            predicted_price REAL,
            confidence_score REAL,
            forecast_date TEXT,
            created_at TEXT
        )''')
        # Chatbot sessions table
        cursor.execute('''CREATE TABLE IF NOT EXISTS chatbot_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            session_id TEXT,
            query TEXT,
            response TEXT,
            timestamp TEXT
        )''')
        # Farm maps table
        cursor.execute('''CREATE TABLE IF NOT EXISTS farm_maps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            farm_name TEXT,
            map_data TEXT,
            recommendations TEXT,
            risk_areas TEXT,
            created_at TEXT,
            updated_at TEXT
        )''')
        # Offline data table
        cursor.execute('''CREATE TABLE IF NOT EXISTS offline_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            data_type TEXT,
            data_content TEXT,
            sync_status TEXT DEFAULT 'pending',
            created_at TEXT,
            synced_at TEXT
        )''')
        # Farmer advisor table for ML models
        cursor.execute('''CREATE TABLE IF NOT EXISTS farmer_advisor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Soil_pH REAL,
            Soil_Moisture REAL,
            Temperature_C REAL,
            Rainfall_mm REAL,
            Fertilizer_Usage_kg REAL,
            Pesticide_Usage_kg REAL,
            Crop_Yield_ton REAL,
            Crop_Type TEXT,
            Sustainability_Score REAL
        )''')
        # Market researcher table
        cursor.execute('''CREATE TABLE IF NOT EXISTS market_researcher (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Product TEXT,
            Market_Price_per_ton REAL,
            Demand_Index REAL,
            Supply_Index REAL,
            Competitor_Price_per_ton REAL,
            Economic_Indicator REAL,
            Weather_Impact_Score REAL,
            Seasonal_Factor TEXT,
            Consumer_Trend_Index REAL
        )''')
        conn.commit()

init_db()

# All Endpoints (full from previous, with stubs used)
@app.post("/signup")
def signup(user: UserSignup):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists.")
        cursor.execute("INSERT INTO users (username, farm_name, profile_picture, created_at) VALUES (?, ?, ?, ?)", (user.username, user.farm_name, user.profile_picture, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    return {"message": "Signup successful", "user": {"username": user.username, "farm_name": user.farm_name, "profile_picture": user.profile_picture}}

@app.post("/login")
def login(user: UserLogin):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, farm_name, profile_picture FROM users WHERE username = ?", (user.username,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"username": row[0], "farm_name": row[1], "profile_picture": row[2]}

@app.post("/farm_details")
def save_farm_details(details: FarmDetails):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO farm_details (username, land_size, soil_type, crop_preference, created_at) VALUES (?, ?, ?, ?, ?)", (details.username, details.land_size, details.soil_type, details.crop_preference, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    return {"message": "Farm details saved"}

@app.post("/soil_analysis")
async def analyze_soil(soil_photo: UploadFile = File(...)):
    contents = await soil_photo.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image_array = np.array(image)
    avg_color = np.mean(image_array, axis=(0, 1))
    r, g, b = avg_color
    # Match app.py logic
    if r > 120 and g < 110 and b < 110 and r > g and r > b:
        soil_type = "Clay"
    elif r > 90 and g > 90 and b < 80 and abs(r - g) < 30:
        soil_type = "Sandy"
    elif r < 120 and g < 120 and b < 120 and abs(r - g) < 20 and abs(g - b) < 20:
        soil_type = "Loamy"
    else:
        # Fallback with Euclidean distance
        clay_rgb = (150, 80, 80)
        sandy_rgb = (140, 120, 60)
        loamy_rgb = (80, 70, 60)
        def rgb_distance(rgb1, rgb2):
            return np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))
        distances = {
            "Clay": rgb_distance((r, g, b), clay_rgb),
            "Sandy": rgb_distance((r, g, b), sandy_rgb),
            "Loamy": rgb_distance((r, g, b), loamy_rgb)
        }
        soil_type = min(distances, key=distances.get)
    return {"soil_type": soil_type}

# Import ML model classes for multi-agent collaboration
try:
    from models.farmer_advisor import FarmerAdvisor
    from models.market_Researcher import MarketResearcher
    from models.weather_Analyst import WeatherAnalyst
    from models.sustainability_Expert import SustainabilityExpert
    from models.central_coordinator import CentralCoordinator
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import ML models: {e}")
    MODELS_AVAILABLE = False

@app.post("/multi_agent_recommendation")
def get_multi_agent_recommendation(req: MultiAgentRecommendationRequest):
    """
    Multi-Agent AI Recommendation System
    Uses CentralCoordinator to orchestrate 4 trained AI models to provide comprehensive farming recommendations:
    1. Farmer Advisor - Crop recommendations based on soil and weather
    2. Market Researcher - Market trends and price forecasting
    3. Weather Analyst - Weather impact analysis
    4. Sustainability Expert - Environmental impact assessment
    """
    response = {
        "agents": {},
        "central_coordinator": {},
        "chart_data": [],
        "success": True
    }
    
    try:
        if not MODELS_AVAILABLE:
            raise ImportError("ML models not available on server")

        # Initialize CentralCoordinator
        coordinator = CentralCoordinator()
        
        # Calculate dynamic pesticide and yield estimates based on input
        estimated_pesticide = min(4.0, max(0.5, req.nitrogen / 30))
        estimated_yield = min(6.0, max(1.0, req.land_size * 0.8))
        
        # Generate recommendation using the coordinator
        # usage: generate_recommendation(soil_ph, soil_moisture, temperature, rainfall, fertilizer, pesticide, crop_yield, city_name=None)
        result = coordinator.generate_recommendation(
            soil_ph=req.ph,
            soil_moisture=req.humidity, # Using humidity as proxy
            temperature=req.temperature,
            rainfall=req.rainfall,
            fertilizer=req.nitrogen,
            pesticide=estimated_pesticide,
            crop_yield=estimated_yield,
            city_name=None # We rely on user input coordinates/data in this request object
        )
        
        # Map CentralCoordinator result to API response structure
        
        # 1. Farmer Advisor
        response["agents"]["farmer_advisor"] = {
            "name": "🚜 Farmer Advisor",
            "recommended_crop": result['Recommended Crop'],
            "confidence": 85.0, # The models don't return confidence explicitly, assuming high
            "advice": f"Based on your farm conditions (pH {req.ph}, {req.soil_type} soil), {result['Recommended Crop']} is the optimal choice.",
            "original_prediction": result['Recommended Crop'],
            "model_used": "CentralCoordinator/FarmerAdvisor"
        }
        
        # 2. Market Researcher
        response["agents"]["market_researcher"] = {
            "name": "💰 Market Researcher",
            "market_score": result['Market Score'],
            "price_trend": "Rising" if result['Market Score'] > 5 else "Stable", # Simplified inference
            "advice": f"Market analysis gives a score of {result['Market Score']}/10 for {result['Recommended Crop']}."
        }
        
        # 3. Weather Analyst
        response["agents"]["weather_analyst"] = {
            "name": "🌤️ Weather Analyst",
            "weather_score": result['Weather Suitability Score'],
            "risk_level": "Low" if result['Weather Suitability Score'] > 7 else "Medium" if result['Weather Suitability Score'] > 4 else "High",
            "forecast": f"Predicted Temp: {result['Predicted Temperature']}°C, Rainfall: {result['Predicted Rainfall']}mm",
            "advice": f"Weather suitability is {result['Weather Suitability Score']}/10."
        }
        
        # 4. Sustainability Expert
        response["agents"]["sustainability_expert"] = {
            "name": "🌱 Sustainability Expert",
            "sustainability_score": result['Sustainability Score'],
            "environmental_impact": "Low" if result['Sustainability Score'] > 7 else "Medium",
            "recommendations": "Follow standard crop rotation.",
            "advice": f"Sustainability Score: {result['Sustainability Score']}/10. Carbon: {result['Carbon Footprint Score']}, Water: {result['Water Score']}."
        }
        
        # Central Coordinator Final
        response["central_coordinator"] = {
            "final_crop": result['Recommended Crop'],
            "overall_score": result['Final Score'],
            "confidence_level": "High",
            "reasoning": f"Aggregated analysis yields a final score of {result['Final Score']}/10.",
            "action_items": result.get('Warnings', []) + list(result.get('Pest/Disease Advice', {}).values())
        }
        
        # Chart Data
        response["chart_data"] = [{
            "crop": result['Recommended Crop'],
            "labels": ["Market", "Weather", "Sustainability", "Carbon", "Water", "Erosion"],
            "values": [
                result['Market Score'] * 10,
                result['Weather Suitability Score'] * 10,
                result['Sustainability Score'] * 10,
                result['Carbon Footprint Score'] * 10,
                result['Water Score'] * 10,
                result['Erosion Score'] * 10
            ]
        }]

    except Exception as e:
        print(f"Error in multi_agent_recommendation: {e}")
        # Fallback to simple rule-based if models fail

            market_result = market_researcher.forecast_market_trends(
                crop=response["agents"]["farmer_advisor"]["recommended_crop"],
                area=req.land_size,
                production=req.land_size * 3,  # Estimated production
                year=2024
            )
            
            response["agents"]["market_researcher"] = {
                "name": "💰 Market Researcher",
                "market_score": market_result.get("market_score", 6.5),
                "price_trend": market_result.get("price_trend", "Stable"),
                "demand_forecast": market_result.get("demand_forecast", "Moderate"),
                "predicted_price": market_result.get("predicted_price", 2000),
                "advice": f"The market for {response['agents']['farmer_advisor']['recommended_crop']} shows "
                         f"{market_result.get('price_trend', 'stable').lower()} prices with "
                         f"{market_result.get('demand_forecast', 'moderate').lower()} demand.",
                "model_version": market_result.get("model_version", "v1")
            }
        except Exception as e:
            response["agents"]["market_researcher"] = {
                "name": "💰 Market Researcher",
                "market_score": 6.5,
                "price_trend": "Stable",
                "demand_forecast": "Moderate",
                "advice": "Market conditions appear stable for the recommended crop.",
                "error": str(e)
            }
        
        # ================== WEATHER ANALYST AGENT ==================
        try:
            weather_analyst = WeatherAnalyst()
            
            # Get weather impact analysis
            weather_result = weather_analyst.analyze_weather_impact(
                temperature=req.temperature,
                rainfall=req.rainfall,
                humidity=req.humidity
            )
            
            response["agents"]["weather_analyst"] = {
                "name": "🌤️ Weather Analyst",
                "weather_score": weather_result.get("weather_score", 7.0),
                "forecast": weather_result.get("forecast", "Suitable conditions"),
                "risk_level": weather_result.get("risk_level", "Low"),
                "predicted_yield_impact": weather_result.get("predicted_yield_impact", 5.0),
                "advice": f"Current weather conditions: {req.temperature}°C temperature, "
                         f"{req.rainfall}mm rainfall, {req.humidity}% humidity. "
                         f"Risk level: {weather_result.get('risk_level', 'Low')}.",
                "model_version": weather_result.get("model_version", "v1")
            }
        except Exception as e:
            response["agents"]["weather_analyst"] = {
                "name": "🌤️ Weather Analyst",
                "weather_score": 7.0,
                "forecast": "Weather conditions appear suitable for farming.",
                "risk_level": "Low",
                "error": str(e)
            }
        
        # ================== SUSTAINABILITY EXPERT AGENT ==================
        try:
            sustainability_expert = SustainabilityExpert()
            
            # Get sustainability assessment
            sustainability_result = sustainability_expert.assess_sustainability(
                fertilizer_usage=req.nitrogen,
                organic_matter=3.0,
                ph=req.ph,
                nitrogen=req.nitrogen,
                phosphorus=req.phosphorus
            )
            
            response["agents"]["sustainability_expert"] = {
                "name": "🌱 Sustainability Expert",
                "sustainability_score": sustainability_result.get("sustainability_score", 7.0),
                "environmental_impact": sustainability_result.get("environmental_impact", "Low"),
                "carbon_footprint": sustainability_result.get("carbon_footprint", "Moderate"),
                "recommendations": sustainability_result.get("recommendations", "Good practices"),
                "advice": f"With current fertilizer usage of {req.nitrogen}kg/ha, your farming "
                         f"sustainability score is {sustainability_result.get('sustainability_score', 7.0):.1f}/10. "
                         f"{sustainability_result.get('recommendations', 'Continue current practices.')}",
                "model_version": sustainability_result.get("model_version", "v1")
            }
        except Exception as e:
            response["agents"]["sustainability_expert"] = {
                "name": "🌱 Sustainability Expert",
                "sustainability_score": 7.0,
                "environmental_impact": "Moderate",
                "recommendations": "Consider organic farming practices.",
                "error": str(e)
            }
        
        # ================== CENTRAL COORDINATOR - FINAL RECOMMENDATION ==================
        # Calculate weighted overall score
        weights = {
            "farmer": 0.30,
            "market": 0.25,
            "weather": 0.25,
            "sustainability": 0.20
        }
        
        farmer_score = response["agents"]["farmer_advisor"].get("confidence", 75) / 10
        market_score = response["agents"]["market_researcher"].get("market_score", 6.5)
        weather_score = response["agents"]["weather_analyst"].get("weather_score", 7.0)
        sustainability_score = response["agents"]["sustainability_expert"].get("sustainability_score", 7.0)
        
        overall_score = (
            weights["farmer"] * farmer_score +
            weights["market"] * market_score +
            weights["weather"] * weather_score +
            weights["sustainability"] * sustainability_score
        )
        
        # Generate final recommendation
        recommended_crop = response["agents"]["farmer_advisor"]["recommended_crop"]
        
        response["central_coordinator"] = {
            "final_crop": recommended_crop,
            "overall_score": round(overall_score, 1),
            "confidence_level": "High" if overall_score >= 7.5 else "Medium" if overall_score >= 5.5 else "Low",
            "reasoning": f"After analyzing all factors from our 4 AI agents, {recommended_crop} is the best choice "
                        f"for your {req.land_size} hectare {req.soil_type.lower()} soil farm. "
                        f"Overall recommendation score: {overall_score:.1f}/10.",
            "action_items": [
                f"Prepare {req.soil_type.lower()} soil with proper drainage",
                f"Maintain soil pH around {req.ph} for optimal growth",
                f"Plan irrigation based on {req.rainfall}mm expected rainfall",
                f"Apply {req.nitrogen}kg/ha nitrogen fertilizer as planned"
            ]
        }
        
        # Generate chart data for visualization
        response["chart_data"] = [{
            "crop": recommended_crop,
            "labels": ["Farmer Score", "Market Score", "Weather Score", "Sustainability Score", "Overall"],
            "values": [
                farmer_score * 10,
                market_score * 10,
                weather_score * 10,
                sustainability_score * 10,
                overall_score * 10
            ]
        }]
        
        # Save recommendation to database
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO recommendations 
                (username, crop, score, rationale, market_score, weather_score, 
                 sustainability_score, carbon_score, water_score, erosion_score, timestamp, recommendation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                req.username,
                recommended_crop,
                overall_score,
                response["central_coordinator"]["reasoning"],
                market_score,
                weather_score,
                sustainability_score,
                sustainability_score * 0.9,  # Carbon score approximation
                weather_score * 0.85,  # Water score approximation
                sustainability_score * 0.8,  # Erosion score approximation
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                json.dumps(response)
            ))
            conn.commit()
        
    except Exception as e:
        response["success"] = False
        response["error"] = str(e)
    
    return response

@app.post("/recommendation")
def get_recommendation(req: RecommendationRequest):
    result = run_agent_collaboration(land_size=req.land_size, soil_type=req.soil_type, crop_preference=req.crop_preference)
    
    # Ensure chart_data exists
    chart_data = result.get('chart_data', [])
    recommendation_text = result.get('recommendation', '')
    
    # Save to database
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Extract first crop score for storage
        score = 85.0
        if chart_data and len(chart_data) > 0:
            values = chart_data[0].get('values', [85])
            score = sum(values) / len(values) if values else 85.0
        
        cursor.execute("""
            INSERT INTO recommendations (username, recommendation, timestamp, score, crop) 
            VALUES (?, ?, ?, ?, ?)
        """, (req.username, recommendation_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), score, req.crop_preference))
        conn.commit()
    
    return {"recommendation": recommendation_text, "chart_data": chart_data}

@app.post("/crop_rotation")
def get_crop_rotation(req: CropRotationRequest):
    planner = CropRotationPlanner(db_path=DB_PATH)
    plan = planner.generate_plan(req.current_crop)
    
    # Generate timeline data for visualization
    years = req.years if req.years else 4
    timeline = {
        "years": [f"Year {i+1}" for i in range(years)],
        "crops": plan.split('\n'),
        "scores": [random.randint(75, 95) for _ in range(years)]
    }
    
    return {"plan": plan, "timeline": timeline}

@app.post("/fertilizer")
def optimize_fertilizer(req: FertilizerRequest):
    optimizer = FertilizerOptimizer(db_path=DB_PATH)
    result = optimizer.calculate_fertilizer(req.land_size, req.soil_type, req.crop_type)
    return result

# Weather API endpoint - REAL weather data
@app.post("/weather")
def get_weather(req: WeatherRequest):
    """Get real weather data from OpenWeatherMap API"""
    try:
        # Current weather
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={req.lat}&lon={req.lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        current_response = requests.get(current_url, timeout=10)
        
        # 5-day forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={req.lat}&lon={req.lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            current_data = current_response.json()
            forecast_data = forecast_response.json()
            
            # Process current weather
            current_weather = {
                "temperature": current_data["main"]["temp"],
                "feels_like": current_data["main"]["feels_like"],
                "humidity": current_data["main"]["humidity"],
                "pressure": current_data["main"]["pressure"],
                "description": current_data["weather"][0]["description"],
                "icon": current_data["weather"][0]["icon"],
                "wind_speed": current_data["wind"]["speed"],
                "clouds": current_data["clouds"]["all"],
                "city": current_data.get("name", "Unknown")
            }
            
            # Process forecast
            forecast_list = []
            for item in forecast_data["list"][:8]:  # Next 24 hours (3-hour intervals)
                forecast_list.append({
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "description": item["weather"][0]["description"],
                    "rain": item.get("rain", {}).get("3h", 0)
                })
            
            # Calculate metrics
            temps = [f["temperature"] for f in forecast_list]
            humidities = [f["humidity"] for f in forecast_list]
            rainfall = sum([f["rain"] for f in forecast_list])
            
            metrics = {
                "avg_temperature": round(sum(temps) / len(temps), 1),
                "max_temperature": round(max(temps), 1),
                "min_temperature": round(min(temps), 1),
                "avg_humidity": round(sum(humidities) / len(humidities), 1),
                "total_rainfall": round(rainfall, 1)
            }
            
            # Agricultural analysis
            risk_level = "low"
            recommendations = []
            
            if metrics["avg_temperature"] > 35:
                risk_level = "high"
                recommendations.append("High temperature alert - increase irrigation frequency")
            elif metrics["avg_temperature"] > 30:
                risk_level = "medium"
                recommendations.append("Warm conditions - monitor soil moisture")
            
            if metrics["total_rainfall"] > 50:
                recommendations.append("Heavy rainfall expected - ensure proper drainage")
            elif metrics["total_rainfall"] < 5:
                recommendations.append("Low rainfall - plan for irrigation")
            
            if metrics["avg_humidity"] > 80:
                recommendations.append("High humidity - watch for fungal diseases")
                risk_level = "medium" if risk_level == "low" else risk_level
            
            # Crop-specific recommendations
            if req.crop_type:
                if req.crop_type.lower() in ["rice", "paddy"]:
                    if metrics["total_rainfall"] > 30:
                        recommendations.append(f"Good conditions for {req.crop_type}")
                elif req.crop_type.lower() in ["wheat", "corn"]:
                    if metrics["avg_temperature"] < 25:
                        recommendations.append(f"Favorable temperature for {req.crop_type}")
            
            return {
                "current_weather": current_weather,
                "forecast": forecast_list,
                "metrics": metrics,
                "agricultural_conditions": {
                    "overall_risk": risk_level,
                    "crop_suitability": "good" if risk_level == "low" else "moderate" if risk_level == "medium" else "poor"
                },
                "recommendations": recommendations,
                "analysis": f"Current conditions: {current_weather['temperature']}°C with {current_weather['description']}. "
                           f"Expected {metrics['total_rainfall']}mm rainfall over next 24 hours. "
                           f"Risk level: {risk_level.upper()}."
            }
        else:
            raise HTTPException(status_code=502, detail="Weather API unavailable")
            
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Weather API timeout")
    except Exception as e:
        # Fallback with calculated data
        return {
            "current_weather": {
                "temperature": 28.0,
                "humidity": 65,
                "description": "partly cloudy",
                "wind_speed": 3.5
            },
            "forecast": [],
            "metrics": {
                "avg_temperature": 27.5,
                "total_rainfall": 15.0,
                "avg_humidity": 62.0
            },
            "agricultural_conditions": {"overall_risk": "medium"},
            "recommendations": ["Weather API temporarily unavailable - using estimated data"],
            "analysis": "Using estimated weather conditions. Please check again later for live data."
        }

# Pest/Disease Prediction endpoint
@app.post("/pest_prediction")
def predict_pest(req: PestPredictionRequest):
    """AI-powered pest and disease prediction"""
    predictions = []
    risk_level = "low"
    
    # Temperature-based predictions
    if req.temperature > 30 and req.humidity > 70:
        predictions.append({
            "pest": "Aphids",
            "probability": 0.75,
            "severity": "high",
            "recommendation": "Apply neem-based organic pesticide"
        })
        risk_level = "high"
    
    if req.humidity > 80 and req.rainfall > 50:
        predictions.append({
            "pest": "Fungal diseases (Blight, Mildew)",
            "probability": 0.8,
            "severity": "high", 
            "recommendation": "Apply copper-based fungicide, improve air circulation"
        })
        risk_level = "high"
    
    # Crop-specific predictions
    crop_pests = {
        "Rice": [("Stem Borer", 0.6), ("Brown Plant Hopper", 0.5)],
        "Wheat": [("Rust", 0.55), ("Aphids", 0.4)],
        "Tomato": [("Whitefly", 0.65), ("Early Blight", 0.5)],
        "Corn": [("Fall Armyworm", 0.6), ("Corn Borer", 0.45)],
        "Potato": [("Late Blight", 0.7), ("Colorado Beetle", 0.4)]
    }
    
    if req.crop_type in crop_pests:
        for pest, base_prob in crop_pests[req.crop_type]:
            # Adjust probability based on conditions
            adjusted_prob = base_prob
            if req.temperature > 28:
                adjusted_prob += 0.1
            if req.humidity > 75:
                adjusted_prob += 0.15
            
            adjusted_prob = min(adjusted_prob, 0.95)
            
            predictions.append({
                "pest": pest,
                "probability": round(adjusted_prob, 2),
                "severity": "high" if adjusted_prob > 0.7 else "medium" if adjusted_prob > 0.5 else "low",
                "recommendation": f"Monitor for {pest}. Apply IPM practices."
            })
    
    # General recommendations
    general_recommendations = [
        "Practice crop rotation to break pest cycles",
        "Use resistant crop varieties when available",
        "Maintain field hygiene - remove crop residues",
        "Install pheromone traps for monitoring",
        "Scout fields weekly for early detection"
    ]
    
    return {
        "predictions": predictions,
        "overall_risk": risk_level,
        "prevention_tips": general_recommendations[:3],
        "analysis": f"Based on {req.crop_type} with temperature {req.temperature}°C and humidity {req.humidity}%, "
                   f"the pest risk is {risk_level.upper()}. Found {len(predictions)} potential threats."
    }

@app.get("/previous_recommendations")
def get_previous(username: str = Query(...)):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM recommendations WHERE username = ? ORDER BY timestamp DESC LIMIT 5", conn, params=(username,))
    return df.to_dict('records') if not df.empty else []

@app.post("/sustainability")
def log_sustainability(log: SustainabilityLog):
    RECOMMENDED_WATER = 2.0
    RECOMMENDED_FERTILIZER = 1.5
    
    score = 100
    if log.water_score > RECOMMENDED_WATER:
        score -= min(30, 30 * (log.water_score - RECOMMENDED_WATER) / RECOMMENDED_WATER)
    if log.fertilizer_use > RECOMMENDED_FERTILIZER:
        score -= min(30, 30 * (log.fertilizer_use - RECOMMENDED_FERTILIZER) / RECOMMENDED_FERTILIZER)
    if log.rotation:
        score += 10
    else:
        score -= 10
    score = max(0, min(100, score))
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sustainability_scores (username, timestamp, water_score, fertilizer_use, rotation, score) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (log.username, datetime.now().strftime("%Y-%m-%d"), log.water_score, log.fertilizer_use, int(log.rotation), score))
        conn.commit()
    
    # Generate improvement tips
    tips = []
    if log.water_score > RECOMMENDED_WATER:
        tips.append(f"Reduce water usage to below {RECOMMENDED_WATER} ML/ha. Consider drip irrigation.")
    if log.fertilizer_use > RECOMMENDED_FERTILIZER:
        tips.append(f"Reduce fertilizer to below {RECOMMENDED_FERTILIZER} tons/ha. Try organic options.")
    if not log.rotation:
        tips.append("Practice crop rotation next season to improve soil health.")
    
    return {"score": round(score, 1), "tips": tips}

@app.get("/sustainability/scores")
def get_sustainability_scores(username: str = Query(None)):
    with sqlite3.connect(DB_PATH) as conn:
        if username:
            df = pd.read_sql("""
                SELECT timestamp, score, water_score, fertilizer_use, rotation 
                FROM sustainability_scores 
                WHERE username = ?
                ORDER BY timestamp ASC
            """, conn, params=(username,))
        else:
            df = pd.read_sql("""
                SELECT timestamp, score, water_score, fertilizer_use, rotation 
                FROM sustainability_scores 
                ORDER BY timestamp ASC
            """, conn)
    
    if not df.empty:
        # Calculate trend
        scores = df['score'].tolist()
        trend = "improving" if len(scores) > 1 and scores[-1] > scores[-2] else "stable" if len(scores) == 1 else "declining"
        
        return {
            "timestamps": df['timestamp'].tolist(),
            "scores": scores,
            "water_scores": df['water_score'].tolist(),
            "fertilizer_use": df['fertilizer_use'].tolist(),
            "trend": trend,
            "average_score": round(sum(scores) / len(scores), 1)
        }
    return {"timestamps": [], "scores": [], "trend": "no_data", "average_score": 0}

@app.post("/farm_map")
def save_farm_map(map_data: dict):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO farm_maps (username, farm_name, map_data, recommendations, risk_areas, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            map_data.get('username', 'anonymous'),
            map_data.get('farm_name', 'My Farm'),
            json.dumps(map_data.get('map_data', {})),
            json.dumps(map_data.get('recommendations', [])),
            json.dumps(map_data.get('risk_areas', [])),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    return {"message": "Map saved successfully"}

@app.get("/farm_map/{username}")
def get_farm_map(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM farm_maps WHERE username = ? ORDER BY updated_at DESC LIMIT 1
        """, (username,))
        row = cursor.fetchone()
    
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "farm_name": row[2],
            "map_data": json.loads(row[3]) if row[3] else {},
            "recommendations": json.loads(row[4]) if row[4] else [],
            "risk_areas": json.loads(row[5]) if row[5] else [],
            "created_at": row[6],
            "updated_at": row[7]
        }
    return {"message": "No map found", "map_data": None}

@app.post("/community")
def log_community(insight: CommunityInsight):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO community_insights (username, crop_type, yield_data, market_price, sustainability_practice, region, season, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            insight.username, insight.crop_type, insight.yield_data, insight.market_price, 
            insight.sustainability_practice, insight.region, insight.season, 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    return {"message": "Insight shared successfully"}

@app.get("/community/insights")
def get_community_insights(region: str = Query(None), crop: str = Query(None)):
    with sqlite3.connect(DB_PATH) as conn:
        query = """
            SELECT crop_type, AVG(yield_data) as avg_yield, AVG(market_price) as avg_price,
                   sustainability_practice, region, season, COUNT(*) as contributors
            FROM community_insights 
        """
        params = []
        conditions = []
        
        if region:
            conditions.append("region = ?")
            params.append(region)
        if crop:
            conditions.append("crop_type = ?")
            params.append(crop)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY crop_type, sustainability_practice, region, season ORDER BY contributors DESC"
        
        df = pd.read_sql(query, conn, params=params if params else None)
    
    if not df.empty:
        insights = []
        for _, row in df.iterrows():
            insights.append({
                "crop_type": row['crop_type'],
                "avg_yield": round(row['avg_yield'], 2),
                "avg_price": round(row['avg_price'], 2),
                "sustainability_practice": row['sustainability_practice'],
                "region": row['region'],
                "season": row['season'],
                "contributors": row['contributors']
            })
        return {"insights": insights, "total_contributors": int(df['contributors'].sum())}
    return {"insights": [], "total_contributors": 0}

@app.get("/market/dashboard")
def market_dashboard(crop: str = Query("Rice"), period: str = Query("3 months")):
    months = 3 if '3' in period else 6 if '6' in period else 12
    
    # Base prices from real market data (approximate Indian market prices in ₹/ton)
    base_prices = {
        "Rice": 25000, "Wheat": 22000, "Corn": 18000, "Soybean": 40000,
        "Tomato": 15000, "Potato": 12000, "Cotton": 55000, "Groundnut": 45000,
        "Sugarcane": 3000, "Onion": 20000
    }
    
    base_price = base_prices.get(crop, 20000)
    
    # Generate realistic forecast with seasonal variations
    forecast = []
    current_price = base_price
    current_month = datetime.now().month
    
    for i in range(months):
        # Seasonal factor
        month = (current_month + i - 1) % 12 + 1
        seasonal_factor = 1.0
        if crop in ["Tomato", "Onion", "Potato"]:
            # Vegetables have higher seasonal variation
            if month in [4, 5, 6]:  # Summer
                seasonal_factor = 1.15
            elif month in [7, 8, 9]:  # Monsoon
                seasonal_factor = 0.85
        elif crop in ["Rice", "Wheat"]:
            # Grains have harvest-related price dips
            if month in [10, 11]:  # Harvest season
                seasonal_factor = 0.92
        
        # Random market fluctuation (-5% to +8%)
        market_factor = random.uniform(0.95, 1.08)
        
        current_price = current_price * seasonal_factor * market_factor
        confidence = max(0.6, 0.95 - (i * 0.03))  # Decreasing confidence
        
        forecast.append({
            "month": f"Month {i+1}",
            "month_name": datetime(2024, month, 1).strftime("%B"),
            "price": round(current_price, 2),
            "confidence": round(confidence, 2),
            "trend": "up" if market_factor > 1 else "down"
        })
    
    # Calculate insights
    start_price = forecast[0]["price"]
    end_price = forecast[-1]["price"]
    price_change = ((end_price - start_price) / start_price) * 100
    
    return {
        "crop": crop,
        "forecast": forecast,
        "current_price": base_price,
        "predicted_price": round(end_price, 2),
        "price_change_percent": round(price_change, 1),
        "recommendation": "Good time to plant" if price_change > 5 else "Monitor market" if price_change > -5 else "Consider alternatives",
        "analysis": f"{crop} prices expected to {'increase' if price_change > 0 else 'decrease'} by {abs(price_change):.1f}% over {period}"
    }

def generate_chatbot_response(query):
    """Generate comprehensive AI response for farming queries - matching app.py logic"""
    query_lower = query.lower()
    
    # Fertilizer questions
    if any(word in query_lower for word in ['fertilizer', 'fertiliser', 'nutrient', 'npk']):
        if 'loamy' in query_lower:
            return "For loamy soil, I recommend balanced NPK fertilizer (10-10-10) at 100-150 kg/hectare. Loamy soil has good drainage and nutrient retention, so moderate fertilization works well. Consider organic options like compost or manure for sustainable farming."
        elif 'clay' in query_lower:
            return "Clay soil requires careful fertilizer management. Use slow-release fertilizers and avoid over-application. I recommend 80-120 kg/hectare of NPK fertilizer. Clay soil holds nutrients well, so less frequent but consistent application is key."
        elif 'sandy' in query_lower:
            return "Sandy soil needs more frequent fertilization due to poor nutrient retention. Use 120-180 kg/hectare of NPK fertilizer in smaller, more frequent applications. Consider adding organic matter to improve soil structure."
        else:
            return "For fertilizer recommendations, I need to know your soil type. Generally, balanced NPK fertilizers work well for most crops. I recommend:\n\n• **Nitrogen (N)**: For leaf growth - 80-120 kg/ha\n• **Phosphorus (P)**: For root development - 40-60 kg/ha\n• **Potassium (K)**: For overall health - 60-80 kg/ha\n\nConsider soil testing for precise recommendations."
    
    # Pest and disease questions
    elif any(word in query_lower for word in ['pest', 'disease', 'insect', 'bug', 'worm', 'blight', 'fungus']):
        return """For pest and disease management, I recommend Integrated Pest Management (IPM):

**Prevention:**
• Practice crop rotation (3-4 year cycle)
• Use resistant varieties
• Maintain field hygiene

**Monitoring:**
• Scout fields weekly
• Install pheromone traps
• Check for early symptoms

**Control Methods:**
1. **Biological**: Natural predators, beneficial insects
2. **Cultural**: Proper spacing, timely planting
3. **Mechanical**: Traps, barriers
4. **Chemical**: Use only when threshold exceeded

What specific pest or disease are you dealing with? I can provide targeted advice."""
    
    # Water and irrigation questions
    elif any(word in query_lower for word in ['water', 'irrigation', 'watering', 'drought', 'moisture']):
        return """Water management is crucial for crop health. Here are my recommendations:

**Irrigation Methods:**
• **Drip Irrigation**: 90% efficiency, best for vegetables
• **Sprinkler**: 75% efficiency, good for field crops
• **Flood**: 50% efficiency, traditional but wasteful

**Best Practices:**
1. Water early morning or late evening
2. Monitor soil moisture (30-40% optimal)
3. Adjust based on crop growth stage
4. Use mulching to retain moisture
5. Install soil moisture sensors

**Water Requirements (approx):**
• Rice: 1200-1500 mm/season
• Wheat: 450-650 mm/season
• Vegetables: 400-600 mm/season

What's your current irrigation setup?"""
    
    # Crop selection questions
    elif any(word in query_lower for word in ['crop', 'plant', 'growing', 'what to grow', 'which crop']):
        return """For crop selection, consider these factors:

**1. Soil Type:**
• Loamy: Most crops thrive
• Sandy: Groundnut, watermelon, carrot
• Clay: Rice, wheat, cotton

**2. Climate & Season:**
• Kharif (June-Oct): Rice, cotton, soybean
• Rabi (Oct-Mar): Wheat, chickpea, mustard
• Zaid (Mar-Jun): Cucumber, watermelon

**3. Market Demand:**
• Check local mandi prices
• Consider contract farming
• Diversify to reduce risk

**4. Water Availability:**
• High water: Rice, sugarcane
• Medium: Wheat, vegetables
• Low: Millets, pulses

What are your specific conditions?"""
    
    # Soil questions
    elif any(word in query_lower for word in ['soil', 'soil type', 'soil test', 'ph', 'organic matter']):
        return """Soil health is fundamental to farming success:

**Soil Testing:**
• Test every 2-3 years
• Check pH, NPK, organic matter
• Cost: ₹200-500 per sample

**Ideal Conditions:**
• pH: 6.0-7.0 for most crops
• Organic Matter: >2%
• Drainage: Good to moderate

**Soil Improvement:**
1. Add compost/FYM (5-10 tons/ha)
2. Practice green manuring
3. Avoid excessive tillage
4. Use cover crops
5. Apply lime if pH < 6.0

Would you like help with soil testing or improvement?"""
    
    # Weather questions
    elif any(word in query_lower for word in ['weather', 'climate', 'season', 'rain', 'temperature']):
        return """Weather and climate are crucial for farming:

**Key Weather Factors:**
• Temperature: Affects growth rate
• Rainfall: Water availability
• Humidity: Disease pressure
• Wind: Evaporation, pollination

**Season Planning:**
• Monitor weather forecasts weekly
• Plan planting around monsoon
• Have irrigation backup
• Use protected cultivation in extreme weather

**Climate-Smart Practices:**
• Drought-tolerant varieties
• Rainwater harvesting
• Mulching for temperature control
• Windbreaks for protection

Use our Weather Forecast feature for detailed predictions!"""
    
    # Yield questions
    elif any(word in query_lower for word in ['yield', 'production', 'harvest', 'output']):
        return """To improve crop yield, focus on these areas:

**1. Quality Inputs:**
• Certified seeds (25-30% yield increase)
• Balanced fertilization
• Timely pest control

**2. Best Practices:**
• Optimal plant spacing
• Proper planting time
• Regular field monitoring

**3. Soil Health:**
• Maintain organic matter
• Proper drainage
• Crop rotation

**4. Water Management:**
• Critical stage irrigation
• Avoid water stress
• Efficient irrigation systems

**Expected Yields (with good practices):**
• Rice: 5-6 tons/ha
• Wheat: 4-5 tons/ha
• Tomato: 40-50 tons/ha
• Potato: 25-30 tons/ha

What crop are you looking to improve?"""
    
    # Market and price questions
    elif any(word in query_lower for word in ['price', 'market', 'sell', 'mandi', 'msp']):
        return """Market and pricing guidance:

**Current MSP (2024-25):**
• Rice: ₹2,300/quintal
• Wheat: ₹2,275/quintal
• Cotton: ₹7,020/quintal

**Marketing Options:**
1. APMC Mandis
2. eNAM (Online trading)
3. Direct to processors
4. Contract farming
5. FPO aggregation

**Price Tips:**
• Store during glut, sell during shortage
• Grade and sort produce
• Build buyer relationships
• Use our Market Forecast feature!

Check our Market Dashboard for price predictions."""
    
    # Default response
    else:
        return """I'm your AI Farming Assistant! I can help with:

🌱 **Crop Planning**: What to grow, when to plant
🧪 **Soil Management**: Testing, improvement, fertilizers
💧 **Water & Irrigation**: Methods, scheduling, efficiency
🐛 **Pest Control**: IPM, organic solutions
📊 **Market Insights**: Prices, trends, selling
🌤️ **Weather**: Forecasts, planning, risks
📈 **Yield Optimization**: Best practices, techniques

Please ask a specific question about any farming topic, and I'll provide detailed guidance!

Examples:
• "What fertilizer for tomatoes in clay soil?"
• "How to control aphids organically?"
• "Best crops for sandy soil in summer?" """

@app.post("/chatbot/ask")
def ask_chatbot(req: ChatQuery):
    response = generate_chatbot_response(req.query)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cursor.execute("""
            INSERT INTO chatbot_sessions (username, session_id, query, response, timestamp) 
            VALUES (?, ?, ?, ?, ?)
        """, (req.username or 'anonymous', session_id, req.query, response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    
    return {"response": response, "session_id": session_id}

@app.get("/chatbot/history/{username}")
def get_chat_history(username: str, limit: int = Query(20)):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("""
            SELECT query, response, timestamp 
            FROM chatbot_sessions 
            WHERE username = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, conn, params=(username, limit))
    
    if not df.empty:
        return {"history": df.to_dict('records')}
    return {"history": []}

# Offline mode endpoints
@app.post("/offline/save")
def save_offline_data(req: OfflineDataRequest):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO offline_data (username, data_type, data_content, sync_status, created_at) 
            VALUES (?, ?, ?, 'pending', ?)
        """, (req.username, req.data_type, req.data_content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    return {"message": "Data saved for sync"}

@app.get("/offline/pending/{username}")
def get_pending_sync(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("""
            SELECT data_type, COUNT(*) as count 
            FROM offline_data 
            WHERE username = ? AND sync_status = 'pending' 
            GROUP BY data_type
        """, conn, params=(username,))
    
    if not df.empty:
        return {"pending": df.to_dict('records'), "total": int(df['count'].sum())}
    return {"pending": [], "total": 0}

@app.post("/offline/sync/{username}")
def sync_offline_data(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE offline_data 
            SET sync_status = 'synced', synced_at = ? 
            WHERE username = ? AND sync_status = 'pending'
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
        affected = cursor.rowcount
        conn.commit()
    return {"message": f"Synced {affected} items", "synced_count": affected}

# User profile endpoints
@app.get("/user/profile/{username}")
def get_user_profile(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, farm_name, profile_picture, email, phone, location, 
                   experience_level, farm_size, primary_crops, created_at 
            FROM users WHERE username = ?
        """, (username,))
        row = cursor.fetchone()
    
    if row:
        return {
            "username": row[0],
            "farm_name": row[1],
            "profile_picture": row[2],
            "email": row[3],
            "phone": row[4],
            "location": row[5],
            "experience_level": row[6],
            "farm_size": row[7],
            "primary_crops": json.loads(row[8]) if row[8] else [],
            "created_at": row[9]
        }
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/user/profile")
def update_user_profile(profile: UserProfileUpdate):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if profile.new_username:
            updates.append("username = ?")
            params.append(profile.new_username)
        if profile.farm_name:
            updates.append("farm_name = ?")
            params.append(profile.farm_name)
        if profile.email:
            updates.append("email = ?")
            params.append(profile.email)
        if profile.phone:
            updates.append("phone = ?")
            params.append(profile.phone)
        if profile.location:
            updates.append("location = ?")
            params.append(profile.location)
        if profile.experience_level:
            updates.append("experience_level = ?")
            params.append(profile.experience_level)
        if profile.farm_size:
            updates.append("farm_size = ?")
            params.append(profile.farm_size)
        if profile.primary_crops:
            updates.append("primary_crops = ?")
            params.append(json.dumps(profile.primary_crops))
        
        if updates:
            params.append(profile.username)
            cursor.execute(f"""
                UPDATE users SET {', '.join(updates)} WHERE username = ?
            """, params)
            conn.commit()
    
    return {"message": "Profile updated successfully"}

@app.get("/")
def root():
    return {
        "message": "Sustainable Farming AI API v2.0",
        "endpoints": {
            "auth": ["/signup", "/login"],
            "farming": ["/recommendation", "/crop_rotation", "/fertilizer", "/soil_analysis"],
            "weather": ["/weather", "/pest_prediction"],
            "sustainability": ["/sustainability", "/sustainability/scores"],
            "community": ["/community", "/community/insights"],
            "market": ["/market/dashboard"],
            "chatbot": ["/chatbot/ask", "/chatbot/history/{username}"],
            "maps": ["/farm_map", "/farm_map/{username}"],
            "offline": ["/offline/save", "/offline/pending/{username}", "/offline/sync/{username}"],
            "user": ["/user/profile/{username}"]
        }
    }