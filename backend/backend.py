from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
import json
import pandas as pd
from datetime import datetime
import random
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Change in production
DB_PATH = os.path.join('database', 'sustainable_farming.db')

# Ensure DB dir exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Multilingual Support (from app.py)
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
        'no_users': "No farmers registered yet. Sign up to start!",
        'logout': "🚪 Logout",
        'profile': "👤 My Profile",
        'dashboard': "🏠 Dashboard",
        'instructions': "Follow these steps: 1) Log in or sign up, 2) Enter farm details, 3) Explore recommendations.",
        'contact_us': "📞 Contact Us",
        'contact_desc': "Need help? Reach out to our support team."
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
        'no_users': "ఇంకా రైతులు నమోదు కాలేదు. సైన్ అప్ చేయండి!",
        'logout': "🚪 లాగౌట్",
        'profile': "👤 నా ప్రొఫైల్",
        'dashboard': "🏠 డాష్బోర్డ్",
        'instructions': "ఈ దశలను అనుసరించండి: 1) లాగిన్ అయ్యండి లేదా సైన్ అప్ చేయండి, 2) వ్యవసాయ వివరాలను నమోదు చేయండి, 3) సూచనలను అన్వేషించండి.",
        'contact_us': "📞 మమ్మల్ని సంప్రదించండి",
        'contact_desc': "సహాయం అవసరమా? మా మద్దతు బృందంతో సంప్రదించండి."
    },
    # Add other languages (Kannada, Hindi, French, Spanish, Tamil) as in app.py (omitted for brevity)
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        farm_name TEXT,
        profile_picture TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        crop TEXT,
        score REAL,
        rationale TEXT,
        carbon_score REAL,
        water_score REAL,
        erosion_score REAL,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sustainability_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        timestamp TEXT,
        water_score REAL,
        fertilizer_use REAL,
        rotation INTEGER,
        score REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS farm_maps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        farm_name TEXT,
        map_data TEXT,
        recommendations TEXT,
        risk_areas TEXT,
        created_at TEXT,
        updated_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS community_insights (
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
    c.execute('''CREATE TABLE IF NOT EXISTS market_forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        crop TEXT,
        predicted_price REAL,
        confidence_score REAL,
        forecast_date TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chatbot_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        session_id TEXT,
        query TEXT,
        response TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS offline_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        data_type TEXT,
        data_content TEXT,
        sync_status TEXT,
        created_at TEXT,
        synced_at TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def image_to_base64(image_file):
    if image_file:
        image = Image.open(image_file)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    return None

def analyze_soil_from_photo(image_data):
    try:
        image = Image.open(BytesIO(base64.b64decode(image_data.split(',')[1])))
        image_array = np.array(image)
        avg_color = np.mean(image_array, axis=(0, 1))
        r, g, b = avg_color
        if r > 120 and g < 110 and b < 110:
            return "Clay"
        elif r > 90 and g > 90 and b < 80:
            return "Sandy"
        else:
            return "Loamy"
    except:
        return "Loamy"

def generate_chatbot_response(query):
    query_lower = query.lower()
    if 'fertilizer' in query_lower:
        if 'loamy' in query_lower:
            return "For loamy soil, use balanced NPK (10-10-10) at 100-150 kg/hectare."
        elif 'sandy' in query_lower:
            return "For sandy soil, use NPK (15-5-10) with organic matter."
    elif 'weather' in query_lower:
        return "Check the weather forecast section for current data."
    elif 'pest' in query_lower:
        return "Monitor for pests; use neem oil if detected."
    return "I'm here to assist with farming queries. Please provide more details!"

def calculate_sustainability_score(water, fertilizer, rotation):
    score = 100
    if water > 2.0:
        score -= min(30, 30 * (water - 2.0) / 2.0)
    if fertilizer > 1.5:
        score -= min(30, 30 * (fertilizer - 1.5) / 1.5)
    if rotation:
        score += 10
    else:
        score -= 10
    return max(0, min(100, score))

@app.route('/')
def index():
    if not session.get('user'):
        return redirect(url_for('login_page'))
    lang = session.get('lang', 'English')
    T = LANGUAGES[lang]
    return render_template('index.html', languages=LANGUAGES, lang=lang, T=T, user=session.get('user'), current_time=datetime.now().strftime("%I:%M %p IST, %d %B %Y"))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = {'username': user[1], 'farm_name': user[2]}
            return redirect(url_for('index'))
        return render_template('login.html', T=LANGUAGES[session.get('lang', 'English')], error="User not found")
    return render_template('login.html', T=LANGUAGES[session.get('lang', 'English')])

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        username = request.form['username']
        farm_name = request.form['farm_name']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return render_template('signup.html', T=LANGUAGES[session.get('lang', 'English')], error=LANGUAGES[session.get('lang', 'English')]['username_exists'])
        c.execute("INSERT INTO users (username, farm_name, created_at) VALUES (?, ?, ?)",
                  (username, farm_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        session['user'] = {'username': username, 'farm_name': farm_name}
        return redirect(url_for('index'))
    return render_template('signup.html', T=LANGUAGES[session.get('lang', 'English')])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

@app.route('/api/generate_recommendation', methods=['POST'])
def generate_recommendation():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    land_size = data['land_size']
    soil_type = data['soil_type']
    crop_preference = data['crop_preference']
    crops = ['Rice', 'Wheat', 'Corn']
    recs = []
    for crop in crops:
        score = random.uniform(70, 95)
        recs.append({'crop': crop, 'score': score, 'rationale': f"Recommended for {soil_type} soil."})
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for rec in recs:
        c.execute("INSERT INTO recommendations (username, crop, score, rationale, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (session['user']['username'], rec['crop'], rec['score'], rec['rationale'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({'recommendations': recs})

@app.route('/api/soil_analysis', methods=['POST'])
def soil_analysis():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    if 'photo' in request.files:
        photo = request.files['photo']
        base64_img = image_to_base64(photo)
        soil = analyze_soil_from_photo(f"data:image/png;base64,{base64_img}")
        return jsonify({'soil_type': soil})
    return jsonify({'soil_type': request.json.get('manual_soil', 'Loamy')})

@app.route('/api/weather_forecast', methods=['POST'])
def weather_forecast():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    lat = request.json['lat']
    lon = request.json['lon']
    return jsonify({
        'current': {'temperature': random.uniform(20, 30), 'humidity': random.uniform(50, 80)},
        'forecast': {'avg_temp': 25, 'rainfall': 10},
        'analysis': 'Ideal for planting.'
    })

@app.route('/api/pest_prediction', methods=['POST'])
def pest_prediction():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'prediction': 'Low risk of pests this season.'})

@app.route('/api/crop_rotation', methods=['GET'])
def crop_rotation():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT crop FROM recommendations WHERE username = ? ORDER BY timestamp DESC LIMIT 1", (session['user']['username'],))
    latest = c.fetchone()
    conn.close()
    plan = ['Legumes', 'Grains', 'Root Crops'] if latest else ['Start with Grains']
    return jsonify({'plan': plan})

@app.route('/api/fertilizer_optimize', methods=['POST'])
def fertilizer_optimize():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    land = data['land']
    soil = data['soil']
    crop = data['crop']
    n, p, k = random.randint(80, 120), random.randint(60, 100), random.randint(100, 150)
    return jsonify({'npk': f"{n}-{p}-{k}", 'total': land * (n + p + k) / 100})

@app.route('/api/previous_recommendations', methods=['GET'])
def previous_recommendations():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM recommendations WHERE username = ? ORDER BY timestamp DESC LIMIT 5", conn, params=(session['user']['username'],))
    conn.close()
    return jsonify(df.to_dict('records'))

@app.route('/api/sustainability_log', methods=['POST'])
def sustainability_log():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    score = calculate_sustainability_score(data['water'], data['fertilizer'], data['rotation'])
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO sustainability_scores (username, timestamp, water_score, fertilizer_use, rotation, score) VALUES (?, ?, ?, ?, ?, ?)",
              (session['user']['username'], datetime.now().strftime("%Y-%m-%d"), data['water'], data['fertilizer'], data['rotation'], score))
    conn.commit()
    conn.close()
    return jsonify({'score': score})

@app.route('/api/sustainability_history', methods=['GET'])
def sustainability_history():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM sustainability_scores WHERE username = ? ORDER BY timestamp ASC", conn, params=(session['user']['username'],))
    conn.close()
    return jsonify(df.to_dict('records'))

@app.route('/api/farm_map_save', methods=['POST'])
def farm_map_save():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO farm_maps (username, farm_name, map_data, created_at, updated_at) VALUES (?, ?, ?, ?, ?)""",
              (session['user']['username'], session['user']['farm_name'], json.dumps(data['map_data']),
               datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/farm_map_load', methods=['GET'])
def farm_map_load():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT map_data FROM farm_maps WHERE username = ? ORDER BY updated_at DESC LIMIT 1", (session['user']['username'],))
    result = c.fetchone()
    conn.close()
    return jsonify({'map_data': json.loads(result[0]) if result else {}})

@app.route('/api/community_share', methods=['POST'])
def community_share():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO community_insights (username, crop_type, yield_data, market_price, sustainability_practice, region, season, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (session['user']['username'], data['crop'], data['yield'], data['price'], data['practice'], data['region'], data['season'],
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/community_insights', methods=['GET'])
def community_insights():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""SELECT crop_type, AVG(yield_data) as avg_yield, COUNT(*) as count FROM community_insights GROUP BY crop_type""", conn)
    conn.close()
    return jsonify(df.to_dict('records'))

@app.route('/api/market_forecast', methods=['POST'])
def market_forecast():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    crop = data['crop']
    months = int(data['period'].split()[0])
    forecasts = []
    price = random.randint(2000, 3500)
    for i in range(months):
        price *= (1 + random.uniform(-0.1, 0.15))
        forecasts.append({'month': f"Month {i+1}", 'price': round(price), 'confidence': 0.8 - i*0.05})
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for f in forecasts:
        c.execute("INSERT INTO market_forecasts (username, crop, predicted_price, confidence_score, forecast_date, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (session['user']['username'], crop, f['price'], f['confidence'], f['month'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({'forecasts': forecasts})

@app.route('/api/chat', methods=['POST'])
def chat():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    query = data['query']
    response = generate_chatbot_response(query)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    c.execute("INSERT INTO chatbot_sessions (username, session_id, query, response, timestamp) VALUES (?, ?, ?, ?, ?)",
              (session['user']['username'], session_id, query, response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({'response': response})

@app.route('/api/offline_sync', methods=['POST'])
def offline_sync():
    if not session.get('user'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'synced': True})

if __name__ == '__main__':
    app.run(debug=True)