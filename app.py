
import streamlit as st
st.set_page_config(page_title="Sustainable Farming Recommendation System", page_icon="🌾")
import sys
import os
import shutil
from pathlib import Path
import sqlite3
import pandas as pd
from datetime import datetime
from agents.init_db import initialize_db
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import re
import base64
import io
import time
import json
import folium
try:
    from streamlit_folium import st_folium
except Exception:
    # Graceful fallback if streamlit-folium is not available in the environment
    def st_folium(*args, **kwargs):
        st.warning("streamlit-folium is not installed. Maps are disabled. Install it to enable map features.")
        return {}
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reduce model/cache footprint in hosted environments (e.g., Hugging Face)
# Route large caches to ephemeral /tmp and disable telemetry
os.environ.setdefault('TRANSFORMERS_CACHE', '/tmp/transformers')
os.environ.setdefault('HF_HOME', '/tmp/hf')
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')
os.environ.setdefault('HF_HUB_ENABLE_HF_TRANSFER', '0')

def clear_runtime_caches():
    """Delete common ML caches to free disk space at runtime."""
    cache_dirs = [
        Path.home() / '.cache' / 'huggingface',
        Path.home() / '.cache' / 'torch',
        Path('/tmp/transformers'),
        Path('/tmp/hf')
    ]
    cleared = []
    for d in cache_dirs:
        try:
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)
                cleared.append(str(d))
        except Exception:
            pass
    return cleared

# Import speech interface at the top level
try:
    from models.speech_interface import SpeechInterface
except ImportError as e:
    st.error(f"Could not import SpeechInterface: {e}")
    SpeechInterface = None

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
        'last_updated': "Last updated: ",
        'signup_title': "🌾 Join the Farming Community",
        'login_title': "🌾 Welcome Back",
        'username': "👤 Farmer Name",
        'farm_name': "🏡 Farm Name",
        'profile_picture': "📷 Profile Picture (Optional)",
        'signup_button': "✅ Join Now",
        'login_button': "✅ Login",
        'signup_instruction': "Fill in your details to get started!",
        'login_instruction': "Select your farmer profile to continue.",
        'no_account': "No account yet? Sign up!",
        'signup_success': "Welcome, {username}! Your account is created.",
        'login_success': "Welcome back, {username}!",
        'username_exists': "⚠️ Farmer name already taken. Try another.",
        'no_users': "No farmers registered yet. Sign up to start!"
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
        'last_updated': "చివరిగా నవీకరించబడింది: ",
        'signup_title': "🌾 వ్యవసాయ సమాజంలో చేరండి",
        'login_title': "🌾 తిరిగి స్వాగతం",
        'username': "👤 రైతు పేరు",
        'farm_name': "🏡 వ్యవసాయం పేరు",
        'profile_picture': "📷 ప్రొఫైల్ చిత్రం (ఐచ్ఛికం)",
        'signup_button': "✅ ఇప్పుడు చేరండి",
        'login_button': "✅ లాగిన్",
        'signup_instruction': "మీ వివరాలను నమోదు చేయండి!",
        'login_instruction': "మీ రైతు ప్రొఫైల్‌ను ఎంచుకోండి.",
        'no_account': "ఇంకా ఖాతా లేదా? సైన్ అప్ చేయండి!",
        'signup_success': "స్వాగతం, {username}! మీ ఖాతా సృష్టించబడింది.",
        'login_success': "తిరిగి స్వాగతం, {username}!",
        'username_exists': "⚠️ రైతు పేరు ఇప్పటికే తీసుకోబడింది. వేరొకటి ప్రయత్నించండి.",
        'no_users': "ఇంకా రైతులు నమోదు కాలేదు. సైన్ అప్ చేయండి!"
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
        'last_updated': "ಕೊನೆಯದಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ: ",
        'signup_title': "🌾 ಕೃಷಿ ಸಮುದಾಯಕ್ಕೆ ಸೇರಿಕೊಳ್ಳಿ",
        'login_title': "🌾 ಮತ್ತೆ ಸ್ವಾಗತ",
        'username': "👤 ರೈತನ ಹೆಸರು",
        'farm_name': "🏡 ಕೃಷಿ ಹೆಸರು",
        'profile_picture': "📷 ಪ್ರೊಫೈಲ್ ಚಿತ್ರ (ಐಚ್ಛಿಕ)",
        'signup_button': "✅ ಈಗ ಸೇರಿಕೊಳ್ಳಿ",
        'login_button': "✅ ಲಾಗಿನ್",
        'signup_instruction': "ಪ್ರಾರಂಭಿಸಲು ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ!",
        'login_instruction': "ಮುಂದುವರಿಯಲು ನಿಮ್ಮ ರೈತ ಪ್ರೊಫೈಲ್ ಆಯ್ಕೆಮಾಡಿ.",
        'no_account': "ಇನ್ನೂ ಖಾತೆ ಇಲ್ಲವೇ? ಸೈನ್ ಅಪ್ ಮಾಡಿ!",
        'signup_success': "ಸ್ವಾಗತ, {username}! ನಿಮ್ಮ ಖಾತೆ ರಚಿಸಲಾಗಿದೆ.",
        'login_success': "ಮತ್ತೆ ಸ್ವಾಗತ, {username}!",
        'username_exists': "⚠️ ರೈತನ ಹೆಸರು ಈಗಾಗಲೇ ತೆಗೆದುಕೊಳ್ಳಲಾಗಿದೆ. ಬೇರೆಯೊಂದನ್ನು ಪ್ರಯತ್ನಿಸಿ.",
        'no_users': "ಇನ್ನೂ ರೈತರು ನೋಂದಾಯಿಸಿಲ್ಲ. ಪ್ರಾರಂಭಿಸಲು ಸೈನ್ ಅಪ್ ಮಾಡಿ!"
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
        'last_updated': "अंतिम बार अपडेट किया गया: ",
        'signup_title': "🌾 कृषक समुदाय में शामिल हों",
        'login_title': "🌾 वापस स्वागत है",
        'username': "👤 किसान का नाम",
        'farm_name': "🏡 खेत का नाम",
        'profile_picture': "📷 प्रोफाइल चित्र (वैकल्पिक)",
        'signup_button': "✅ अब शामिल हों",
        'login_button': "✅ लॉगिन",
        'signup_instruction': "शुरू करने के लिए अपनी जानकारी भरें!",
        'login_instruction': "जारी रखने के लिए अपनी किसान प्रोफाइल चुनें।",
        'no_account': "अभी तक कोई खाता नहीं है? साइन अप करें!",
        'signup_success': "स्वागत है, {username}! आपका खाता बन गया है।",
        'login_success': "वापस स्वागत है, {username}!",
        'username_exists': "⚠️ किसान का नाम पहले से लिया गया है। दूसरा नाम आज़माएं।",
        'no_users': "अभी तक कोई किसान पंजीकृत नहीं है। शुरू करने के लिए साइन अप करें!"
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
        'last_updated': "Dernière mise à jour: ",
        'signup_title': "🌾 Rejoignez la communauté agricole",
        'login_title': "🌾 Bienvenue à nouveau",
        'username': "👤 Nom de l'agriculteur",
        'farm_name': "🏡 Nom de la ferme",
        'profile_picture': "📷 Photo de profil (facultatif)",
        'signup_button': "✅ S'inscrire maintenant",
        'login_button': "✅ Connexion",
        'signup_instruction': "Remplissez vos informations pour commencer !",
        'login_instruction': "Sélectionnez votre profil d'agriculteur pour continuer.",
        'no_account': "Pas encore de compte ? Inscrivez-vous !",
        'signup_success': "Bienvenue, {username} ! Votre compte a été créé.",
        'login_success': "Bon retour, {username} !",
        'username_exists': "⚠️ Nom d'agriculteur déjà pris. Essayez un autre.",
        'no_users': "Aucun agriculteur enregistré pour le moment. Inscrivez-vous pour commencer !"
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
        'last_updated': "Última actualización: ",
        'signup_title': "🌾 Únete a la comunidad agrícola",
        'login_title': "🌾 Bienvenido de nuevo",
        'username': "👤 Nombre del agricultor",
        'farm_name': "🏡 Nombre de la granja",
        'profile_picture': "📷 Foto de perfil (opcional)",
        'signup_button': "✅ Únete ahora",
        'login_button': "✅ Iniciar sesión",
        'signup_instruction': "¡Completa tus datos para empezar!",
        'login_instruction': "Selecciona tu perfil de agricultor para continuar.",
        'no_account': "¿Aún no tienes cuenta? ¡Regístrate!",
        'signup_success': "¡Bienvenido, {username}! Tu cuenta ha sido creada.",
        'login_success': "¡Bienvenido de nuevo, {username}!",
        'username_exists': "⚠️ Nombre de agricultor ya tomado. Prueba con otro.",
        'no_users': "Aún no hay agricultores registrados. ¡Regístrate para comenzar!"
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
        'last_updated': "கடைசியாக புதுப்பிக்கப்பட்டது: ",
        'signup_title': "🌾 விவசாய சமூகத்தில் சேரவும்",
        'login_title': "🌾 மீண்டும் வரவேற்கிறோம்",
        'username': "👤 விவசாயி பெயர்",
        'farm_name': "🏡 பண்ணை பெயர்",
        'profile_picture': "📷 சுயவிவர படம் (விருப்பமானது)",
        'signup_button': "✅ இப்போது சேரவும்",
        'login_button': "✅ உள்நுழை",
        'signup_instruction': "தொடங்க உங்கள் விவரங்களை நிரப்பவும்!",
        'login_instruction': "தொடர உங்கள் விவசாயி சுயவிவரத்தைத் தேர்ந்தெடுக்கவும்.",
        'no_account': "இன்னும் கணக்கு இல்லையா? பதிவு செய்யவும்!",
        'signup_success': "வரவேற்கிறோம், {username}! உங்கள் கணக்கு உருவாக்கப்பட்டது.",
        'login_success': "மீண்டும் வரவேற்கிறோம், {username}!",
        'username_exists': "⚠️ விவசாயி பெயர் ஏற்கனவே எடுக்கப்பட்டுள்ளது. வேறு ஒரு பெயரை முயற்சிக்கவும்.",
        'no_users': "இன்னும் விவசாயிகள் பதிவு செய்யப்படவில்லை. தொடங்க பதிவு செய்யவும்!"
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
        'last_updated': "അവസാനമായി പുതുക്കിയത്: ",
        'signup_title': "🌾 കൃഷി സമൂഹത്തിൽ ചേരുക",
        'login_title': "🌾 വീണ്ടും സ്വാഗതം",
        'username': "👤 കർഷകന്റെ പേര്",
        'farm_name': "🏡 കൃഷിസ്ഥലത്തിന്റെ പേര്",
        'profile_picture': "📷 പ്രൊഫൈൽ ചിത്രം (ഓപ്ഷണൽ)",
        'signup_button': "✅ ഇപ്പോൾ ചേരുക",
        'login_button': "✅ ലോഗിൻ",
        'signup_instruction': "തുടങ്ങാൻ നിന്റെ വിശദാംശങ്ങൾ നൽകുക!",
        'login_instruction': "തുടരാൻ നിന്റെ കർഷക പ്രൊഫൈൽ തിരഞ്ഞെടുക്കുക.",
        'no_account': "ഇതുവരെ അക്കൗണ്ട് ഇല്ലേ? സൈൻ അപ്പ് ചെയ്യുക!",
        'signup_success': "സ്വാഗതം, {username}! നിന്റെ അക്കൗണ്ട് സൃഷ്ടിച്ചു.",
        'login_success': "വീണ്ടും സ്വാഗതം, {username}!",
        'username_exists': "⚠️ കർഷകന്റെ പേര് ഇതിനകം എടുത്തിട്ടുണ്ട്. മറ്റൊരു പേര് പരീക്ഷിക്കുക.",
        'no_users': "ഇതുവരെ കർഷകർ രജിസ്റ്റർ ചെയ്തിട്ടില്ല. തുടങ്ങാൻ സൈൻ അപ്പ് ചെയ്യുക!"
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
        'last_updated': "शेवटचे अद्यतन: ",
        'signup_title': "🌾 शेती समुदायात सामील व्हा",
        'login_title': "🌾 परत स्वागत आहे",
        'username': "👤 शेतकऱ्याचे नाव",
        'farm_name': "🏡 शेताचे नाव",
        'profile_picture': "📷 प्रोफाइल चित्र (पर्यायी)",
        'signup_button': "✅ आता सामील व्हा",
        'login_button': "✅ लॉगिन",
        'signup_instruction': "सुरू करण्यासाठी आपले तपशील भरा!",
        'login_instruction': "पुढे जाण्यासाठी आपले शेतकरी प्रोफाइल निवडा.",
        'no_account': "अजून खाते नाही? साइन अप करा!",
        'signup_success': "स्वागत आहे, {username}! आपले खाते तयार झाले आहे.",
        'login_success': "परत स्वागत आहे, {username}!",
        'username_exists': "⚠️ शेतकऱ्याचे नाव आधीच घेतले आहे. दुसरे नाव वापरून पहा.",
        'no_users': "अजून कोणतेही शेतकरी नोंदणीकृत नाहीत. सुरू करण्यासाठी साइन अप करा!"
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
        'last_updated': "शेवटचे अद्यतन: ",
        'signup_title': "🌾 शेती समुदायात सामील व्हा",
        'login_title': "🌾 परत स्वागत आहे",
        'username': "👤 शेतकऱ्याचे नाव",
        'farm_name': "🏡 शेताचे नाव",
        'profile_picture': "📷 प्रोफाइल चित्र (पर्यायी)",
        'signup_button': "✅ आता सामील व्हा",
        'login_button': "✅ लॉगिन",
        'signup_instruction': "सुरू करण्यासाठी आपले तपशील भरा!",
        'login_instruction': "पुढे जाण्यासाठी आपले शेतकरी प्रोफाइल निवडा.",
        'no_account': "अजून खाते नाही? साइन अप करा!",
        'signup_success': "स्वागत आहे, {username}! आपले खाते तयार झाले आहे.",
        'login_success': "परत स्वागत आहे, {username}!",
        'username_exists': "⚠️ शेतकऱ्याचे नाव आधीच घेतले आहे. दुसरे नाव वापरून पहा.",
        'no_users': "अजून कोणतेही शेतकरी नोंदणीकृत नाहीत. सुरू करण्यासाठी साइन अप करा!"
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
        'last_updated': "آخری بار اپ ڈیٹ کیا گیا: ",
        'signup_title': "🌾 زرعی برادری میں شامل ہوں",
        'login_title': "🌾 واپس خوش آمدید",
        'username': "👤 کسان کا نام",
        'farm_name': "🏡 کھیت کا نام",
        'profile_picture': "📷 پروفائل تصویر (اختیاری)",
        'signup_button': "✅ ابھی شامل ہوں",
        'login_button': "✅ لاگ ان",
        'signup_instruction': "شروع کرنے کے لیے اپنی تفصیلات پُر کریں!",
        'login_instruction': "جاری رکھنے کے لیے اپنا کسان پروفائل منتخب کریں۔",
        'no_account': "ابھی تک کوئی اکاؤنٹ نہیں ہے؟ سائن اپ کریں!",
        'signup_success': "خوش آمدید، {username}! آپ کا اکاؤنٹ بن گیا ہے۔",
        'login_success': "واپس خوش آمدید، {username}!",
        'username_exists': "⚠️ کسان کا نام پہلے سے لیا جا چکا ہے۔ کوئی اور نام آزمائیں۔",
        'no_users': "ابھی تک کوئی کسان رجسٹرڈ نہیں ہیں۔ شروع کرنے کے لیے سائن اپ کریں!"
    }
}

