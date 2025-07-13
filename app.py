import streamlit as st
import speech_recognition as sr
import pyttsx3
import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime
from agents.init_db import initialize_db
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import re

# Set page config as the first Streamlit command
st.set_page_config(page_title="Sustainable Farming Recommendation System", page_icon="🌾")

# Add the 'agents' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'agents')))


# Import the run_agent_collaboration function from agent_setup
from agents.agent_setup import run_agent_collaboration

# Import WeatherAnalyst and PestDiseasePredictor
from models.weather_Analyst import WeatherAnalyst
from models.pest_disease_predictor import PestDiseasePredictor

# --- Soil Analysis Function ---
def analyze_soil_from_photo(uploaded_file):
    try:
        image = Image.open(uploaded_file).convert("RGB")
        image_array = np.array(image)
        avg_color = np.mean(image_array, axis=(0, 1))
        r, g, b = avg_color

        # Define typical RGB ranges for soil types
        if r > 120 and g < 110 and b < 110 and r > g and r > b:
            return "Clay"
        elif r > 90 and g > 90 and b < 80 and abs(r - g) < 30:
            return "Sandy"
        elif r < 120 and g < 120 and b < 120 and abs(r - g) < 20 and abs(g - b) < 20:
            return "Loamy"

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
        return min(distances, key=distances.get)
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

