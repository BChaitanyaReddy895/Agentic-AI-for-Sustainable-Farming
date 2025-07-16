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
import base64
import io

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
st.set_page_config(page_title=LANGUAGES['English']['title'], page_icon="🌾")

# Initialize database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db'))
initialize_db()

# Update initialize_db to include users table
def initialize_db():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Create recommendations table (existing)
        cursor.execute('''CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT,
            score REAL,
            rationale TEXT,
            carbon_score REAL,
            water_score REAL,
            erosion_score REAL,
            timestamp TEXT
        )''')
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
        conn.commit()

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

    # --- Modern & Responsive Custom CSS ---
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(120deg, #e0f7fa 0%, #f5f7fa 100%);
        }
        .main { background-color: transparent !important; padding: 0; }
        .stButton>button {
            width: 100%;
            margin-top: 1rem;
            margin-bottom: 2rem;
            background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.9rem;
            font-weight: 700;
            font-size: 1.1em;
            letter-spacing: 0.5px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 12px rgba(24,90,157,0.08);
        }
        .stButton>button:hover {
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 8px 24px rgba(24,90,157,0.15);
        }
        .card-section {
            background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%);
            border-radius: 18px;
            margin: 28px 0;
            box-shadow: 0 8px 24px rgba(24,90,157,0.08);
            padding: 2.2rem 1.5rem 1.5rem 1.5rem;
            transition: transform 0.3s;
            position: relative;
        }
        .card-section:hover { transform: translateY(-5px) scale(1.01); }
        .section-step {
            position: absolute;
            top: -22px;
            left: 24px;
            background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
            color: #fff;
            font-weight: 700;
            font-size: 1.1em;
            border-radius: 50px;
            padding: 0.4em 1.2em;
            box-shadow: 0 2px 8px rgba(24,90,157,0.10);
            letter-spacing: 1px;
        }
        .section-icon {
            font-size: 2em;
            margin-right: 0.5em;
            vertical-align: middle;
        }
        .section-instructions {
            color: #185a9d;
            font-size: 1.08em;
            margin-bottom: 1em;
            margin-top: 0.5em;
            font-weight: 500;
        }
        .score-header {
            text-align: center;
            color: #185a9d;
            margin-bottom: 2rem;
            font-weight: 700;
            font-size: 2em;
            text-shadow: 1px 1px 2px rgba(24,90,157,0.08);
        }
        @media (max-width: 900px) {
            .card-section, .score-header { font-size: 1em !important; }
            .stButton>button { font-size: 1em; }
        }
        @media (max-width: 600px) {
            .card-section { padding: 1rem; font-size: 0.95em; }
            .score-header { font-size: 1.1em !important; }
            .stButton>button { font-size: 0.95em; padding: 0.7rem; }
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Hero Section ---
    st.markdown("""
        <div style='background: linear-gradient(120deg, #43cea2 0%, #185a9d 100%), url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"); background-size: cover; background-blend-mode: multiply; border-radius: 22px; padding: 3.5rem 1.5rem 2.5rem 1.5rem; margin-bottom: 2.5rem; box-shadow: 0 8px 32px rgba(24,90,157,0.18); color: white; text-align: center;'>
            <h1 style='font-size:2.8em; margin-bottom: 0.4em; letter-spacing: 1px;'>🌾 Sustainable Farming AI Platform</h1>
            <p style='font-size:1.25em; margin-bottom: 1.2em; max-width: 600px; margin-left:auto; margin-right:auto;'>Empowering farmers with <b>real-time, AI-powered recommendations</b> for a greener, more profitable future. Plan, optimize, and track your farm with ease—on any device.</p>
            <div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 1.2em; margin-bottom: 1.2em;'>
                <div style='background: rgba(255,255,255,0.13); border-radius: 12px; padding: 1em 1.5em; font-size: 1.1em; display: flex; align-items: center; gap: 0.5em;'><span style='font-size:1.5em;'>🌱</span> Crop Planning</div>
                <div style='background: rgba(255,255,255,0.13); border-radius: 12px; padding: 1em 1.5em; font-size: 1.1em; display: flex; align-items: center; gap: 0.5em;'><span style='font-size:1.5em;'>🧪</span> Fertilizer Optimization</div>
                <div style='background: rgba(255,255,255,0.13); border-radius: 12px; padding: 1em 1.5em; font-size: 1.1em; display: flex; align-items: center; gap: 0.5em;'><span style='font-size:1.5em;'>📊</span> Sustainability Tracking</div>
                <div style='background: rgba(255,255,255,0.13); border-radius: 12px; padding: 1em 1.5em; font-size: 1.1em; display: flex; align-items: center; gap: 0.5em;'><span style='font-size:1.5em;'>🤖</span> AI Insights</div>
            </div>
            <div style='margin-top: 1.2em; font-size: 1.1em; background: rgba(255,255,255,0.10); border-radius: 8px; display: inline-block; padding: 0.7em 1.5em;'>
                <b>Get started below — follow the steps for a seamless experience!</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Main Content ---
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

    col1, col2 = st.columns(2, gap="large")
    with col1:
        land_size = st.select_slider(
            f"🌾 {T.get('farm_size_label', 'Farm size (hectares)')}",
            options=[1, 2, 5, 8, 10, 15, 20],
            value=8,
            help=T.get('farm_size_help', "Slide to select your farm size")
        )
    with col2:
        crop_preference = st.selectbox(
            f"🌱 {T.get('crop_preference_label', 'What would you like to grow?')}",
            options=["Grains", "Vegetables", "Fruits"],
            help=T.get('crop_preference_help', "Choose your preferred crop type")
        )

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
                st.markdown(f"<div class='card-section'><strong>{T['details']}</strong><br>{details_html}</div>", unsafe_allow_html=True)

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