# Set page config FIRST, before any other Streamlit command
## st.set_page_config moved to top of file

# Update initialize_db to include users table and new features
def initialize_db():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Create recommendations table with extended schema used by agents
        cursor.execute('''CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT,
            score REAL,
            rationale TEXT,
            market_score REAL,
            weather_score REAL,
            sustainability_score REAL,
            carbon_score REAL,
            water_score REAL,
            erosion_score REAL,
            timestamp TEXT
        )''')
        # Ensure legacy databases are migrated to include new columns
        try:
            cursor.execute("PRAGMA table_info(recommendations)")
            existing_cols = {row[1] for row in cursor.fetchall()}
            missing_cols = []
            if 'market_score' not in existing_cols:
                missing_cols.append(("market_score", "REAL"))
            if 'weather_score' not in existing_cols:
                missing_cols.append(("weather_score", "REAL"))
            if 'sustainability_score' not in existing_cols:
                missing_cols.append(("sustainability_score", "REAL"))
            for col_name, col_type in missing_cols:
                cursor.execute(f"ALTER TABLE recommendations ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass
        # Create farmer_advisor table required by multiple models
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
        # Seed minimal sample data if empty to avoid cold-start errors
        cursor.execute('SELECT COUNT(*) FROM farmer_advisor')
        fa_count = cursor.fetchone()[0]
        if fa_count == 0:
            sample_farmer_rows = [
                (6.5, 30.0, 28.0, 120.0, 80.0, 10.0, 3.5, 'Wheat', 78.0),
                (6.2, 35.0, 30.0, 90.0, 70.0, 8.0, 3.2, 'Rice', 75.0),
                (6.8, 25.0, 32.0, 60.0, 60.0, 6.0, 2.8, 'Corn', 80.0),
                (6.4, 33.0, 27.0, 100.0, 85.0, 9.0, 3.0, 'Soybean', 76.0)
            ]
            cursor.executemany('''
                INSERT INTO farmer_advisor (
                    Soil_pH, Soil_Moisture, Temperature_C, Rainfall_mm,
                    Fertilizer_Usage_kg, Pesticide_Usage_kg, Crop_Yield_ton,
                    Crop_Type, Sustainability_Score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_farmer_rows)
        # Ensure market_researcher table exists (needed by MarketResearcher on import)
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
        # Seed minimal sample data if empty to avoid cold-start errors
        cursor.execute('SELECT COUNT(*) FROM market_researcher')
        count = cursor.fetchone()[0]
        if count == 0:
            sample_data = [
                ("tomatoes", 950.0, 0.6, 0.4, 900.0, 0.8, 0.7, "High", 0.6),
                ("carrots", 800.0, 0.5, 0.5, 850.0, 0.7, 0.6, "Medium", 0.5),
                ("wheat", 600.0, 0.4, 0.6, 650.0, 0.9, 0.8, "Low", 0.7),
                ("corn", 700.0, 0.5, 0.5, 720.0, 0.8, 0.7, "Medium", 0.6)
            ]
            cursor.executemany('''
                INSERT INTO market_researcher (Product, Market_Price_per_ton, Demand_Index, Supply_Index,
                                               Competitor_Price_per_ton, Economic_Indicator,
                                               Weather_Impact_Score, Seasonal_Factor, Consumer_Trend_Index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_data)
        # Create sustainability_scores table (existing)
        cursor.execute('''CREATE TABLE IF NOT EXISTS sustainability_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            water_score REAL,
            fertilizer_use REAL,
            rotation INTEGER,
            score REAL
        )''')
        # Create users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            farm_name TEXT,
            profile_picture TEXT,
            created_at TEXT
        )''')
        # Create farm_maps table for interactive farm mapping
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
        # Create community_insights table for community-driven data
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
        # Create market_forecasts table for price predictions
        cursor.execute('''CREATE TABLE IF NOT EXISTS market_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT,
            predicted_price REAL,
            confidence_score REAL,
            forecast_date TEXT,
            created_at TEXT
        )''')
        # Create chatbot_sessions table for chat history
        cursor.execute('''CREATE TABLE IF NOT EXISTS chatbot_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            session_id TEXT,
            query TEXT,
            response TEXT,
            timestamp TEXT
        )''')
        # Create offline_data table for offline mode
        cursor.execute('''CREATE TABLE IF NOT EXISTS offline_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            data_type TEXT,
            data_content TEXT,
            sync_status TEXT,
            created_at TEXT,
            synced_at TEXT
        )''')
        conn.commit()

# Initialize database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db'))

# Ensure database directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Initialize database with all tables
initialize_db()

# Helper: Convert image to base64 for storage
def image_to_base64(image_file):
    if image_file:
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    return None

# Helper: Display base64 image
def display_base64_image(base64_string, size=50):
    if base64_string:
        return f'<img src="data:image/png;base64,{base64_string}" width="{size}" style="border-radius:50%;margin-right:10px;">'
    return '<span style="font-size:2em;margin-right:10px;">👤</span>'

# Helper: Generate chatbot response
def generate_chatbot_response(query):
    """Generate AI response for farming queries"""
    query_lower = query.lower()
    
    # Simple rule-based responses (in production, this would use the agent framework)
    if any(word in query_lower for word in ['fertilizer', 'fertilizer', 'nutrient']):
        if 'loamy' in query_lower:
            return "For loamy soil, I recommend balanced NPK fertilizer (10-10-10) at 100-150 kg/hectare. Loamy soil has good drainage and nutrient retention, so moderate fertilization works well. Consider organic options like compost or manure for sustainable farming."
        elif 'clay' in query_lower:
            return "Clay soil requires careful fertilizer management. Use slow-release fertilizers and avoid over-application. I recommend 80-120 kg/hectare of NPK fertilizer. Clay soil holds nutrients well, so less frequent but consistent application is key."
        elif 'sandy' in query_lower:
            return "Sandy soil needs more frequent fertilization due to poor nutrient retention. Use 120-180 kg/hectare of NPK fertilizer in smaller, more frequent applications. Consider adding organic matter to improve soil structure."
        else:
            return "For fertilizer recommendations, I need to know your soil type. Generally, balanced NPK fertilizers work well for most crops. Consider soil testing for precise recommendations."
    
    elif any(word in query_lower for word in ['pest', 'disease', 'insect']):
        return "For pest and disease management, I recommend integrated pest management (IPM) approach: 1) Monitor regularly, 2) Use biological controls, 3) Apply chemical treatments only when necessary, 4) Practice crop rotation. What specific pest or disease are you dealing with?"
    
    elif any(word in query_lower for word in ['water', 'irrigation', 'watering']):
        return "Water management is crucial for crop health. I recommend: 1) Monitor soil moisture regularly, 2) Use drip irrigation for water efficiency, 3) Water early morning or evening, 4) Adjust based on weather conditions. What's your current irrigation setup?"
    
    elif any(word in query_lower for word in ['crop', 'plant', 'growing']):
        return "For crop selection, consider: 1) Soil type and climate, 2) Market demand and prices, 3) Your farming experience, 4) Water availability. What crops are you interested in growing?"
    
    elif any(word in query_lower for word in ['soil', 'soil type', 'soil test']):
        return "Soil health is fundamental to farming success. I recommend: 1) Get soil tested regularly, 2) Maintain proper pH levels (6.0-7.0 for most crops), 3) Add organic matter, 4) Practice crop rotation. Would you like help with soil testing or improvement?"
    
    elif any(word in query_lower for word in ['weather', 'climate', 'season']):
        return "Weather and climate play a crucial role in farming. I can help with: 1) Weather-based planting decisions, 2) Climate-appropriate crop selection, 3) Seasonal farming practices, 4) Weather risk management. What specific weather concern do you have?"
    
    elif any(word in query_lower for word in ['yield', 'production', 'harvest']):
        return "To improve crop yield, focus on: 1) Quality seeds and planting material, 2) Proper spacing and timing, 3) Adequate nutrition and water, 4) Pest and disease control, 5) Post-harvest management. What crop are you looking to improve yield for?"
    
    else:
        return "I'm here to help with all your farming questions! I can assist with soil management, crop selection, pest control, irrigation, weather planning, and much more. Could you be more specific about what you'd like to know?"

# --- Authentication ---
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'English'

# Language selection
lang = st.selectbox(
    "🌐 " + LANGUAGES[st.session_state['lang']].get('select_language', 'Select Language'),
    options=list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(st.session_state['lang']),
    key="language_selector"
)
st.session_state['lang'] = lang
T = LANGUAGES[lang]

# Check if user is logged in
if not st.session_state['user']:
    # Tabs for Signup and Login
    tab1, tab2 = st.tabs([T['signup_title'], T['login_title']])

    with tab1:
        st.markdown(f"<div class='card-section'><span class='section-step'>👋</span><b style='font-size:1.3em'>{T['signup_title']}</b><div class='section-instructions'>{T['signup_instruction']}</div></div>", unsafe_allow_html=True)
        with st.form("signup_form"):
            col1, col2 = st.columns([1, 1])
            with col1:
                username = st.text_input(f"👤 {T['username']}", help=T['username'])
            with col2:
                farm_name = st.text_input(f"🏡 {T['farm_name']}", help=T['farm_name'])
            profile_picture = st.file_uploader(f"📷 {T['profile_picture']}", type=["jpg", "jpeg", "png"])
            submit_signup = st.form_submit_button(f"✅ {T['signup_button']}", type="primary")

            if submit_signup:
                if username and farm_name:
                    with sqlite3.connect(db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
                        if cursor.fetchone():
                            st.error(T['username_exists'])
                        else:
                            profile_picture_base64 = image_to_base64(profile_picture)
                            cursor.execute(
                                "INSERT INTO users (username, farm_name, profile_picture, created_at) VALUES (?, ?, ?, ?)",
                                (username, farm_name, profile_picture_base64, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            )
                            conn.commit()
                            st.session_state['user'] = {'username': username, 'farm_name': farm_name, 'profile_picture': profile_picture_base64}
                            st.success(T['signup_success'].format(username=username))
                            st.rerun()
                else:
                    st.error(T.get('fill_all_fields', "Please fill in all required fields."))

    with tab2:
        st.markdown(f"<div class='card-section'><span class='section-step'>👋</span><b style='font-size:1.3em'>{T['login_title']}</b><div class='section-instructions'>{T['login_instruction']}</div></div>", unsafe_allow_html=True)
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, farm_name, profile_picture FROM users")
            users = cursor.fetchall()
        
        if users:
            user_options = [
                (f"{display_base64_image(user[2])} {user[0]} ({user[1]})", user) for user in users
            ]
            selected_user = st.selectbox(
                f"👤 {T.get('select_farmer', 'Select your farmer profile')}",
                options=[u[0] for u in user_options],
                format_func=lambda x: x,
                help=T['login_instruction']
            )
            if st.button(f"✅ {T['login_button']}", type="primary"):
                selected_user_data = next(u[1] for u in user_options if u[0] == selected_user)
                st.session_state['user'] = {
                    'username': selected_user_data[0],
                    'farm_name': selected_user_data[1],
                    'profile_picture': selected_user_data[2]
                }
                st.success(T['login_success'].format(username=selected_user_data[0]))
                st.rerun()
        else:
            st.info(T['no_users'])
            st.markdown(f"<a href='#' onclick='st.set_page_config(page_title=\"{T['signup_title']}\");'>{T['no_account']}</a>", unsafe_allow_html=True)
else:
    # Display logged-in user
    user = st.session_state['user']
    st.markdown(
        f"<div style='display:flex;align-items:center;'>{display_base64_image(user['profile_picture'])} <b>{T.get('welcome', 'Welcome')}, {user['username']} ({user['farm_name']})!</b></div>",
        unsafe_allow_html=True
    )
    if st.button(f"🔓 {T.get('logout', 'Logout')}"):
        st.session_state['user'] = None
        st.rerun()
    
    # Check which page to display
    current_page = st.session_state.get('current_page', '🏠 Main App')
    
    if current_page == '👤 User Profile':
        # User Profile Page
        st.title("👤 User Profile")
        
        # Profile tabs
        tab_profile, tab_history, tab_settings = st.tabs(["📋 Profile Info", "📊 Farming History", "⚙️ Settings"])
        
        with tab_profile:
            st.markdown("### 👤 Personal Information")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Profile picture
                st.markdown("#### Profile Picture")
                current_pic = display_base64_image(user['profile_picture'], size=150)
                st.markdown(current_pic, unsafe_allow_html=True)
                
                # Upload new picture
                new_picture = st.file_uploader("Upload new profile picture", type=['png', 'jpg', 'jpeg'], key="profile_pic_upload")
                if new_picture:
                    new_pic_base64 = image_to_base64(new_picture)
                    st.session_state['user']['profile_picture'] = new_pic_base64
                    st.success("✅ Profile picture updated!")
                    st.rerun()
            
            with col2:
                # User information
                st.markdown("#### User Details")
                
                # Editable fields
                new_username = st.text_input("Username", value=user['username'], key="edit_username")
                new_farm_name = st.text_input("Farm Name", value=user['farm_name'], key="edit_farm_name")
                
                # Additional profile fields
                st.markdown("#### Additional Information")
                email = st.text_input("Email (Optional)", value=st.session_state.get('user_email', ''), key="edit_email")
                phone = st.text_input("Phone (Optional)", value=st.session_state.get('user_phone', ''), key="edit_phone")
                location = st.text_input("Location (Optional)", value=st.session_state.get('user_location', ''), key="edit_location")
                
                # Farming preferences
                st.markdown("#### Farming Preferences")
                experience_level = st.selectbox("Experience Level", 
                    ["Beginner", "Intermediate", "Advanced", "Expert"], 
                    index=["Beginner", "Intermediate", "Advanced", "Expert"].index(st.session_state.get('experience_level', 'Beginner')),
                    key="edit_experience")
                
                farm_size = st.number_input("Farm Size (hectares)", 
                    min_value=0.1, max_value=1000.0, 
                    value=float(st.session_state.get('farm_size', 5.0)), 
                    step=0.1, key="edit_farm_size")
                
                primary_crops = st.multiselect("Primary Crops", 
                    ["Rice", "Wheat", "Corn", "Soybean", "Vegetables", "Fruits", "Spices", "Other"],
                    default=st.session_state.get('primary_crops', []),
                    key="edit_primary_crops")
                
                # Save button
                if st.button("💾 Save Profile Changes", key="save_profile"):
                    # Update user data
                    st.session_state['user']['username'] = new_username
                    st.session_state['user']['farm_name'] = new_farm_name
                    st.session_state['user_email'] = email
                    st.session_state['user_phone'] = phone
                    st.session_state['user_location'] = location
                    st.session_state['experience_level'] = experience_level
                    st.session_state['farm_size'] = farm_size
                    st.session_state['primary_crops'] = primary_crops
                    
                    # Update database
                    try:
                        conn = sqlite3.connect('database/sustainable_farming.db')
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE users 
                            SET username = ?, farm_name = ?, profile_picture = ?
                            WHERE username = ?
                        """, (new_username, new_farm_name, st.session_state['user']['profile_picture'], user['username']))
                        conn.commit()
                        conn.close()
                        st.success("✅ Profile updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating profile: {e}")
        
        with tab_history:
            st.markdown("### 📊 Farming History & Analytics")
            
            # Recent recommendations
            st.markdown("#### Recent Recommendations")
            try:
                conn = sqlite3.connect('database/sustainable_farming.db')
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT recommendation, created_at, sustainability_score 
                    FROM recommendations 
                    WHERE username = ? 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """, (user['username'],))
                recommendations = cursor.fetchall()
                
                if recommendations:
                    for i, (rec, date, score) in enumerate(recommendations):
                        with st.expander(f"Recommendation {i+1} - {date[:10]} (Score: {score}/100)"):
                            st.text(rec[:500] + "..." if len(rec) > 500 else rec)
                else:
                    st.info("No recommendations found. Generate some recommendations to see your history!")
                
                conn.close()
            except Exception as e:
                st.warning(f"Could not load recommendations: {e}")
            
            # Sustainability tracking
            st.markdown("#### Sustainability Score History")
            try:
                conn = sqlite3.connect('database/sustainable_farming.db')
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT sustainability_score, created_at 
                    FROM sustainability_tracking 
                    WHERE username = ? 
                    ORDER BY created_at DESC 
                    LIMIT 20
                """, (user['username'],))
                scores = cursor.fetchall()
                
                if scores:
                    import pandas as pd
                    df = pd.DataFrame(scores, columns=['Score', 'Date'])
                    df['Date'] = pd.to_datetime(df['Date'])
                    
                    # Create a simple line chart
                    import plotly.express as px
                    fig = px.line(df, x='Date', y='Score', title='Sustainability Score Over Time')
                    fig.update_layout(yaxis_title="Sustainability Score", xaxis_title="Date")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No sustainability data found. Start tracking your farming practices!")
                
                conn.close()
            except Exception as e:
                st.warning(f"Could not load sustainability data: {e}")
        
        with tab_settings:
            st.markdown("### ⚙️ Account Settings")
            
            # Language settings
            st.markdown("#### Language & Voice Settings")
            current_lang = st.session_state.get('language', 'English')
            new_language = st.selectbox("Preferred Language", 
                ["English", "Hindi", "Kannada", "Telugu", "Tamil", "Malayalam", "Bengali", "Gujarati", "Marathi", "Punjabi", "Odia", "Assamese", "French", "Spanish"],
                index=["English", "Hindi", "Kannada", "Telugu", "Tamil", "Malayalam", "Bengali", "Gujarati", "Marathi", "Punjabi", "Odia", "Assamese", "French", "Spanish"].index(current_lang),
                key="settings_language")
            
            # Voice settings
            voice_enabled = st.checkbox("Enable Voice Interface", 
                value=st.session_state.get('voice_enabled', True),
                key="settings_voice")
            
            # Notification settings
            st.markdown("#### Notification Settings")
            email_notifications = st.checkbox("Email Notifications", 
                value=st.session_state.get('email_notifications', False),
                key="settings_email")
            
            weather_alerts = st.checkbox("Weather Alerts", 
                value=st.session_state.get('weather_alerts', True),
                key="settings_weather")
            
            # Data export
            st.markdown("#### Data Management")
            if st.button("📥 Export My Data", key="export_data"):
                try:
                    # Export user data
                    export_data = {
                        'username': user['username'],
                        'farm_name': user['farm_name'],
                        'email': st.session_state.get('user_email', ''),
                        'phone': st.session_state.get('user_phone', ''),
                        'location': st.session_state.get('user_location', ''),
                        'experience_level': st.session_state.get('experience_level', 'Beginner'),
                        'farm_size': st.session_state.get('farm_size', 5.0),
                        'primary_crops': st.session_state.get('primary_crops', []),
                        'language': st.session_state.get('language', 'English'),
                        'voice_enabled': st.session_state.get('voice_enabled', True)
                    }
                    
                    import json
                    st.download_button(
                        label="⬇️ Download Profile Data",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"{user['username']}_profile_data.json",
                        mime="application/json"
                    )
                    st.success("✅ Data export ready!")
                except Exception as e:
                    st.error(f"❌ Error exporting data: {e}")
            
            # Save settings
            if st.button("💾 Save Settings", key="save_settings"):
                st.session_state['language'] = new_language
                st.session_state['voice_enabled'] = voice_enabled
                st.session_state['email_notifications'] = email_notifications
                st.session_state['weather_alerts'] = weather_alerts
                st.success("✅ Settings saved successfully!")
    
    else:
        # Main App Page (existing content)
        
        # Sidebar quick panel
        with st.sidebar:
            st.markdown("### 🌾 Quick Panel")
            st.markdown(f"{display_base64_image(user['profile_picture'], size=36)} <b>{user['username']}</b><br><small>{user['farm_name']}</small>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<b style='font-size:1.1em;color:#00bfff;'>Choose a feature:</b>", unsafe_allow_html=True)
            quick_features = [
                ("🏡 Farm Details", "#farm-details", "#00c3ff"),
                ("🗺️ Soil Analysis", "#soil-analysis", "#f7971e"),
                ("💡 Smart Recommendation", "#smart-recommendation", "#00ff85"),
                ("🌱 Crop Rotation Planner", "#crop-rotation-planner", "#43cea2"),
                ("🧪 Fertilizer Optimization Calculator", "#fertilizer-optimization", "#f857a6"),
                ("📜 Previous Recommendations", "#previous-recommendations", "#ff5858"),
                ("🌍 Sustainability Score Tracker", "#sustainability-score-tracker", "#2af598"),
                ("🗺️ Interactive Farm Map", "#interactive-farm-map", "#ff6b6b"),
                ("👥 Community Insights", "#community-insights", "#4ecdc4"),
                ("📈 Market Dashboard", "#market-dashboard", "#45b7d1"),
                ("🤖 AI Chatbot", "#ai-chatbot", "#ff9f1c"),
                ("📱 Offline Mode", "#offline-mode", "#9b59b6")
            ]
            for label, anchor, color in quick_features:
                # Extract the section name from the anchor
                section_name = anchor.replace('#', '')
                st.markdown(f"""
                    <div class='nav-button' style='margin:8px 0;padding:12px 0;border-radius:14px;background:linear-gradient(90deg,{color} 0%,#fff 100%);text-align:center;box-shadow:0 2px 12px rgba(0,191,255,0.12);' 
                         onclick="document.getElementById('{section_name}').scrollIntoView({{behavior: 'smooth'}});">
                        <span style='text-decoration:none;font-size:1.15em;font-weight:600;color:#1e3c72;cursor:pointer;'>{label}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.session_state.setdefault('last_recs_csv', None)
            if st.session_state['last_recs_csv']:
                st.download_button("⬇ Download recent recommendations", data=st.session_state['last_recs_csv'], file_name="recent_recommendations.csv", mime="text/csv")
            
            # Navigation
            st.markdown("### 🧭 Navigation")
            page = st.radio("Choose a page:", ["🏠 Main App", "👤 User Profile"], key="page_selector")
            st.session_state['current_page'] = page
            st.divider()
            
            # API Configuration
            st.markdown("### ⚙️ Configuration")
            openweather_key = st.text_input(
                "OpenWeatherMap API Key", 
                value=os.getenv('OPENWEATHER_API_KEY', 'e6f39f1d5c2c4ecea6d180422252609'),
                type="password",
                help="Get your free API key from openweathermap.org"
            )
            if openweather_key:
                os.environ['OPENWEATHER_API_KEY'] = openweather_key
                st.success("✅ API key configured")
            else:
                st.warning("⚠️ Using simulated weather data")

            # Runtime cache management
            st.markdown("### 🧹 Runtime Storage")
            if st.button("Free up disk space (clear ML caches)"):
                cleared = clear_runtime_caches()
                if cleared:
                    st.success("Cleared caches: " + ", ".join(cleared))
                else:
                    st.info("No caches found or already clean.")
            
            # Speech Feature Integration
            st.markdown("### 🎤 Voice Controls")
            if 'speech_interface' not in st.session_state:
                if SpeechInterface is not None:
                    st.session_state['speech_interface'] = SpeechInterface()
                else:
                    st.session_state['speech_interface'] = None
            speech_interface = st.session_state['speech_interface']
            voice_enabled = st.checkbox("Enable Voice Interface", value=True, help="Allow voice input and output")
            st.session_state['voice_enabled'] = voice_enabled
            if voice_enabled:
                if speech_interface is not None:
                    mic_ok = getattr(speech_interface, 'is_voice_available', lambda: False)()
                    tts_ok = getattr(speech_interface, 'has_tts', lambda: False)()
                    if mic_ok:
                        st.success("✅ Microphone available")
                    else:
                        # Clarify that WebRTC may enable mic even without PyAudio
                        st.warning("⚠️ Microphone not available (native). If using a browser, WebRTC capture will be used where supported.")
                    if tts_ok:
                        st.success("✅ Text-to-Speech available")
                        if st.button("🔊 Voice Help", help="Listen to voice instructions"):
                            speech_interface.create_voice_help_system(lang)
                    else:
                        st.warning("⚠️ Text-to-Speech not available")
                else:
                    st.warning("⚠️ Speech interface not available. Please install speech dependencies.")
                    with st.expander("📋 Installation Instructions"):
                        st.markdown("""
                        **To enable voice features, install PyAudio:**
                        **Option 1 (Recommended):**
                        ```bash
                        pip install pipwin
                        pipwin install pyaudio
                        ```
                        **Option 2:**
                        ```bash
                        conda install pyaudio
                        ```
                        **Option 3:**
                        ```bash
                        pip install pyaudio
                        ```
                        **Note:** The app works perfectly without voice features - all farming functionality is available!
                        """)
        
        # Location Configuration
        st.markdown("### 📍 Location Settings")
        location_option = st.radio(
            "Choose location method:",
            ["Use my coordinates", "Enter city name", "Use default (Bangalore)"],
            index=2
        )
        
        user_lat = 12.9716  # Default Bangalore
        user_lon = 77.5946
        
        if location_option == "Use my coordinates":
            col1, col2 = st.columns(2)
            with col1:
                user_lat = st.number_input("Latitude", value=12.9716, min_value=-90.0, max_value=90.0, step=0.0001)
            with col2:
                user_lon = st.number_input("Longitude", value=77.5946, min_value=-180.0, max_value=180.0, step=0.0001)
        elif location_option == "Enter city name":
            city_name = st.text_input("City Name", value="Bangalore, India")
            if city_name:
                # Simple geocoding - you could enhance this with a proper geocoding service
                city_coords = {
                    "bangalore, india": (12.9716, 77.5946),
                    "mumbai, india": (19.0760, 72.8777),
                    "delhi, india": (28.7041, 77.1025),
                    "chennai, india": (13.0827, 80.2707),
                    "kolkata, india": (22.5726, 88.3639),
                    "hyderabad, india": (17.3850, 78.4867),
                    "pune, india": (18.5204, 73.8567),
                    "ahmedabad, india": (23.0225, 72.5714),
                    "jaipur, india": (26.9124, 75.7873),
                    "lucknow, india": (26.8467, 80.9462)
                }
                city_lower = city_name.lower()
                if city_lower in city_coords:
                    user_lat, user_lon = city_coords[city_lower]
                    st.success(f"📍 Found coordinates: {user_lat:.4f}, {user_lon:.4f}")
                else:
                    st.warning("City not found in database. Using default location.")
        
        # Store location in session state
        st.session_state['user_lat'] = user_lat
        st.session_state['user_lon'] = user_lon
        
        st.divider()
        st.markdown("- Generate a new recommendation below\n- Log sustainability in the tracker")

    # Add the 'agents' directory to the Python path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'agents')))

    # Import the run_agent_collaboration function from agent_setup
    from agents.agent_setup import run_agent_collaboration

    # Import enhanced models conditionally to support fast deploy without heavy deps
    fast_deploy = os.getenv('FAST_DEPLOY', '0') == '1'
    EnhancedWeatherAnalyst = None
    EnhancedPestDiseasePredictor = None
    if not fast_deploy:
        try:
            from models.enhanced_weather_analyst import EnhancedWeatherAnalyst
        except Exception:
            EnhancedWeatherAnalyst = None
        try:
            from models.enhanced_pest_predictor import EnhancedPestDiseasePredictor
        except Exception:
            EnhancedPestDiseasePredictor = None
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

    # --- Enhanced Modern & Robust Custom CSS with Vibrant Colors, Gradients, and 3D Light Background ---
    st.markdown("""
        <style>
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        @keyframes glow {
            0% { text-shadow: 0 0 5px rgba(255,255,255,0.5); }
            50% { text-shadow: 0 0 15px rgba(255,255,255,0.8); }
            100% { text-shadow: 0 0 5px rgba(255,255,255,0.5); }
        }
        html, body, [class*="css"]  {
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%), url('https://images.pexels.com/photos/4406323/pexels-photo-4406323.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2') no-repeat center center fixed;
            background-size: cover;
            background-blend-mode: lighten;
            color: #ffffff;
        }
        .main { background-color: transparent !important; padding: 0; }
        .stButton>button {
            width: 100%;
            margin-top: 1rem;
            margin-bottom: 2rem;
            background: linear-gradient(90deg, #00ff85 0%, #00bfff 100%);
            color: #1e3c72;
            border: none;
            border-radius: 20px;
            padding: 1rem;
            font-weight: 700;
            font-size: 1.2em;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 6px 15px rgba(0,191,255,0.3);
        }
        .stButton>button:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 10px 30px rgba(0,191,255,0.5);
            background: linear-gradient(90deg, #00bfff 0%, #00ff85 100%);
        }
        .card-section {
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(227,242,253,0.9) 100%);
            border-radius: 25px;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(30,60,114,0.15);
            padding: 2.5rem 2rem 2rem 2rem;
            transition: all 0.3s ease;
            animation: fadeIn 0.8s ease-out;
            position: relative;
            backdrop-filter: blur(5px);
        }
        .card-section:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 15px 40px rgba(30,60,114,0.25);
        }
        .section-step {
            position: absolute;
            top: -25px;
            left: 30px;
            background: linear-gradient(90deg, #00ff85 0%, #00bfff 100%);
            color: #ffffff;
            font-weight: 700;
            font-size: 1.2em;
            border-radius: 50px;
            padding: 0.5em 1.3em;
            box-shadow: 0 3px 10px rgba(0,191,255,0.2);
            letter-spacing: 1px;
            animation: glow 2s infinite;
        }
        .section-icon {
            font-size: 2.2em;
            margin-right: 0.6em;
            vertical-align: middle;
            color: #00bfff;
        }
        .section-instructions {
            color: #1e3c72;
            font-size: 1.1em;
            margin-bottom: 1.2em;
            margin-top: 0.6em;
            font-weight: 500;
        }
        .score-header {
            text-align: center;
            color: #00ff85;
            margin-bottom: 2.5rem;
            font-weight: 700;
            font-size: 2.2em;
            text-shadow: 0 0 10px rgba(0,255,133,0.3);
            animation: glow 2s infinite;
        }
        /* Smooth scrolling for navigation */
        html {
            scroll-behavior: smooth;
        }
        /* Navigation button hover effects */
        .nav-button {
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .nav-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,191,255,0.3);
        }
        @media (max-width: 900px) {
            .card-section, .score-header { font-size: 1em !important; }
            .stButton>button { font-size: 1em; }
        }
        @media (max-width: 600px) {
            .card-section { padding: 1.5rem; font-size: 0.95em; }
            .score-header { font-size: 1.8em !important; }
            .stButton>button { font-size: 1em; padding: 0.8rem; }
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Hero Section ---
    st.markdown("""
        <div style='background: linear-gradient(120deg, #00ff85 0%, #00bfff 100%), url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"); background-size: cover; background-blend-mode: overlay; border-radius: 25px; padding: 4rem 2rem 3rem 2rem; margin-bottom: 3rem; box-shadow: 0 10px 40px rgba(0,191,255,0.3); color: white; text-align: center; animation: fadeIn 1s ease-out;'>
            <h1 style='font-size:3em; margin-bottom: 0.5em; letter-spacing: 1.5px; text-shadow: 0 0 10px rgba(255,255,255,0.5);'>🌾 Sustainable Farming AI Platform</h1>
            <p style='font-size:1.4em; margin-bottom: 1.5em; max-width: 650px; margin-left:auto; margin-right:auto;'>Empowering farmers with <b>real-time, AI-powered recommendations</b> for a greener, more profitable future. Plan, optimize, and track your farm with ease—on any device.</p>
            <div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5em; margin-bottom: 1.5em;'>
                <div style='background: rgba(255,255,255,0.2); border-radius: 15px; padding: 1.2em 1.8em; font-size: 1.2em; display: flex; align-items: center; gap: 0.6em; box-shadow: 0 4px 15px rgba(255,255,255,0.2);'><span style='font-size:1.8em;'>🌱</span> Crop Planning</div>
                <div style='background: rgba(255,255,255,0.2); border-radius: 15px; padding: 1.2em 1.8em; font-size: 1.2em; display: flex; align-items: center; gap: 0.6em; box-shadow: 0 4px 15px rgba(255,255,255,0.2);'><span style='font-size:1.8em;'>🧪</span> Fertilizer Optimization</div>
                <div style='background: rgba(255,255,255,0.2); border-radius: 15px; padding: 1.2em 1.8em; font-size: 1.2em; display: flex; align-items: center; gap: 0.6em; box-shadow: 0 4px 15px rgba(255,255,255,0.2);'><span style='font-size:1.8em;'>📊</span> Sustainability Tracking</div>
                <div style='background: rgba(255,255,255,0.2); border-radius: 15px; padding: 1.2em 1.8em; font-size: 1.2em; display: flex; align-items: center; gap: 0.6em; box-shadow: 0 4px 15px rgba(255,255,255,0.2);'><span style='font-size:1.8em;'>🤖</span> AI Insights</div>
            </div>
            <div style='margin-top: 1.5em; font-size: 1.2em; background: rgba(255,255,255,0.15); border-radius: 10px; display: inline-block; padding: 0.8em 1.8em; box-shadow: 0 4px 15px rgba(255,255,255,0.2);'>
                <b>Get started below — follow the steps for a seamless experience!</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Farmer Usage Instructions ---
    st.markdown("""
        <div class='card-section'>
            <span class='section-step'>📋</span>
            <span class='section-icon'>📋</span>
            <b style='font-size:1.3em'>How to Use This Platform</b>
            <div class='section-instructions'>Follow these simple steps to get the most out of your farming AI assistant:</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Usage instructions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🌾 **Basic Farming Features**
        
        **1. Farm Details & Soil Analysis**
        - Enter your farm size (hectares or cents)
        - Upload soil photos or select soil type manually
        - Get AI-powered soil analysis and recommendations
        
        **2. Smart Recommendations**
        - Click "Generate Smart Recommendation" button
        - Get personalized crop suggestions based on your data
        - View detailed analysis with charts and insights
        
        **3. Crop Rotation Planning**
        - Plan your crop rotation for better soil health
        - Get timeline-based planting schedules
        - Optimize your farming calendar
        """)
    
    with col2:
        st.markdown("""
        ### 🚀 **Advanced Features**
        
        **4. Interactive Farm Map**
        - Create visual maps of your farm
        - Mark soil zones and risk areas
        - Get location-specific recommendations
        
        **5. Community Insights**
        - Share your farming data (anonymous)
        - Learn from other farmers' experiences
        - Get regional yield and price insights
        
        **6. AI Chatbot**
        - Ask any farming question
        - Get instant expert advice
        - Chat history is saved for reference
        """)
    
    st.markdown("""
    ### 💡 **Pro Tips for Farmers**
    
    - **Start with Farm Details**: Always begin by entering your farm size and soil type
    - **Use Voice Features**: Enable voice interface for hands-free operation
    - **Share Community Data**: Help other farmers by sharing your yield data
    - **Check Market Forecasts**: Use price predictions to plan your crops
    - **Enable Offline Mode**: Use the app without internet when needed
    - **Save Your Maps**: Create and save farm maps for future reference
    """)
    
    st.info("🎯 **Quick Start**: Click on any feature button in the sidebar to jump directly to that section!")

    # --- Main Content ---
    # Anchor for Farm Details
    st.markdown('<div id="farm-details"></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class='card-section'>
            <span class='section-step'>1</span>
            <span class='section-icon'>📏</span>
            <b style='font-size:1.3em'>{T['farm_details']}</b>
            <div class='section-instructions'>{T.get('farm_details_instruction', 'Enter your farm size and crop preference.')}</div>
            <div style='display:flex;gap:2em;justify-content:center;margin-top:1em;'>
                <div style='text-align:center;'>
                    <span style='font-size:2.5em;'>🌾</span><br><span style='font-size:1.1em;'>{T.get('farm_size_label', 'Farm size')}</span>
                </div>
                <div style='text-align:center;'>
                    <span style='font-size:2.5em;'>🌱</span><br><span style='font-size:1.1em;'>{T.get('crop_preference_label', 'Crop type')}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Voice input for farm details
    if (st.session_state.get('speech_interface') is not None and 
        st.session_state.get('voice_enabled', True)):
        st.markdown("### 🎤 Voice Input for Farm Details")
        voice_data = st.session_state['speech_interface'].create_voice_interface_for_farm_details(lang)
        
        # Update form values with voice input
        if voice_data:
            if 'land_size' in voice_data:
                st.session_state['land_size_voice'] = voice_data['land_size']
            if 'crop_preference' in voice_data:
                st.session_state['crop_preference_voice'] = voice_data['crop_preference']
            if 'soil_type' in voice_data:
                st.session_state['soil_type_voice'] = voice_data['soil_type']
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        # Use voice input if available, otherwise use slider
        if st.session_state.get('land_size_voice'):
            land_size = st.session_state['land_size_voice']
            st.info(f"🌾 Farm size from voice: {land_size} hectares")
        else:
            land_size = st.select_slider(
                f"🌾 {T.get('farm_size_label', 'Farm size')}",
                options=[1, 2, 5, 8, 10, 15, 20],
                value=8,
                help=T.get('farm_size_help', "Slide to select your farm size")
            )
            size_unit = st.selectbox(
                "Unit",
                options=["Hectares", "Cents"],
                index=0  # Default to Hectares
            )
            if size_unit == "Cents":
                land_size = land_size * 0.00404686  # Convert cents to hectares
            st.caption(f"Converted to {land_size:.2f} hectares for calculations.")
    with col2:
        # Use voice input if available, otherwise use selectbox
        if st.session_state.get('crop_preference_voice'):
            crop_preference = st.session_state['crop_preference_voice']
            st.info(f"🌱 Crop preference from voice: {crop_preference}")
        else:
            crop_preference = st.selectbox(
                f"🌱 {T.get('crop_preference_label', 'What would you like to grow?')}",
                options=["Grains", "Vegetables", "Fruits"],
                help=T.get('crop_preference_help', "Choose your preferred crop type")
            )

    # Anchor for Soil Analysis
    st.markdown('<div id="soil-analysis"></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class='card-section'>
            <span class='section-step'>2</span>
            <span class='section-icon'>🗺️</span>
            <b style='font-size:1.3em'>{T['soil_analysis']}</b>
            <div class='section-instructions'>{T.get('soil_analysis_instruction', 'Analyze your soil by uploading a photo or selecting manually.')}</div>
            <div style='display:flex;gap:2em;justify-content:center;margin-top:1em;'>
                <div style='text-align:center;'>
                    <span style='font-size:2.5em;'>📸</span><br><span style='font-size:1.1em;'>{T['upload_photo']}</span>
                </div>
                <div style='text-align:center;'>
                    <span style='font-size:2.5em;'>📝</span><br><span style='font-size:1.1em;'>{T['manual_selection']}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    soil_type = None
    
    # Check for voice input for soil type
    if st.session_state.get('soil_type_voice'):
        soil_type = st.session_state['soil_type_voice']
        st.info(f"🗺️ Soil type from voice: {soil_type}")
    else:
        soil_option = st.radio(
            f"🗺️ {T.get('soil_option_label', 'How would you like to determine your soil type?')}",
            [T['upload_photo'], T['manual_selection']],
            horizontal=True
        )
        
        if soil_option == T['upload_photo']:
            soil_photo = st.file_uploader(f"📸 {T['upload_photo']}", type=["jpg", "jpeg", "png"], key="soil_photo_uploader")
            if soil_photo:
                soil_type = analyze_soil_from_photo(soil_photo)
                if soil_type:
                    st.success(f"✅ {T.get('detected_soil_type', 'Detected soil type')}: {soil_type}")
                else:
                    st.warning(T.get('could_not_detect_soil', "⚠️ Could not determine soil type from photo. Please select manually."))
                    soil_type = st.selectbox(f"📝 {T['select_soil_type']}", options=["Loamy", "Sandy", "Clay"], key="manual_soil_select")
            else:
                soil_type = st.selectbox(f"📝 {T['select_soil_type']}", options=["Loamy", "Sandy", "Clay"], key="manual_soil_select_fallback")
        elif soil_option == T['manual_selection']:
            soil_type = st.selectbox(f"📝 {T['select_soil_type']}", options=["Loamy", "Sandy", "Clay"], key="manual_soil_select")

    # Anchor for Smart Recommendation
    st.markdown('<div id="smart-recommendation"></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class='card-section'>
            <span class='section-step'>3</span>
            <span class='section-icon'>💡</span>
            <b style='font-size:1.3em'>{T['generate_recommendation']}</b>
            <div class='section-instructions'>{T.get('recommendation_instruction', 'Click the button below to get your personalized AI-powered recommendation!')}</div>
            <div style='display:flex;gap:2em;justify-content:center;margin-top:1em;'>
                <div style='text-align:center;'>
                    <span style='font-size:2.5em;'>🤖</span><br><span style='font-size:1.1em;'>{T['generate_recommendation']}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Recommendation Generation ---
    if st.button(T['generate_recommendation'], type="primary"):
        # Progress feedback
        progress = st.progress(0)
        for i in range(0, 61, 12):
            time.sleep(0.05)
            progress.progress(min(i, 60))
        with st.spinner("🔄 Analyzing your farm conditions..."):
            try:
                result = run_agent_collaboration(land_size=land_size, soil_type=soil_type, crop_preference=crop_preference)
                progress.progress(80)
                crops_data = parse_recommendation(result['recommendation'])

                # --- Enhanced Weather Forecasting with Llama 2 ---
                # Weather analysis (heavy model optional)
                weather_analyst = EnhancedWeatherAnalyst() if EnhancedWeatherAnalyst is not None else None
                soil_ph = 6.5
                soil_moisture = 25
                
                # Get user's location from session state
                user_lat = st.session_state.get('user_lat', 12.9716)
                user_lon = st.session_state.get('user_lon', 77.5946)
                
                # Get comprehensive weather forecast with agricultural insights
                if weather_analyst is not None:
                    weather_data = weather_analyst.forecast_agricultural_conditions(
                        lat=user_lat,
                        lon=user_lon,
                        crop_type=crop_preference
                    )
                else:
                    # Lightweight fallback forecast
                    weather_data = {
                        'current_weather': {'temperature': 28.0, 'humidity': 60.0, 'description': 'Partly cloudy'},
                        'metrics': {'avg_temperature': 27.5, 'total_rainfall': 25.0, 'avg_humidity': 62.0},
                        'analysis': 'Fast mode: using lightweight weather analysis based on defaults.',
                        'agricultural_conditions': {'overall_risk': 'medium'},
                        'recommendations': ['Irrigate in early morning', 'Monitor humidity for fungal risk']
                    }
                
                # Organize results into tabs
                tab_summary, tab_charts, tab_details = st.tabs(["Summary", "Charts", "Details"])

                with tab_summary:
                    st.markdown(T['weather_forecast'])
                    
                    # Display location info
                    st.info(f"📍 **Location:** {user_lat:.4f}°N, {user_lon:.4f}°E")
                    
                    # Display current weather
                    current = weather_data['current_weather']
                    st.info(f"**Current Conditions:** Temperature: {current['temperature']:.1f}°C, "
                           f"Humidity: {current['humidity']:.1f}%, "
                           f"Description: {current['description']}")
                    
                    # Display forecast metrics
                    metrics = weather_data['metrics']
                    st.info(f"**5-Day Forecast:** Avg Temperature: {metrics['avg_temperature']:.1f}°C, "
                           f"Total Rainfall: {metrics['total_rainfall']:.1f}mm, "
                           f"Avg Humidity: {metrics['avg_humidity']:.1f}%")
                    
                    # Display AI analysis
                    st.markdown("**🤖 AI Weather Analysis:**")
                    st.text(weather_data['analysis'])
                    
                    # Display agricultural conditions
                    conditions = weather_data['agricultural_conditions']
                    risk_color = "🔴" if conditions['overall_risk'] == 'high' else "🟡" if conditions['overall_risk'] == 'medium' else "🟢"
                    st.markdown(f"**Agricultural Risk Level:** {risk_color} {conditions['overall_risk'].upper()}")
                    
                    # Display recommendations
                    if weather_data['recommendations']:
                        st.markdown("**💡 Weather Recommendations:**")
                        for rec in weather_data['recommendations']:
                            st.text(f"• {rec}")

                # --- Enhanced Pest/Disease Prediction with Llama 2 ---
                if EnhancedPestDiseasePredictor is not None:
                    pest_predictor = EnhancedPestDiseasePredictor()
                    pest_prediction = pest_predictor.predict(
                        crop_type=crop_preference,
                        soil_ph=soil_ph,
                        soil_moisture=soil_moisture,
                        temperature=current['temperature'],
                        rainfall=metrics['total_rainfall'],
                        additional_data={
                            'weather': current,
                            'soil': {'ph': soil_ph, 'moisture': soil_moisture, 'type': soil_type}
                        }
                    )
                else:
                    pest_prediction = 'Fast mode: basic IPM advice — scout weekly, rotate crops, and use targeted treatments as needed.'
                with tab_summary:
                    st.markdown(T['pest_prediction'])
                    st.text(pest_prediction)

                    st.markdown(T['personalized_recommendation'])

                    # Text-to-speech for recommendations
                    if (st.session_state.get('speech_interface') is not None and 
                        st.session_state.get('voice_enabled', True)):
                        st.markdown("### 🔊 Listen to Recommendations")
                        
                        # Debug information
                        with st.expander("🔧 Debug Information", expanded=False):
                            st.write(f"Speech interface available: {st.session_state.get('speech_interface') is not None}")
                            st.write(f"Voice enabled: {st.session_state.get('voice_enabled', False)}")
                            if st.session_state.get('speech_interface'):
                                si = st.session_state['speech_interface']
                                st.write(f"PyAudio available: {si.pyaudio_available}")
                                st.write(f"TTS engine available: {si.tts_engine is not None}")
                                st.write(f"Language: {lang}")
                                st.write(f"Recommendation length: {len(result['recommendation'])} characters")
                                
                                # Test button
                                if st.button("🔊 Test TTS with Simple Text", key="test_tts_simple"):
                                    with st.spinner("Testing TTS..."):
                                        success = si.text_to_speech("Hello, this is a test of text to speech.", lang)
                                        if success:
                                            st.success("✅ TTS test successful!")
                                        else:
                                            st.error("❌ TTS test failed!")
                        
                        # Main recommendation button
                        if st.button("🔊 Listen to Full Recommendation", key="speak_recommendation", help="Listen to the complete farming recommendation"):
                            with st.spinner("Generating audio for recommendation..."):
                                success = st.session_state['speech_interface'].text_to_speech(result['recommendation'], lang)
                                if success:
                                    st.success("✅ Audio generated successfully! Check your speakers.")
                                else:
                                    st.error("❌ Failed to generate audio. Please try again.")
                        
                        # Additional analysis buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔊 Listen to Weather Analysis", key="speak_weather", help="Listen to weather analysis"):
                                with st.spinner("Generating weather audio..."):
                                    success = st.session_state['speech_interface'].text_to_speech(weather_data['analysis'], lang)
                                    if success:
                                        st.success("✅ Weather audio generated!")
                                    else:
                                        st.error("❌ Failed to generate weather audio.")
                        with col2:
                            if st.button("🔊 Listen to Pest Prediction", key="speak_pest", help="Listen to pest and disease prediction"):
                                with st.spinner("Generating pest prediction audio..."):
                                    success = st.session_state['speech_interface'].text_to_speech(pest_prediction, lang)
                                    if success:
                                        st.success("✅ Pest prediction audio generated!")
                                    else:
                                        st.error("❌ Failed to generate pest prediction audio.")

                    # Download button for full recommendation text
                    st.download_button(
                        label="⬇️ Download Recommendation",
                        data=result['recommendation'],
                        file_name="recommendation.txt",
                        mime="text/plain"
                    )

                if 'Weather Forecast' in result and result['Weather Forecast']:
                    with tab_summary:
                        st.markdown("#### 🌤️ Weather Forecast (Agent)")
                        st.info(result['Weather Forecast'])

                if 'Pest/Disease Prediction' in result and result['Pest/Disease Prediction']:
                    with tab_summary:
                        st.markdown("#### 🐛 Pest/Disease Prediction (Agent)")
                        st.info(result['Pest/Disease Prediction'])

                if 'Warnings' in result and result['Warnings']:
                    with tab_summary:
                        for warn in result['Warnings']:
                            st.warning(f"Weather Alert: {warn}")

                if 'Pest/Disease Advice' in result and result['Pest/Disease Advice']:
                    with tab_summary:
                        st.info(f"Pest/Disease Advice: {result['Pest/Disease Advice']}")

                with tab_charts:
                    for crop_data in crops_data:
                        crop = crop_data['crop']
                        scores = crop_data['scores']
                        market_price = crop_data['market_price']
                        labels = list(scores.keys())
                        values = [score * 100 for score in scores.values()]
                        fig = go.Figure(data=[go.Bar(y=labels, x=values, orientation='h', marker=dict(color=[
                            "#00ff85", "#00bfff", "#ffcc00", "#ff6b6b", "#4ecdc4", "#45b7d1", "#ff9f1c"
                        ]), text=[f"{val:.1f}%" for val in values], textposition='auto')])
                        fig.update_layout(title=f"{crop.capitalize()} Scores (Market Price: ${market_price:.2f}/ton)", title_x=0.5, xaxis_title="Score (%)", yaxis_title="Category", xaxis=dict(range=[0, 100]), margin=dict(l=0, r=0, t=40, b=0), height=400)
                        st.plotly_chart(fig, use_container_width=True)

                with tab_charts:
                    st.markdown("<h3 class='score-header'>📊 Detailed Score Analysis</h3>", unsafe_allow_html=True)
                    for chart in result['chart_data']:
                        crop = chart['crop']
                        labels = chart['labels']
                        values = chart['values']
                        fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent', hoverinfo='label+value', marker=dict(colors=[
                            "#00ff85", "#00bfff", "#ffcc00", "#ff6b6b", "#4ecdc4", "#45b7d1", "#ff9f1c"
                        ]))])
                        fig.update_layout(title=f"{crop.capitalize()} Score Distribution", title_x=0.5, margin=dict(l=0, r=0, t=40, b=0), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                        st.plotly_chart(fig, use_container_width=True)

                with tab_details:
                    details = result['recommendation'].split("Details:")[1].strip()
                    details_html = details.replace('\n', '<br>')
                    st.markdown(f"<div class='card-section'><strong>{T['details']}</strong><br>{details_html}</div>", unsafe_allow_html=True)
                    
                    # Text-to-speech for details
                    if (st.session_state.get('speech_interface') is not None and 
                        st.session_state.get('voice_enabled', True)):
                        st.markdown("### 🔊 Listen to Details")
                        if st.button("🔊 Listen to Recommendation Details", key="speak_details", help="Listen to the detailed farming recommendations"):
                            with st.spinner("Generating details audio..."):
                                success = st.session_state['speech_interface'].text_to_speech(details, lang)
                                if success:
                                    st.success("✅ Details audio generated!")
                                else:
                                    st.error("❌ Failed to generate details audio.")

                progress.progress(100)
                st.balloons()

            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")

    # Anchor for Crop Rotation Planner
    st.markdown('<div id="crop-rotation-planner"></div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header(T['crop_rotation_planner'])
    planner = CropRotationPlanner(db_path=db_path)
    try:
        with sqlite3.connect(db_path) as conn:
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

    # Anchor for Fertilizer Optimization
    st.markdown('<div id="fertilizer-optimization"></div>', unsafe_allow_html=True)
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
        optimizer = FertilizerOptimizer(db_path=db_path)
        result = optimizer.calculate_fertilizer(st.session_state['fert_land'], st.session_state['fert_soil'], st.session_state['fert_crop'])
        st.success(f"For {st.session_state['fert_land']} hectares of {st.session_state['fert_soil'].lower()} soil planting {st.session_state['fert_crop'].lower()}, use:")
        st.write(f"- Nitrogen: {result['nitrogen_kg']} kg")
        st.write(f"- Phosphorus: {result['phosphorus_kg']} kg")
        st.write(f"- Potassium: {result['potassium_kg']} kg")
        st.caption("*This recommendation factors in sustainability by reducing excess fertilizer to lower carbon footprint.")

    # Anchor for Previous Recommendations
    st.markdown('<div id="previous-recommendations"></div>', unsafe_allow_html=True)
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
            # Update sidebar CSV download
            st.session_state['last_recs_csv'] = past_recommendations.to_csv(index=False)
        else:
            st.info("No past recommendations found.")
    except Exception as e:
        st.warning(f"Could not load past recommendations: {str(e)}")

    # Anchor for Sustainability Score Tracker
    st.markdown('<div id="sustainability-score-tracker"></div>', unsafe_allow_html=True)
    # --- Sustainability Score Tracker ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("🌱 Sustainability Score Tracker")

    # Recommended values
    RECOMMENDED_WATER = 2.0  # e.g., 2 ML/ha/season
    RECOMMENDED_FERTILIZER = 1.5  # e.g., 1.5 tons/ha/season

    # Helper: Calculate sustainability score
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

    # Ensure sustainability_scores table exists
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

    # --- Voice Input for Sustainability Data ---
    if (st.session_state.get('speech_interface') is not None and 
        st.session_state.get('voice_enabled', True)):
        st.markdown("### 🎤 Voice Input for Sustainability Data")
        voice_sustainability_data = st.session_state['speech_interface'].create_voice_interface_for_sustainability(lang)
        
        # Update form values with voice input
        if voice_sustainability_data:
            if 'water_score' in voice_sustainability_data:
                st.session_state['voice_water_score'] = voice_sustainability_data['water_score']
            if 'fertilizer_use' in voice_sustainability_data:
                st.session_state['voice_fertilizer_use'] = voice_sustainability_data['fertilizer_use']
            if 'rotation' in voice_sustainability_data:
                st.session_state['voice_rotation'] = voice_sustainability_data['rotation']

    # --- User Input for Current Season ---
    with st.form("sustainability_form"):
        st.markdown("**Log your current season's practices:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            # Use voice input if available
            if st.session_state.get('voice_water_score'):
                water_score = st.session_state['voice_water_score']
                st.info(f"💧 Water usage from voice: {water_score} ML/ha")
            else:
                water_score = st.number_input("Water usage (ML/ha)", min_value=0.0, max_value=10.0, value=RECOMMENDED_WATER, step=0.1)
        with col2:
            # Use voice input if available
            if st.session_state.get('voice_fertilizer_use'):
                fertilizer_use = st.session_state['voice_fertilizer_use']
                st.info(f"🧪 Fertilizer use from voice: {fertilizer_use} tons/ha")
            else:
                fertilizer_use = st.number_input("Fertilizer use (tons/ha)", min_value=0.0, max_value=10.0, value=RECOMMENDED_FERTILIZER, step=0.1)
        with col3:
            # Use voice input if available
            if st.session_state.get('voice_rotation') is not None:
                rotation = st.session_state['voice_rotation']
                st.info(f"🔄 Crop rotation from voice: {'Yes' if rotation else 'No'}")
            else:
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
        fig.add_trace(go.Scatter(x=df_scores['timestamp'], y=df_scores['score'], mode='lines+markers', name='Sustainability Score', line=dict(color='#00ff85', width=3)))
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

    # --- Interactive Farm Map ---
    st.markdown('<div id="interactive-farm-map"></div>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    st.header("🗺️ Interactive Farm Map")
    
    # Farm Map Section
    st.markdown("""
        <div class='card-section'>
            <span class='section-step'>🗺️</span>
            <span class='section-icon'>🗺️</span>
            <b style='font-size:1.3em'>Interactive Farm Mapping</b>
            <div class='section-instructions'>Upload or draw your farm map to get location-specific recommendations and risk analysis.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Map creation options
    map_option = st.radio(
        "Choose map creation method:",
        ["Create New Map", "Load Existing Map", "Upload Farm Image"],
        horizontal=True
    )
    
    if map_option == "Create New Map":
        # Get farm coordinates
        col1, col2 = st.columns(2)
        with col1:
            farm_lat = st.number_input("Farm Latitude", value=12.9716, min_value=-90.0, max_value=90.0, step=0.0001)
        with col2:
            farm_lon = st.number_input("Farm Longitude", value=77.5946, min_value=-180.0, max_value=180.0, step=0.0001)
        
        # Create interactive map
        m = folium.Map(
            location=[farm_lat, farm_lon],
            zoom_start=15,
            tiles='OpenStreetMap'
        )
        
        # Add farm boundary (example)
        farm_boundary = folium.Rectangle(
            bounds=[[farm_lat-0.001, farm_lon-0.001], [farm_lat+0.001, farm_lon+0.001]],
            color='green',
            fill=True,
            fillColor='lightgreen',
            fillOpacity=0.3,
            popup='Your Farm'
        )
        farm_boundary.add_to(m)
        
        # Add soil zones
        soil_zones = [
            {"lat": farm_lat-0.0005, "lon": farm_lon-0.0005, "soil": "Clay", "color": "brown"},
            {"lat": farm_lat+0.0005, "lon": farm_lon-0.0005, "soil": "Sandy", "color": "yellow"},
            {"lat": farm_lat-0.0005, "lon": farm_lon+0.0005, "soil": "Loamy", "color": "green"},
            {"lat": farm_lat+0.0005, "lon": farm_lon+0.0005, "soil": "Clay", "color": "brown"}
        ]
        
        for zone in soil_zones:
            folium.CircleMarker(
                location=[zone["lat"], zone["lon"]],
                radius=20,
                popup=f"Soil Type: {zone['soil']}",
                color=zone["color"],
                fill=True,
                fillColor=zone["color"],
                fillOpacity=0.7
            ).add_to(m)
        
        # Add risk areas
        risk_areas = [
            {"lat": farm_lat-0.0003, "lon": farm_lon+0.0003, "risk": "Erosion Risk", "color": "red"},
            {"lat": farm_lat+0.0003, "lon": farm_lon-0.0003, "risk": "Waterlogging", "color": "blue"}
        ]
        
        for area in risk_areas:
            folium.Marker(
                location=[area["lat"], area["lon"]],
                popup=f"⚠️ {area['risk']}",
                icon=folium.Icon(color=area["color"], icon='warning-sign')
            ).add_to(m)
        
        # Display map
        st_folium(m, width=700, height=500)
        
        # Map Legend and Explanation
        st.markdown("### 🗺️ Map Legend & Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🌱 Soil Zones:**
            - 🟤 **Brown Circles**: Clay soil areas
            - 🟡 **Yellow Circles**: Sandy soil areas  
            - 🟢 **Green Circles**: Loamy soil areas
            """)
        
        with col2:
            st.markdown("""
            **⚠️ Risk Areas:**
            - 🔴 **Red Markers**: Erosion risk zones
            - 🔵 **Blue Markers**: Waterlogging areas
            - ⚠️ **Warning Icons**: High-risk locations
            """)
        
        with col3:
            st.markdown("""
            **🏡 Farm Features:**
            - 🟢 **Green Rectangle**: Your farm boundary
            - 📍 **Markers**: Specific locations
            - 🗺️ **Interactive**: Click and zoom to explore
            """)
        
        st.info("💡 **Tip**: Click on any marker or zone to see detailed information about that area!")
        
        # Save map data
        if st.button("💾 Save Farm Map"):
            map_data = {
                "center": [farm_lat, farm_lon],
                "soil_zones": soil_zones,
                "risk_areas": risk_areas,
                "boundary": [[farm_lat-0.001, farm_lon-0.001], [farm_lat+0.001, farm_lon+0.001]]
            }
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO farm_maps 
                    (username, farm_name, map_data, recommendations, risk_areas, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user['username'],
                    user['farm_name'],
                    json.dumps(map_data),
                    json.dumps({"recommendations": ["Plant soybeans in northern section", "Avoid planting in erosion risk area"]}),
                    json.dumps(risk_areas),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                conn.commit()
            st.success("✅ Farm map saved successfully!")
    
    elif map_option == "Load Existing Map":
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM farm_maps WHERE username = ? ORDER BY updated_at DESC LIMIT 1", (user['username'],))
                map_record = cursor.fetchone()
        except Exception as e:
            st.error(f"Could not load farm map: {e}")
            map_record = None
        
        if map_record:
            map_data = json.loads(map_record[3])
            recommendations = json.loads(map_record[4])
            risk_areas = json.loads(map_record[5])
            
            # Recreate map from saved data
            m = folium.Map(
                location=map_data["center"],
                zoom_start=15,
                tiles='OpenStreetMap'
            )
            
            # Add farm boundary
            farm_boundary = folium.Rectangle(
                bounds=map_data["boundary"],
                color='green',
                fill=True,
                fillColor='lightgreen',
                fillOpacity=0.3,
                popup='Your Farm'
            )
            farm_boundary.add_to(m)
            
            # Add soil zones
            for zone in map_data["soil_zones"]:
                folium.CircleMarker(
                    location=[zone["lat"], zone["lon"]],
                    radius=20,
                    popup=f"Soil Type: {zone['soil']}",
                    color=zone["color"],
                    fill=True,
                    fillColor=zone["color"],
                    fillOpacity=0.7
                ).add_to(m)
            
            # Add risk areas
            for area in risk_areas:
                folium.Marker(
                    location=[area["lat"], area["lon"]],
                    popup=f"⚠️ {area['risk']}",
                    icon=folium.Icon(color=area["color"], icon='warning-sign')
                ).add_to(m)
            
            st_folium(m, width=700, height=500)
            
            # Map Legend for Loaded Map
            st.markdown("### 🗺️ Your Farm Map Legend")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **🌱 Soil Zones:**
                - 🟤 **Brown**: Clay soil
                - 🟡 **Yellow**: Sandy soil  
                - 🟢 **Green**: Loamy soil
                """)
            
            with col2:
                st.markdown("""
                **⚠️ Risk Areas:**
                - 🔴 **Red**: Erosion risk
                - 🔵 **Blue**: Waterlogging
                - ⚠️ **Warning**: High risk
                """)
            
            with col3:
                st.markdown("""
                **🏡 Farm Layout:**
                - 🟢 **Green**: Farm boundary
                - 📍 **Markers**: Key locations
                - 🗺️ **Interactive**: Click to explore
                """)
            
            # Display recommendations
            st.markdown("### 📋 Location-Specific Recommendations")
            for rec in recommendations["recommendations"]:
                st.info(f"💡 {rec}")
        else:
            st.info("No saved farm map found. Create a new map first!")
    
    elif map_option == "Upload Farm Image":
        uploaded_image = st.file_uploader("Upload Farm Image", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            st.image(uploaded_image, caption="Your Farm Image", use_column_width=True)
            st.info("🔄 Image analysis in progress... This feature will analyze your farm image and create recommendations based on visual soil and terrain analysis.")

    # --- Community Insights ---
    st.markdown('<div id="community-insights"></div>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    st.header("👥 Community Insights")
    
    st.markdown("""
        <div class='card-section'>
            <span class='section-step'>👥</span>
            <span class='section-icon'>👥</span>
            <b style='font-size:1.3em'>Community-Driven Insights</b>
            <div class='section-instructions'>Share and learn from anonymized community data on crop yields, market prices, and sustainability practices.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Community data sharing
    with st.expander("📊 Share Your Data (Anonymous)"):
        st.markdown("**Help the community by sharing your farming data:**")
        
        with st.form("community_data_form"):
            col1, col2 = st.columns(2)
            with col1:
                crop_type = st.selectbox("Crop Type", ["Rice", "Wheat", "Corn", "Soybean", "Tomato", "Potato", "Other"])
                yield_data = st.number_input("Yield (tons/hectare)", min_value=0.0, max_value=50.0, step=0.1)
            with col2:
                market_price = st.number_input("Market Price (₹/ton)", min_value=0, max_value=100000, step=100)
                region = st.selectbox("Region", ["North", "South", "East", "West", "Central"])
            
            sustainability_practice = st.selectbox("Sustainability Practice", [
                "Organic Farming", "Drip Irrigation", "Crop Rotation", 
                "Integrated Pest Management", "Conservation Tillage", "Other"
            ])
            season = st.selectbox("Season", ["Kharif", "Rabi", "Zaid", "Year-round"])
            
            if st.form_submit_button("📤 Share Data"):
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO community_insights 
                        (username, crop_type, yield_data, market_price, sustainability_practice, region, season, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user['username'], crop_type, yield_data, market_price, 
                        sustainability_practice, region, season, 
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    conn.commit()
                st.success("✅ Data shared successfully! Thank you for contributing to the community.")
    
    # Community insights display
    st.markdown("### 📈 Community Insights Dashboard")
    
    # Get community data
    try:
        with sqlite3.connect(db_path) as conn:
            community_data = pd.read_sql("""
                SELECT crop_type, AVG(yield_data) as avg_yield, AVG(market_price) as avg_price, 
                       sustainability_practice, region, season, COUNT(*) as data_points
                FROM community_insights 
                GROUP BY crop_type, sustainability_practice, region, season
                ORDER BY data_points DESC
            """, conn)
    except Exception as e:
        st.warning(f"Could not load community data: {e}")
        community_data = pd.DataFrame()
    
    if not community_data.empty:
        # Display insights
        st.markdown("#### 🌾 Regional Yield Insights")
        for _, row in community_data.head(5).iterrows():
            st.info(f"**{row['crop_type']}** in {row['region']} region: "
                   f"Average yield {row['avg_yield']:.1f} tons/hectare with {row['sustainability_practice']} "
                   f"({row['data_points']} farmers contributed)")
        
        # Create insights chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=community_data['crop_type'],
            y=community_data['avg_yield'],
            name='Average Yield',
            marker_color='#00ff85'
        ))
        fig.update_layout(
            title="Community Yield Data by Crop Type",
            xaxis_title="Crop Type",
            yaxis_title="Average Yield (tons/hectare)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No community data available yet. Be the first to share your data!")

    # --- Market Price Forecasting Dashboard ---
    st.markdown('<div id="market-dashboard"></div>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    st.header("📈 Market Price Forecasting Dashboard")
    
    st.markdown("""
        <div class='card-section'>
            <span class='section-step'>📈</span>
            <span class='section-icon'>📈</span>
            <b style='font-size:1.3em'>Market Price Forecasting</b>
            <div class='section-instructions'>Get AI-powered market price predictions for your crops over the next 3-6 months.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Market forecasting interface
    col1, col2 = st.columns(2)
    with col1:
        forecast_crop = st.selectbox("Select Crop for Forecasting", 
                                   ["Rice", "Wheat", "Corn", "Soybean", "Tomato", "Potato", "Cotton"])
    with col2:
        forecast_period = st.selectbox("Forecast Period", ["3 months", "6 months", "12 months"])
    
    if st.button("🔮 Generate Price Forecast"):
        # Simulate market forecasting (in real implementation, this would use ML models)
        import random
        base_prices = {
            "Rice": 2500, "Wheat": 2000, "Corn": 1800, "Soybean": 3500,
            "Tomato": 8000, "Potato": 1500, "Cotton": 6000
        }
        
        base_price = base_prices.get(forecast_crop, 2000)
        
        # Generate forecast data
        months = 3 if "3" in forecast_period else 6 if "6" in forecast_period else 12
        forecast_data = []
        current_price = base_price
        
        for i in range(months):
            # Simulate price fluctuations
            change = random.uniform(-0.1, 0.15)  # -10% to +15% change
            current_price = current_price * (1 + change)
            confidence = max(0.6, 1.0 - (i * 0.05))  # Decreasing confidence over time
            
            forecast_data.append({
                "month": f"Month {i+1}",
                "price": round(current_price, 2),
                "confidence": round(confidence, 2)
            })
        
        # Save forecast to database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for data in forecast_data:
                cursor.execute("""
                    INSERT INTO market_forecasts 
                    (crop, predicted_price, confidence_score, forecast_date, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    forecast_crop, data["price"], data["confidence"], 
                    data["month"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
            conn.commit()
        
        # Display forecast
        st.markdown(f"### 📊 {forecast_crop} Price Forecast")
        
        # Create forecast chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[d["month"] for d in forecast_data],
            y=[d["price"] for d in forecast_data],
            mode='lines+markers',
            name='Predicted Price',
            line=dict(color='#00bfff', width=3),
            marker=dict(size=8)
        ))
        
        # Add confidence bands
        upper_band = [d["price"] * (1 + (1-d["confidence"])) for d in forecast_data]
        lower_band = [d["price"] * (1 - (1-d["confidence"])) for d in forecast_data]
        
        fig.add_trace(go.Scatter(
            x=[d["month"] for d in forecast_data],
            y=upper_band,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=[d["month"] for d in forecast_data],
            y=lower_band,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(0,191,255,0.2)',
            name='Confidence Band',
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title=f"{forecast_crop} Price Forecast ({forecast_period})",
            xaxis_title="Time Period",
            yaxis_title="Price (₹/ton)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display insights
        st.markdown("### 💡 Market Insights")
        current_price = forecast_data[0]["price"]
        future_price = forecast_data[-1]["price"]
        price_change = ((future_price - current_price) / current_price) * 100
        
        if price_change > 0:
            st.success(f"📈 {forecast_crop} prices are expected to **increase by {price_change:.1f}%** over {forecast_period}")
        else:
            st.warning(f"📉 {forecast_crop} prices are expected to **decrease by {abs(price_change):.1f}%** over {forecast_period}")
        
        st.info(f"🎯 **Recommendation**: {'Consider planting' if price_change > 5 else 'Monitor market closely'} {forecast_crop} for optimal returns")

    # --- AI Chatbot ---
    st.markdown('<div id="ai-chatbot"></div>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    st.header("🤖 AI Chatbot")
    
    st.markdown("""
        <div class='card-section'>
            <span class='section-step'>🤖</span>
            <span class='section-icon'>🤖</span>
            <b style='font-size:1.3em'>AI Farming Assistant</b>
            <div class='section-instructions'>Ask questions about farming practices, crop management, and get instant AI-powered answers.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat session
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # Chat interface
    st.markdown("### 💬 Chat with AI Assistant")
    
    # Display chat history
    for message in st.session_state['chat_history']:
        if message['role'] == 'user':
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI Assistant:** {message['content']}")
    
    # Chat input
    user_query = st.text_input("Ask me anything about farming:", placeholder="e.g., What's the best fertilizer for loamy soil?")
    
    if st.button("💬 Send Message") and user_query:
        # Add user message to history
        st.session_state['chat_history'].append({'role': 'user', 'content': user_query})
        
        # Generate AI response (simplified - in real implementation, this would use the agent framework)
        ai_response = generate_chatbot_response(user_query)
        
        # Add AI response to history
        st.session_state['chat_history'].append({'role': 'assistant', 'content': ai_response})
        
        # Save to database
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chatbot_sessions 
                (username, session_id, query, response, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user['username'], session_id, user_query, ai_response,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
        
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state['chat_history'] = []
        st.rerun()

    # --- Offline Mode ---
    st.markdown('<div id="offline-mode"></div>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    st.header("📱 Offline Mode")
    
    st.markdown("""
        <div class='card-section'>
            <span class='section-step'>📱</span>
            <span class='section-icon'>📱</span>
            <b style='font-size:1.3em'>Offline Farming Assistant</b>
            <div class='section-instructions'>Use the app without internet connection. Data syncs automatically when online.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Offline mode status
    offline_status = st.session_state.get('offline_mode', False)
    if st.checkbox("📱 Enable Offline Mode", value=offline_status):
        st.session_state['offline_mode'] = True
        st.success("✅ Offline mode enabled. You can now use the app without internet connection.")
        
        # Offline data management
        st.markdown("### 📊 Offline Data Management")
        
        # Check for unsynced data
        try:
            with sqlite3.connect(db_path) as conn:
                unsynced_data = pd.read_sql("""
                    SELECT data_type, COUNT(*) as count 
                    FROM offline_data 
                    WHERE sync_status = 'pending' 
                    GROUP BY data_type
                """, conn)
        except Exception as e:
            st.warning(f"Could not load offline data: {e}")
            unsynced_data = pd.DataFrame()
        
        if not unsynced_data.empty:
            st.warning(f"⚠️ You have {unsynced_data['count'].sum()} unsynced data items")
            for _, row in unsynced_data.iterrows():
                st.info(f"📄 {row['data_type']}: {row['count']} items pending sync")
            
            if st.button("🔄 Sync All Data"):
                # Simulate data sync
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE offline_data 
                        SET sync_status = 'synced', synced_at = ?
                        WHERE sync_status = 'pending'
                    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
                    conn.commit()
                st.success("✅ All data synced successfully!")
        else:
            st.success("✅ All data is synced!")
    else:
        st.session_state['offline_mode'] = False
        st.info("📶 Online mode enabled. All features available with internet connection.")

    # --- Footer ---
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
    st.markdown(f"""
        ---
        <div style='text-align: center; color: #2ecc71; opacity: 0.95;'>
            <p style='color:#2ecc71;'>{T['built_with']}</p>
            <p><small style='color:#2ecc71;'>{T['last_updated']} {current_time}</small></p>
        </div>
    """, unsafe_allow_html=True)