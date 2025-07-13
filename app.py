
import streamlit as st
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

# --- Multilingual Support ---
LANGUAGES = {
    ... # existing LANGUAGES dictionary
}

# Set page config FIRST, before any other Streamlit command
st.set_page_config(page_title=LANGUAGES['English']['title'], page_icon="🌾")

# --- Multilingual Support ---
LANGUAGES = {
    'English': {
        'title': "Sustainable Farming Recommendation System",
        'farm_details': "📏 Farm Details",
        'crop_preference': "🌱 Crop Preference",
        'soil_analysis': "🗺️ Soil Analysis",
        'upload_photo': "📸 Upload a photo",
        'manual_selection': "📝 Manual selection",
        'select_soil_type': "Select soil type",
        'generate_recommendation': "💡 Generate Smart Recommendation",
        'personalized_recommendation': "### 🎯 Your Personalized Recommendation",
        'weather_forecast': "#### 🌤️ Weather Forecast (AI Model)",
        'pest_prediction': "#### 🐛 Pest/Disease Prediction (AI Model)",
        'details': "Details:",
        'crop_rotation_planner': "🌱 Crop Rotation Planner",
        'fertilizer_optimization': "🧪 Fertilizer Optimization Calculator",
        'previous_recommendations': "📜 Previous Recommendations",
        'built_with': "Built with ❤️ for sustainable farming",
        'last_updated': "Last updated: "
    },
    'Telugu': {
        'title': "సస్టైనబుల్ వ్యవసాయ సూచన వ్యవస్థ",
        'farm_details': "📏 వ్యవసాయ వివరాలు",
        'crop_preference': "🌱 పంట ప్రాధాన్యత",
        'soil_analysis': "🗺️ నేల విశ్లేషణ",
        'upload_photo': "📸 ఫోటోను అప్‌లోడ్ చేయండి",
        'manual_selection': "📝 మాన్యువల్ ఎంపిక",
        'select_soil_type': "నేల రకాన్ని ఎంచుకోండి",
        'generate_recommendation': "💡 స్మార్ట్ సూచనను రూపొందించండి",
        'personalized_recommendation': "### 🎯 మీ వ్యక్తిగత సూచన",
        'weather_forecast': "#### 🌤️ వాతావరణ సూచన (AI మోడల్)",
        'pest_prediction': "#### 🐛 తెగులు/పురుగు సూచన (AI మోడల్)",
        'details': "వివరాలు:",
        'crop_rotation_planner': "🌱 పంట మార్పిడి ప్రణాళిక",
        'fertilizer_optimization': "🧪 ఎరువు ఆప్టిమైజేషన్ కాలిక్యులేటర్",
        'previous_recommendations': "📜 గత సూచనలు",
        'built_with': "సస్టైనబుల్ వ్యవసాయం కోసం ప్రేమతో నిర్మించబడింది",
        'last_updated': "చివరిగా నవీకరించబడింది: "
    },
    'Kannada': {
        'title': "ಸ್ಥಿರ ಕೃಷಿ ಶಿಫಾರಸು ವ್ಯವಸ್ಥೆ",
        'farm_details': "📏 ಕೃಷಿ ವಿವರಗಳು",
        'crop_preference': "🌱 ಬೆಳೆ ಆದ್ಯತೆ",
        'soil_analysis': "🗺️ ಮಣ್ಣು ವಿಶ್ಲೇಷಣೆ",
        'upload_photo': "📸 ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        'manual_selection': "📝 ಕೈಯಾರೆ ಆಯ್ಕೆ",
        'select_soil_type': "ಮಣ್ಣಿನ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        'generate_recommendation': "💡 ಸ್ಮಾರ್ಟ್ ಶಿಫಾರಸು ರಚಿಸಿ",
        'personalized_recommendation': "### 🎯 ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಶಿಫಾರಸು",
        'weather_forecast': "#### 🌤️ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ (AI ಮಾದರಿ)",
        'pest_prediction': "#### 🐛 ಕೀಟ/ರೋಗ ಮುನ್ಸೂಚನೆ (AI ಮಾದರಿ)",
        'details': "ವಿವರಗಳು:",
        'crop_rotation_planner': "🌱 ಬೆಳೆ ಪರಿವರ್ತನೆ ಯೋಜನೆ",
        'fertilizer_optimization': "🧪 ರಸಗೊಬ್ಬರ ಆಪ್ಟಿಮೈಸೇಶನ್ ಕ್ಯಾಲ್ಕ್ಯುಲೇಟರ್",
        'previous_recommendations': "📜 ಹಿಂದಿನ ಶಿಫಾರಸುಗಳು",
        'built_with': "ಸ್ಥಿರ ಕೃಷಿಗಾಗಿ ಪ್ರೀತಿಯಿಂದ ನಿರ್ಮಿಸಲಾಗಿದೆ",
        'last_updated': "ಕೊನೆಯದಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ: "
    },
    'Hindi': {
        'title': "सस्टेनेबल फार्मिंग सिफारिश प्रणाली",
        'farm_details': "📏 कृषि विवरण",
        'crop_preference': "🌱 फसल प्राथमिकता",
        'soil_analysis': "🗺️ मिट्टी विश्लेषण",
        'upload_photo': "📸 फोटो अपलोड करें",
        'manual_selection': "📝 मैन्युअल चयन",
        'select_soil_type': "मिट्टी का प्रकार चुनें",
        'generate_recommendation': "💡 स्मार्ट सिफारिश उत्पन्न करें",
        'personalized_recommendation': "### 🎯 आपकी व्यक्तिगत सिफारिश",
        'weather_forecast': "#### 🌤️ मौसम पूर्वानुमान (AI मॉडल)",
        'pest_prediction': "#### 🐛 कीट/रोग पूर्वानुमान (AI मॉडल)",
        'details': "विवरण:",
        'crop_rotation_planner': "🌱 फसल चक्र योजना",
        'fertilizer_optimization': "🧪 उर्वरक अनुकूलन कैलकुलेटर",
        'previous_recommendations': "📜 पिछली सिफारिशें",
        'built_with': "सस्टेनेबल फार्मिंग के लिए प्यार से बनाया गया",
        'last_updated': "अंतिम बार अपडेट किया गया: "
    },
    'French': {
        'title': "Système de recommandation agricole durable",
        'farm_details': "📏 Détails de la ferme",
        'crop_preference': "🌱 Préférence de culture",
        'soil_analysis': "🗺️ Analyse du sol",
        'upload_photo': "📸 Télécharger une photo",
        'manual_selection': "📝 Sélection manuelle",
        'select_soil_type': "Sélectionnez le type de sol",
        'generate_recommendation': "💡 Générer une recommandation intelligente",
        'personalized_recommendation': "### 🎯 Votre recommandation personnalisée",
        'weather_forecast': "#### 🌤️ Prévision météo (modèle IA)",
        'pest_prediction': "#### 🐛 Prévision des ravageurs/maladies (modèle IA)",
        'details': "Détails:",
        'crop_rotation_planner': "🌱 Planificateur de rotation des cultures",
        'fertilizer_optimization': "🧪 Calculateur d'optimisation des engrais",
        'previous_recommendations': "📜 Recommandations précédentes",
        'built_with': "Construit avec ❤️ pour une agriculture durable",
        'last_updated': "Dernière mise à jour: "
    },
    'Spanish': {
        'title': "Sistema de Recomendación de Agricultura Sostenible",
        'farm_details': "📏 Detalles de la granja",
        'crop_preference': "🌱 Preferencia de cultivo",
        'soil_analysis': "🗺️ Análisis del suelo",
        'upload_photo': "📸 Subir foto",
        'manual_selection': "📝 Selección manual",
        'select_soil_type': "Seleccione el tipo de suelo",
        'generate_recommendation': "💡 Generar recomendación inteligente",
        'personalized_recommendation': "### 🎯 Su recomendación personalizada",
        'weather_forecast': "#### 🌤️ Pronóstico del tiempo (modelo IA)",
        'pest_prediction': "#### 🐛 Pronóstico de plagas/enfermedades (modelo IA)",
        'details': "Detalles:",
        'crop_rotation_planner': "🌱 Planificador de rotación de cultivos",
        'fertilizer_optimization': "🧪 Calculadora de optimización de fertilizantes",
        'previous_recommendations': "📜 Recomendaciones anteriores",
        'built_with': "Construido con ❤️ para la agricultura sostenible",
        'last_updated': "Última actualización: "
    },
    'Tamil': {
        'title': "திடமான விவசாய பரிந்துரை அமைப்பு",
        'farm_details': "📏 விவசாய விவரங்கள்",
        'crop_preference': "🌱 பயிர் விருப்பம்",
        'soil_analysis': "🗺️ மண் பகுப்பாய்வு",
        'upload_photo': "📸 புகைப்படத்தை பதிவேற்றவும்",
        'manual_selection': "📝 கைமுறையிலான தேர்வு",
        'select_soil_type': "மண் வகையைத் தேர்ந்தெடுக்கவும்",
        'generate_recommendation': "💡 ஸ்மார்ட் பரிந்துரையை உருவாக்கவும்",
        'personalized_recommendation': "### 🎯 உங்கள் தனிப்பட்ட பரிந்துரை",
        'weather_forecast': "#### 🌤️ வானிலை முன்னறிவு (AI மாதிரி)",
        'pest_prediction': "#### 🐛 பூச்சி/நோய் முன்னறிவு (AI மாதிரி)",
        'details': "விவரங்கள்:",
        'crop_rotation_planner': "🌱 பயிர் சுழற்சி திட்டம்",
        'fertilizer_optimization': "🧪 உரம் மேம்பாட்டு கணிப்பான்",
        'previous_recommendations': "📜 முந்தைய பரிந்துரைகள்",
        'built_with': "திடமான விவசாயத்திற்கு அன்புடன் உருவாக்கப்பட்டது",
        'last_updated': "கடைசியாக புதுப்பிக்கப்பட்டது: "
    },
    'Malayalam': {
        'title': "സ്ഥിരമായ കൃഷി ശുപാർശ സംവിധാനം",
        'farm_details': "📏 കൃഷി വിശദാംശങ്ങൾ",
        'crop_preference': "🌱 വിളയുടെ മുൻഗണന",
        'soil_analysis': "🗺️ മണ്ണ് വിശകലനം",
        'upload_photo': "📸 ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക",
        'manual_selection': "📝 മാനുവൽ തിരഞ്ഞെടുപ്പ്",
        'select_soil_type': "മണ്ണിന്റെ തരം തിരഞ്ഞെടുക്കുക",
        'generate_recommendation': "💡 സ്മാർട്ട് ശുപാർശ സൃഷ്ടിക്കുക",
        'personalized_recommendation': "### 🎯 നിങ്ങളുടെ വ്യക്തിഗത ശുപാർശ",
        'weather_forecast': "#### 🌤️ കാലാവസ്ഥ പ്രവചനം (AI മോഡൽ)",
        'pest_prediction': "#### 🐛 കീടം/രോഗം പ്രവചനം (AI മോഡൽ)",
        'details': "വിശദാംശങ്ങൾ:",
        'crop_rotation_planner': "🌱 വിള ചക്ര പദ്ധതി",
        'fertilizer_optimization': "🧪 വളം ഓപ്റ്റിമൈസേഷൻ കാൽക്കുലേറ്റർ",
        'previous_recommendations': "📜 മുമ്പത്തെ ശുപാർശകൾ",
        'built_with': "സ്ഥിരമായ കൃഷിക്ക് സ്നേഹത്തോടെ നിർമ്മിച്ചു",
        'last_updated': "അവസാനമായി പുതുക്കിയത്: "
    },
    'Marathi': {
        'title': "शाश्वत शेती शिफारस प्रणाली",
        'farm_details': "📏 शेती तपशील",
        'crop_preference': "🌱 पिक प्राधान्य",
        'soil_analysis': "🗺️ माती विश्लेषण",
        'upload_photo': "📸 फोटो अपलोड करा",
        'manual_selection': "📝 मॅन्युअल निवड",
        'select_soil_type': "मातीचा प्रकार निवडा",
        'generate_recommendation': "💡 स्मार्ट शिफारस तयार करा",
        'personalized_recommendation': "### 🎯 आपली वैयक्तिक शिफारस",
        'weather_forecast': "#### 🌤️ हवामान अंदाज (AI मॉडेल)",
        'pest_prediction': "#### 🐛 कीटक/रोग अंदाज (AI मॉडेल)",
        'details': "तपशील:",
        'crop_rotation_planner': "🌱 पिक फेरपालट नियोजक",
        'fertilizer_optimization': "🧪 खत ऑप्टिमायझेशन कॅल्क्युलेटर",
        'previous_recommendations': "📜 मागील शिफारसी",
        'built_with': "शाश्वत शेतीसाठी प्रेमाने तयार केले",
        'last_updated': "शेवटचे अद्यतन: "
    },
    'Konkani': {
        'title': "सस्टेनेबल फार्मिंग रेकमेंडेशन सिस्टिम",
        'farm_details': "📏 शेतीचे तपशील",
        'crop_preference': "🌱 पिकाची प्राधान्य",
        'soil_analysis': "🗺️ मातीचे विश्लेषण",
        'upload_photo': "📸 फोटो अपलोड करा",
        'manual_selection': "📝 मॅन्युअल निवड",
        'select_soil_type': "मातीचा प्रकार निवडा",
        'generate_recommendation': "💡 स्मार्ट शिफारस तयार करा",
        'personalized_recommendation': "### 🎯 तुमची वैयक्तिक शिफारस",
        'weather_forecast': "#### 🌤️ हवामानाचा अंदाज (AI मॉडेल)",
        'pest_prediction': "#### 🐛 कीटक/रोगाचा अंदाज (AI मॉडेल)",
        'details': "तपशील:",
        'crop_rotation_planner': "🌱 पिक फेरपालट नियोजक",
        'fertilizer_optimization': "🧪 खत ऑप्टिमायझेशन कॅल्क्युलेटर",
        'previous_recommendations': "📜 मागील शिफारसी",
        'built_with': "सस्टेनेबल फार्मिंगसाठी प्रेमाने तयार केले",
        'last_updated': "शेवटचे अद्यतन: "
    },
    'Urdu': {
        'title': "پائیدار زراعت کی سفارشات کا نظام",
        'farm_details': "📏 زرعی تفصیلات",
        'crop_preference': "🌱 فصل کی ترجیح",
        'soil_analysis': "🗺️ مٹی کا تجزیہ",
        'upload_photo': "📸 تصویر اپ لوڈ کریں",
        'manual_selection': "📝 دستی انتخاب",
        'select_soil_type': "مٹی کی قسم منتخب کریں",
        'generate_recommendation': "💡 اسمارٹ سفارش تیار کریں",
        'personalized_recommendation': "### 🎯 آپ کی ذاتی سفارش",
        'weather_forecast': "#### 🌤️ موسم کی پیش گوئی (AI ماڈل)",
        'pest_prediction': "#### 🐛 کیڑوں/بیماری کی پیش گوئی (AI ماڈل)",
        'details': "تفصیلات:",
        'crop_rotation_planner': "🌱 فصل کی گردش کا منصوبہ",
        'fertilizer_optimization': "🧪 کھاد کی اصلاح کیلکولیٹر",
        'previous_recommendations': "📜 پچھلی سفارشات",
        'built_with': "پائیدار زراعت کے لیے محبت سے تیار کیا گیا",
        'last_updated': "آخری بار اپ ڈیٹ کیا گیا: "
    }
}