# --- Voice Input/Output Utilities ---
def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("Listening... Please speak now.")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
    try:
        st.info("Transcribing...")
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.warning("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# --- Recommendation Parsing ---
def parse_recommendation(recommendation_text):
    crops_data = []
    crop_entries = recommendation_text.split("Plant ")[1:]
    for entry in crop_entries:
        crop_match = re.match(r"(\w+):", entry)
        if not crop_match:
            continue
        crop = crop_match.group(1)
        scores = {
            "Market Score": float(re.search(r"market score: ([\d.]+)", entry).group(1)),
            "Weather Suitability": float(re.search(r"weather suitability: ([\d.]+)", entry).group(1)),
            "Sustainability": float(re.search(r"sustainability: ([\d.]+)", entry).group(1)),
            "Carbon Footprint": float(re.search(r"carbon footprint: ([\d.]+)", entry).group(1)),
            "Water": float(re.search(r"water: ([\d.]+)", entry).group(1)),
            "Erosion": float(re.search(r"erosion: ([\d.]+)", entry).group(1)),
            "Final Score": float(re.search(r"Final Score: ([\d.]+)", entry).group(1))
        }
        price_match = re.search(r"\(\$([\d.]+)/ton\)", entry)
        market_price = float(price_match.group(1)) if price_match else 0.0
        crops_data.append({"crop": crop, "scores": scores, "market_price": market_price})
    return crops_data

# --- Custom CSS ---
st.markdown("""
    <style>
    :root {
        --primary-color: #2E7D32;
        --secondary-color: #1565C0;
        --accent-color: #FF6D00;
        --background-color: #F5F7F9;
    }
    .main { background-color: var(--background-color); padding: 2rem; }
    .stButton>button { width: 100%; margin-top: 1rem; margin-bottom: 2rem; background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); color: white; border: none; border-radius: 10px; padding: 0.75rem; font-weight: 600; transition: transform 0.2s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 8px rgba(0,0,0,0.15); }
    .recommendation-box { background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border-left: 6px solid #4CAF50; padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 8px 16px rgba(0,0,0,0.1); transition: transform 0.3s ease; }
    .recommendation-box:hover { transform: translateY(-5px); }
    .score-header { text-align: center; color: #2C3E50; margin-bottom: 2rem; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .stRadio>label, .stSelectbox { background: white; padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin: 5px; }
    .stFileUploader { background: white; padding: 20px; border-radius: 10px; border: 2px dashed #4CAF50; }
    .stSuccess { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 20px; border-radius: 10px; color: white; }
    .stWarning { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 20px; border-radius: 10px; color: white; }
    .dataframe { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    hr { border: none; height: 3px; background: linear-gradient(90deg, #4CAF50 0%, #1565C0 100%); margin: 2rem 0; }
    </style>
""", unsafe_allow_html=True)

# --- Main Content ---
st.markdown("""
<div class='recommendation-box' style='background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%); color: white;'>
    <h2 style='color: white; font-size: 2.5em; margin-bottom: 20px;'>🌾 Smart Farming Assistant</h2>
    <p style='font-size: 1.2em; margin-bottom: 15px;'>Get AI-powered recommendations based on:</p>
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>📊 Market Analysis</div>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>🌤️ Weather Patterns</div>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>🌱 Sustainability Metrics</div>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>🌍 Environmental Impact</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'><h3 style='color: #2E7D32;'>📏 Farm Details</h3></div>", unsafe_allow_html=True)
    land_size = st.select_slider("Farm size (hectares)", options=[1, 2, 5, 8, 10, 15, 20], value=8, help="Slide to select your farm size")

with col2:
    st.markdown("<div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'><h3 style='color: #2E7D32;'>🌱 Crop Preference</h3></div>", unsafe_allow_html=True)
    crop_preference = st.selectbox("What would you like to grow?", options=["Grains", "Vegetables", "Fruits"], help="Choose your preferred crop type")

# --- Soil Type Input with Both Options ---
st.markdown("### 🗺️ Soil Analysis")
soil_type = None
soil_option = st.radio("How would you like to determine your soil type?", ["📸 Upload a photo", "📝 Manual selection"], horizontal=True)

if soil_option == "📸 Upload a photo":
    soil_photo = st.file_uploader("Upload soil photo", type=["jpg", "jpeg", "png"], key="soil_photo_uploader")
    if soil_photo:
        soil_type = analyze_soil_from_photo(soil_photo)
        if soil_type:
            st.success(f"✅ Detected soil type: {soil_type}")
            st.success(f"✅ Detected soil type: {soil_type}")
        else:
            st.warning("⚠️ Could not determine soil type from photo. Please select manually.")
            soil_type = st.selectbox("Select soil type", options=["Loamy", "Sandy", "Clay"], key="manual_soil_select")
    else:
        soil_type = st.selectbox("Select soil type", options=["Loamy", "Sandy", "Clay"], key="manual_soil_select_fallback")
elif soil_option == "📝 Manual selection":
    soil_type = st.selectbox("Select soil type", options=["Loamy", "Sandy", "Clay"], key="manual_soil_select")

# Initialize database if it doesn't exist
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db'))
if not os.path.exists(db_path):
    initialize_db()

# --- Recommendation Generation ---
st.markdown("<br>", unsafe_allow_html=True)

if st.button("💡 Generate Smart Recommendation", type="primary"):
    with st.spinner("🔄 Analyzing your farm conditions..."):
        try:
            result = run_agent_collaboration(land_size=land_size, soil_type=soil_type, crop_preference=crop_preference)
            crops_data = parse_recommendation(result['recommendation'])

            # --- Weather Forecasting (using WeatherAnalyst) ---
            weather_analyst = WeatherAnalyst()
            # Example: use default or dummy values for demonstration; replace with real user input if available
            soil_ph = 6.5
            soil_moisture = 25
            fertilizer = 50
            pesticide = 5
            weather_forecast = weather_analyst.forecast(soil_ph, soil_moisture, fertilizer, pesticide)
            st.markdown("#### 🌤️ Weather Forecast (AI Model)")
            st.info(f"Predicted Temperature: {weather_forecast['temperature'][0]:.1f}°C, Predicted Rainfall: {weather_forecast['rainfall'][0]:.1f} mm")

            # --- Pest/Disease Prediction (using PestDiseasePredictor) ---
            pest_predictor = PestDiseasePredictor()
            pest_prediction = pest_predictor.predict(
                crop_type=crop_preference,
                soil_ph=soil_ph,
                soil_moisture=soil_moisture,
                temperature=weather_forecast['temperature'][0],
                rainfall=weather_forecast['rainfall'][0]
            )
            st.markdown("#### 🐛 Pest/Disease Prediction (AI Model)")
            st.info(pest_prediction)

            st.markdown("### 🎯 Your Personalized Recommendation")

            details = result['recommendation'].split("Details:")[1].strip()
            details_html = details.replace('\n', '<br>')
            st.markdown(f"<div class='recommendation-box'><strong>Details:</strong><br>{details_html}</div>", unsafe_allow_html=True)

            # --- Weather Forecasting Display (from agent, if present) ---
            if 'Weather Forecast' in result and result['Weather Forecast']:
                st.markdown("#### 🌤️ Weather Forecast (Agent)")
                st.info(result['Weather Forecast'])

            # --- Pest/Disease Prediction Display (from agent, if present) ---
            if 'Pest/Disease Prediction' in result and result['Pest/Disease Prediction']:
                st.markdown("#### 🐛 Pest/Disease Prediction (Agent)")
                st.info(result['Pest/Disease Prediction'])

            # --- Weather Alerts ---
            if 'Warnings' in result and result['Warnings']:
                for warn in result['Warnings']:
                    st.warning(f"Weather Alert: {warn}")

            # --- Pest/Disease Advice ---
            if 'Pest/Disease Advice' in result and result['Pest/Disease Advice']:
                st.info(f"Pest/Disease Advice: {result['Pest/Disease Advice']}")

            for crop_data in crops_data:
                crop = crop_data['crop']
                scores = crop_data['scores']
                market_price = crop_data['market_price']
                labels = list(scores.keys())
                values = [score * 100 for score in scores.values()]
                fig = go.Figure(data=[go.Bar(y=labels, x=values, orientation='h', marker=dict(color=[
                    "#4caf50", "#2196f3", "#ff9800", "#607d8b", "#00bcd4", "#795548", "#e91e63"
                ]), text=[f"{val:.1f}%" for val in values], textposition='auto')])
                fig.update_layout(title=f"{crop.capitalize()} Scores (Market Price: ${market_price:.2f}/ton)", title_x=0.5, xaxis_title="Score (%)", yaxis_title="Category", xaxis=dict(range=[0, 100]), margin=dict(l=0, r=0, t=40, b=0), height=400)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("<h3 class='score-header'>📊 Detailed Score Analysis</h3>", unsafe_allow_html=True)
            for chart in result['chart_data']:
                crop = chart['crop']
                labels = chart['labels']
                values = chart['values']
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent', hoverinfo='label+value', marker=dict(colors=[
                    "#4caf50", "#2196f3", "#ff9800", "#607d8b", "#00bcd4", "#795548", "#e91e63"
                ]))])
                fig.update_layout(title=f"{crop.capitalize()} Score Distribution", title_x=0.5, margin=dict(l=0, r=0, t=40, b=0), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")
# ... (existing imports at the top of app.py)

from crop_rotation_planner import CropRotationPlanner

# ... (existing code up to the recommendation generation)

# --- Crop Rotation Planner Section ---
st.markdown("<hr>", unsafe_allow_html=True)
st.header("🌱 Crop Rotation Planner")
planner = CropRotationPlanner(db_path=os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db')))
try:
    with sqlite3.connect(os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db'))) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT crop FROM recommendations ORDER BY timestamp DESC LIMIT 1")
        latest_crop = cursor.fetchone()
    if latest_crop:
        latest_crop = latest_crop[0]
        plan = planner.generate_plan(latest_crop)
        st.success(f"Last planted crop: {latest_crop}. Suggested rotation plan:")
        st.plotly_chart(planner.create_timeline(plan), use_container_width=True)
    else:
        st.info("No crop history found. Generate a recommendation to start building your rotation plan!")
except Exception as e:
    st.warning(f"Could not load crop rotation plan: {str(e)}")

# ... (existing imports at the top of app.py)

from fertilizer_optimizer import FertilizerOptimizer

# ... (existing code up to the crop rotation planner)

# --- Fertilizer Optimization Calculator Section ---
st.markdown("<hr>", unsafe_allow_html=True)
st.header("🧪 Fertilizer Optimization Calculator")
with st.form("fertilizer_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        fert_soil = st.selectbox("Soil Type", ["Loamy", "Sandy", "Clay"], key="fert_soil")
    with col2:
        fert_crop = st.selectbox("Crop Type", ["Wheat", "Corn", "Rice", "Soybeans", "Tomatoes", "Carrots"], key="fert_crop")
    with col3:
        fert_land = st.number_input("Land Size (hectares)", min_value=1, max_value=100, value=8, key="fert_land")
    submitted = st.form_submit_button("Calculate Optimal Fertilizer")
if submitted and 'fert_soil' in st.session_state and 'fert_crop' in st.session_state and 'fert_land' in st.session_state:
    optimizer = FertilizerOptimizer(db_path=os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db')))
    result = optimizer.calculate_fertilizer(st.session_state['fert_land'], st.session_state['fert_soil'], st.session_state['fert_crop'])
    st.success(f"For {st.session_state['fert_land']} hectares of {st.session_state['fert_soil'].lower()} soil planting {st.session_state['fert_crop'].lower()}, use:")
    st.write(f"- Nitrogen: {result['nitrogen_kg']} kg")
    st.write(f"- Phosphorus: {result['phosphorus_kg']} kg")
    st.write(f"- Potassium: {result['potassium_kg']} kg")
    st.caption("*This recommendation factors in sustainability by reducing excess fertilizer to lower carbon footprint.")


# --- Past Recommendations ---
st.markdown("<h3 class='score-header'>📜 Previous Recommendations</h3>", unsafe_allow_html=True)
st.subheader("Past Recommendations", divider="green")
try:
    with sqlite3.connect(db_path) as conn:
        past_recommendations = pd.read_sql("SELECT * FROM recommendations ORDER BY timestamp DESC LIMIT 5", conn)
    if not past_recommendations.empty:
        st.dataframe(
            past_recommendations[['crop', 'score', 'rationale', 'carbon_score', 'water_score', 'erosion_score', 'timestamp']],
            use_container_width=True,
            column_config={
                "crop": "Crop",
                "score": "Final Score",
                "rationale": "Rationale",
                "carbon_score": "Carbon Footprint Score",
                "water_score": "Water Score",
                "erosion_score": "Erosion Score",
                "timestamp": "Timestamp"
            },
            hide_index=True
        )
    else:
        st.info("No past recommendations found.")
except Exception as e:
    st.warning(f"Could not load past recommendations: {str(e)}")

# --- Voice Assistant Sidebar ---
st.sidebar.header("🎤 Voice Assistant")
if st.sidebar.button("Start Voice Input", key="voice_input_btn_sidebar"):
    try:
        user_query = recognize_speech_from_mic()
        if user_query:
            st.sidebar.success(f"You said: {user_query}")
            land_size = 8
            crop_preference = "Grains"
            soil_type = "Loamy"
            size_match = re.search(r'(\d+)[- ]*hectare', user_query)
            if size_match:
                land_size = int(size_match.group(1))
            for pref in ["grains", "vegetables", "fruits"]:
                if pref in user_query.lower():
                    crop_preference = pref.capitalize()
            for s in ["loamy", "sandy", "clay"]:
                if s in user_query.lower():
                    soil_type = s.capitalize()
            result = run_agent_collaboration(land_size=land_size, soil_type=soil_type, crop_preference=crop_preference)
            rec_text = result['recommendation'].split("\n")[1] if '\n' in result['recommendation'] else result['recommendation']
            speak_text(rec_text)
            st.sidebar.success(f"Recommendation: {rec_text}")
    except Exception as e:
        st.sidebar.error(f"Voice input error: {str(e)}")
if st.sidebar.button("Test Voice Output", key="voice_output_btn_sidebar"):
    try:
        speak_text("I recommend planting soybeans with a final score of 0.69.")
        st.sidebar.success("Voice output played.")
    except Exception as e:
        st.sidebar.error(f"Voice output error: {str(e)}")

# --- Footer ---
current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
st.markdown(f"""
---
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ for sustainable farming</p>
    <p><small>Last updated: {current_time}</small></p>
</div>

""", unsafe_allow_html=True)