# Language selection (after set_page_config)
lang = st.selectbox(
    "Select Language / భాషను ఎంచుకోండి / ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ / भाषा चुनें / Sélectionnez la langue / Seleccione el idioma / மொழியைத் தேர்ந்தெடுக்கவும் / ഭാഷ തിരഞ്ഞെടുക്കുക / भाषा निवडा / Konkani: भाषा निवडा / زبان منتخب کریں",
    options=list(LANGUAGES.keys()),
    index=0,  # Default to English
    key="language_selector"
)
T = LANGUAGES[lang]

# Add the 'agents' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'agents')))

# Import the run_agent_collaboration function from agent_setup
from agents.agent_setup import run_agent_collaboration

# Import WeatherAnalyst and PestDiseasePredictor
from models.weather_Analyst import WeatherAnalyst
from models.pest_disease_predictor import PestDiseasePredictor
from crop_rotation_planner import CropRotationPlanner
from fertilizer_optimizer import FertilizerOptimizer

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
st.markdown(f"""
<div class='recommendation-box' style='background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%); color: white;'>
    <h2 style='color: white; font-size: 2.5em; margin-bottom: 20px;'>🌾 {T['title']}</h2>
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
    st.markdown(f"<div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'><h3 style='color: #2E7D32;'>{T['farm_details']}</h3></div>", unsafe_allow_html=True)
    land_size = st.select_slider("Farm size (hectares)", options=[1, 2, 5, 8, 10, 15, 20], value=8, help="Slide to select your farm size")

with col2:
    st.markdown(f"<div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'><h3 style='color: #2E7D32;'>{T['crop_preference']}</h3></div>", unsafe_allow_html=True)
    crop_preference = st.selectbox("What would you like to grow?", options=["Grains", "Vegetables", "Fruits"], help="Choose your preferred crop type")

# --- Soil Type Input with Both Options ---
st.markdown(f"### {T['soil_analysis']}")
soil_type = None
soil_option = st.radio(f"How would you like to determine your soil type?", [T['upload_photo'], T['manual_selection']], horizontal=True)

if soil_option == T['upload_photo']:
    soil_photo = st.file_uploader(T['upload_photo'], type=["jpg", "jpeg", "png"], key="soil_photo_uploader")
    if soil_photo:
        soil_type = analyze_soil_from_photo(soil_photo)
        if soil_type:
            st.success(f"✅ Detected soil type: {soil_type}")
        else:
            st.warning("⚠️ Could not determine soil type from photo. Please select manually.")
            soil_type = st.selectbox(T['select_soil_type'], options=["Loamy", "Sandy", "Clay"], key="manual_soil_select")
    else:
        soil_type = st.selectbox(T['select_soil_type'], options=["Loamy", "Sandy", "Clay"], key="manual_soil_select_fallback")
elif soil_option == T['manual_selection']:
    soil_type = st.selectbox(T['select_soil_type'], options=["Loamy", "Sandy", "Clay"], key="manual_soil_select")

# Initialize database if it doesn't exist
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db'))
if not os.path.exists(db_path):
    initialize_db()

# --- Recommendation Generation ---
st.markdown("<br>", unsafe_allow_html=True)

if st.button(T['generate_recommendation'], type="primary"):
    with st.spinner("🔄 Analyzing your farm conditions..."):
        try:
            result = run_agent_collaboration(land_size=land_size, soil_type=soil_type, crop_preference=crop_preference)
            crops_data = parse_recommendation(result['recommendation'])

            # --- Weather Forecasting (using WeatherAnalyst) ---
            weather_analyst = WeatherAnalyst()
            soil_ph = 6.5
            soil_moisture = 25
            fertilizer = 50
            pesticide = 5
            weather_forecast = weather_analyst.forecast(soil_ph, soil_moisture, fertilizer, pesticide)
            st.markdown(T['weather_forecast'])
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
            st.markdown(T['pest_prediction'])
            st.info(pest_prediction)

            st.markdown(T['personalized_recommendation'])

            details = result['recommendation'].split("Details:")[1].strip()
            details_html = details.replace('\n', '<br>')
            st.markdown(f"<div class='recommendation-box'><strong>{T['details']}</strong><br>{details_html}</div>", unsafe_allow_html=True)

            if 'Weather Forecast' in result and result['Weather Forecast']:
                st.markdown("#### 🌤️ Weather Forecast (Agent)")
                st.info(result['Weather Forecast'])

            if 'Pest/Disease Prediction' in result and result['Pest/Disease Prediction']:
                st.markdown("#### 🐛 Pest/Disease Prediction (Agent)")
                st.info(result['Pest/Disease Prediction'])

            if 'Warnings' in result and result['Warnings']:
                for warn in result['Warnings']:
                    st.warning(f"Weather Alert: {warn}")

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

st.markdown("<hr>", unsafe_allow_html=True)
st.header(T['crop_rotation_planner'])
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

st.markdown("<hr>", unsafe_allow_html=True)
st.header(T['fertilizer_optimization'])
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

st.markdown(f"<h3 class='score-header'>{T['previous_recommendations']}</h3>", unsafe_allow_html=True)
st.subheader(T['previous_recommendations'], divider="green")
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

# --- Sustainability Score Tracker ---
st.markdown("<hr>", unsafe_allow_html=True)
st.header("🌱 Sustainability Score Tracker")

# Recommended values (example, adjust as needed)
RECOMMENDED_WATER = 2.0  # e.g., 2 ML/ha/season
RECOMMENDED_FERTILIZER = 1.5  # e.g., 1.5 tons/ha/season

# Helper: Calculate sustainability score (realistic)
def calculate_sustainability_score(row):
    score = 100
    water = row.get('water_score', 0)
    if water > RECOMMENDED_WATER:
        score -= min(30, 30 * (water - RECOMMENDED_WATER) / RECOMMENDED_WATER)
    fert = row.get('fertilizer_use', 0)
    if fert > RECOMMENDED_FERTILIZER:
        score -= min(30, 30 * (fert - RECOMMENDED_FERTILIZER) / RECOMMENDED_FERTILIZER)
    if row.get('rotation', False):
        score += 10
    else:
        score -= 10
    return max(0, min(100, score))

# Ensure table exists
with sqlite3.connect(db_path) as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS sustainability_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        water_score REAL,
        fertilizer_use REAL,
        rotation INTEGER,
        score REAL
    )''')
    conn.commit()

# --- User Input for Current Season ---
with st.form("sustainability_form"):
    st.markdown("**Log your current season's practices:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        water_score = st.number_input("Water usage (ML/ha)", min_value=0.0, max_value=10.0, value=RECOMMENDED_WATER, step=0.1)
    with col2:
        fertilizer_use = st.number_input("Fertilizer use (tons/ha)", min_value=0.0, max_value=10.0, value=RECOMMENDED_FERTILIZER, step=0.1)
    with col3:
        rotation = st.checkbox("Practiced crop rotation?", value=True)
    submitted = st.form_submit_button("Log Season")

if submitted:
    score = calculate_sustainability_score({'water_score': water_score, 'fertilizer_use': fertilizer_use, 'rotation': rotation})
    ts = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO sustainability_scores (timestamp, water_score, fertilizer_use, rotation, score) VALUES (?, ?, ?, ?, ?)",
                     (ts, water_score, fertilizer_use, int(rotation), score))
        conn.commit()
    st.success(f"Logged! Your sustainability score for this season: {score:.1f}")

# Fetch all scores
with sqlite3.connect(db_path) as conn:
    df_scores = pd.read_sql("SELECT * FROM sustainability_scores ORDER BY timestamp ASC", conn)

# Plot trend chart
if not df_scores.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_scores['timestamp'], y=df_scores['score'], mode='lines+markers', name='Sustainability Score', line=dict(color='#4caf50', width=3)))
    fig.update_layout(title="Sustainability Score Over Time", xaxis_title="Season", yaxis_title="Score", height=350)
    st.plotly_chart(fig, use_container_width=True)

    if len(df_scores) > 1:
        prev = df_scores['score'].iloc[-2]
        curr = df_scores['score'].iloc[-1]
        pct = ((curr - prev) / prev) * 100 if prev != 0 else 0
        if pct > 0:
            st.success(f"Your sustainability score has improved by {pct:.1f}% since last season!")
        elif pct < 0:
            st.warning(f"Your sustainability score has decreased by {abs(pct):.1f}% since last season.")
        else:
            st.info("Your sustainability score is unchanged since last season.")

    tips = []
    last = df_scores.iloc[-1]
    if last['fertilizer_use'] > RECOMMENDED_FERTILIZER:
        tips.append(f"Reduce fertilizer use to below {RECOMMENDED_FERTILIZER} tons/ha. Try organic options.")
    if last['water_score'] > RECOMMENDED_WATER:
        tips.append(f"Reduce water usage to below {RECOMMENDED_WATER} ML/ha. Consider drip irrigation or mulching.")
    if not last['rotation']:
        tips.append("Practice crop rotation next season to improve soil health and sustainability.")
    if tips:
        st.markdown("**Tips to improve your score:**")
        for tip in tips:
            st.info(tip)
    else:
        st.success("Great job! Your practices are highly sustainable.")
else:
    st.info("No sustainability score data found. Log your first season above!")

# --- Footer ---
current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
st.markdown(f"""
---
<div style='text-align: center; color: #666;'>
    <p>{T['built_with']}</p>
    <p><small>{T['last_updated']} {current_time}</small></p>
</div>
""", unsafe_allow_html=True)