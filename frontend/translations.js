/* ══════════════════════════════════════════════════
   AgriSmart AI — Multilingual Translation Engine
   Supports: en, hi, kn, te, ta, ml, bn, gu, mr, pa, or
   ══════════════════════════════════════════════════ */

const TRANSLATIONS = {

// ═══════════════════════════════════════
//  ENGLISH (base)
// ═══════════════════════════════════════
en: {
    // Auth
    "auth.appName": "AgriSmart AI",
    "auth.tagline": "Smart Sustainable Farming",
    "auth.createAccount": "Create Account",
    "auth.login": "Login",
    "auth.yourName": "Your Name *",
    "auth.farmName": "Farm Name *",
    "auth.phone": "Phone",
    "auth.location": "Location",
    "auth.getStarted": "Get Started",
    "auth.phoneNumber": "Phone Number",
    "auth.password": "Password",
    "auth.loginBtn": "Login",
    "auth.namePlaceholder": "Enter your name",
    "auth.farmPlaceholder": "e.g. Green Valley Farm",
    "auth.phonePlaceholder": "Phone number",
    "auth.locationPlaceholder": "Village / City",
    "auth.loginPhonePlaceholder": "Enter phone",

    // Sidebar
    "nav.dashboard": "Dashboard",
    "nav.farmSetup": "Farm Setup",
    "nav.recommendations": "AI Recommendations",
    "nav.cropPlanner": "Crop Planner",
    "nav.fertilizer": "Fertilizer Calculator",
    "nav.farmMap": "Farm Map",
    "nav.sustainability": "Sustainability",
    "nav.community": "Community",
    "nav.market": "Market Forecast",
    "nav.chatbot": "AI Assistant",
    "nav.weather": "Weather",
    "nav.soilAnalysis": "Soil Analysis",
    "nav.pestPrediction": "Pest Prediction",
    "nav.history": "My History",
    "nav.offline": "Offline Mode",
    "nav.settings": "Settings",
    "nav.logout": "Logout",
    "nav.smartFarming": "Smart Farming",

    // Mobile Nav
    "mob.menu": "Menu",
    "mob.home": "Home",
    "mob.ai": "AI",
    "mob.chat": "Chat",
    "mob.profile": "Profile",

    // Dashboard
    "dash.goodMorning": "Good Morning,",
    "dash.goodAfternoon": "Good Afternoon,",
    "dash.goodEvening": "Good Evening,",
    "dash.farmSize": "Farm Size",
    "dash.sustainability": "Sustainability",
    "dash.recommendations": "Recommendations",
    "dash.farmers": "Farmers",
    "dash.quickActions": "Quick Actions",
    "dash.setupFarm": "Set Up Farm",
    "dash.setupFarmDesc": "Enter farm details for personalized AI advice",
    "dash.aiRec": "AI Recommendations",
    "dash.aiRecDesc": "Get smart crop suggestions based on your farm",
    "dash.cropRotation": "Crop Rotation Planner",
    "dash.cropRotationDesc": "Plan seasonal rotations for better yields",
    "dash.fertCalc": "Fertilizer Calculator",
    "dash.fertCalcDesc": "Calculate optimal NPK requirements",
    "dash.farmMap": "Farm Map",
    "dash.farmMapDesc": "Interactive map with soil zones & risks",
    "dash.exploreMore": "Explore More",
    "dash.marketForecast": "Market Forecast",
    "dash.communityLabel": "Community",
    "dash.weatherLabel": "Weather",
    "dash.aiChat": "AI Chat",
    "dash.sustainLabel": "Sustainability",
    "dash.pestAlert": "Pest Alert",
    "dash.howToUse": "📋 How to Use This App",
    "dash.step1Title": "Enter Farm Details",
    "dash.step1Desc": "Add your soil type, farm size, and location",
    "dash.step2Title": "Get AI Recommendations",
    "dash.step2Desc": "4 AI agents analyze your data for the best crops",
    "dash.step3Title": "Plan Your Season",
    "dash.step3Desc": "Use rotation planner, fertilizer calc & market insights",
    "dash.step4Title": "Track & Improve",
    "dash.step4Desc": "Log sustainability data and learn from community",

    // Farm Setup
    "setup.title": "Farm Setup",
    "setup.desc": "Enter your farm details for personalized recommendations",
    "setup.locationSettings": "Location Settings",
    "setup.default": "Default (Bangalore)",
    "setup.coordinates": "Coordinates",
    "setup.cityName": "City Name",
    "setup.latitude": "Latitude",
    "setup.longitude": "Longitude",
    "setup.city": "City",
    "setup.cityPlaceholder": "e.g. Bangalore, India",
    "setup.farmDetails": "Farm Details",
    "setup.farmSizeLabel": "Farm Size",
    "setup.cropPreference": "Crop Preference",
    "setup.soilType": "Soil Type",
    "setup.soilClimate": "Soil & Climate Parameters",
    "setup.nitrogen": "Nitrogen (N)",
    "setup.phosphorus": "Phosphorus (P)",
    "setup.potassium": "Potassium (K)",
    "setup.temperature": "Temperature °C",
    "setup.humidity": "Humidity %",
    "setup.phLevel": "pH Level",
    "setup.rainfall": "Rainfall (mm)",
    "setup.saveFarm": "Save Farm Details",
    "setup.grains": "🌾 Grains (Wheat, Rice, Corn)",
    "setup.vegetables": "🥬 Vegetables",
    "setup.fruits": "🍎 Fruits",
    "setup.hectares": "Hectares",
    "setup.cents": "Cents",
    "setup.acres": "Acres",
    "setup.loamy": "Loamy (Best for most crops)",
    "setup.sandy": "Sandy",
    "setup.clay": "Clay",
    "setup.black": "Black / Cotton soil",
    "setup.red": "Red soil",
    "setup.silty": "Silty",

    // AI Recommendations
    "rec.title": "AI Recommendations",
    "rec.desc": "Smart crop suggestions based on your farm data",
    "rec.regenerate": "Regenerate",
    "rec.noRec": "No Recommendations Yet",
    "rec.noRecDesc": "Set up your farm details first, then generate AI recommendations.",
    "rec.generateNow": "Generate Now",

    // Crop Rotation
    "rot.title": "Crop Rotation Planner",
    "rot.desc": "Plan sustainable rotations for better yields and soil health",
    "rot.currentCrop": "Current Crop",
    "rot.generatePlan": "Generate Rotation Plan",
    "rot.timeline": "Rotation Timeline",

    // Fertilizer
    "fert.title": "Fertilizer Calculator",
    "fert.desc": "Calculate exact NPK requirements for your farm",
    "fert.farmDetails": "Farm Details",
    "fert.soilType": "Soil Type",
    "fert.crop": "Crop",
    "fert.landSize": "Land Size (ha)",
    "fert.calculate": "Calculate",
    "fert.nutrientBreakdown": "Nutrient Breakdown",

    // Farm Map
    "map.title": "Interactive Farm Map",
    "map.desc": "Visualize soil zones, risk areas, and get location-specific advice",
    "map.settings": "Map Settings",
    "map.create": "Create Map",
    "map.loadSaved": "Load Saved",
    "map.saveMap": "Save Map",
    "map.legend": "Legend",
    "map.claySoil": "Clay Soil",
    "map.sandySoil": "Sandy Soil",
    "map.loamySoil": "Loamy Soil",
    "map.erosionRisk": "Erosion Risk",
    "map.waterlogging": "Waterlogging",
    "map.locationRecs": "Location-Specific Recommendations",

    // Sustainability
    "sust.title": "Sustainability Tracker",
    "sust.desc": "Monitor and improve your environmental impact",
    "sust.logPractices": "Log Season Practices",
    "sust.waterUsage": "Water Usage (ML/ha)",
    "sust.fertilizerUse": "Fertilizer (tons/ha)",
    "sust.cropRotation": "Crop Rotation?",
    "sust.yesRotation": "Yes, rotation practiced",
    "sust.noRotation": "No rotation this season",
    "sust.logData": "Log Data",
    "sust.scoreOverTime": "Score Over Time",
    "sust.improvementTips": "Improvement Tips",
    "sust.logFirst": "Log your data to get personalized sustainability tips.",

    // Community
    "comm.title": "Community Insights",
    "comm.desc": "Share data anonymously and learn from other farmers",
    "comm.shareData": "Share Your Data (Anonymous)",
    "comm.shareDesc": "Help fellow farmers by sharing your yield and price data.",
    "comm.crop": "Crop",
    "comm.yield": "Yield (tons/ha)",
    "comm.marketPrice": "Market Price (₹/ton)",
    "comm.region": "Region",
    "comm.season": "Season",
    "comm.practice": "Practice",
    "comm.shareBtn": "Share Data",
    "comm.regionalInsights": "Regional Insights",
    "comm.avgYield": "Avg Yield (t/ha)",
    "comm.avgPrice": "Avg Price (per quintal)",
    "comm.topPractices": "Top Practices from Farmers",
    "comm.north": "North",
    "comm.south": "South",
    "comm.east": "East",
    "comm.west": "West",
    "comm.central": "Central",

    // Market
    "mkt.title": "Market Forecast",
    "mkt.desc": "AI-powered price predictions and market insights",
    "mkt.forecastSettings": "Forecast Settings",
    "mkt.crop": "Crop",
    "mkt.period": "Period",
    "mkt.months3": "3 Months",
    "mkt.months6": "6 Months",
    "mkt.months12": "12 Months",
    "mkt.generate": "Generate Forecast",
    "mkt.priceForecast": "Price Forecast",
    "mkt.insights": "Market Insights",
    "mkt.insightsPlaceholder": "Generate a forecast to see insights and recommendations.",

    // AI Chatbot
    "chat.title": "AI Farming Assistant",
    "chat.desc": "Ask any farming question and get instant answers",
    "chat.welcome": "Hello! I'm your AI farming assistant 🌾. Ask me about crops, soil, weather, pests, fertilizers, or any farming topic!",
    "chat.placeholder": "Ask a farming question...",

    // Weather
    "weather.title": "Weather Intelligence",
    "weather.desc": "Real-time weather with agricultural risk assessments",
    "weather.location": "Location",
    "weather.cropType": "Crop Type",
    "weather.getForecast": "Get Forecast",
    "weather.7day": "7-Day Forecast",

    // Soil Analysis
    "soil.title": "Soil Analysis",
    "soil.desc": "Upload a photo for AI analysis or select manually",
    "soil.uploadTitle": "📸 Upload Soil Photo",
    "soil.uploadDesc": "Click or drag a soil photo here",
    "soil.uploadHint": "JPG, PNG — Clear close-up works best",
    "soil.analyze": "Analyze Soil",
    "soil.manualTitle": "📝 Manual Selection",
    "soil.loamy": "Loamy",
    "soil.loamyDesc": "Best for most crops. Good drainage.",
    "soil.sandy": "Sandy",
    "soil.sandyDesc": "Drains fast. Good for root crops.",
    "soil.clay": "Clay",
    "soil.clayDesc": "Holds water. Good for rice, wheat.",
    "soil.black": "Black",
    "soil.blackDesc": "Rich in minerals. Best for cotton.",
    "soil.red": "Red",
    "soil.redDesc": "Iron-rich. Good for pulses.",

    // Pest Prediction
    "pest.title": "Pest & Disease Prediction",
    "pest.desc": "AI early-warning system for pest outbreaks",
    "pest.conditions": "Farm Conditions",
    "pest.crop": "Crop",
    "pest.soilType": "Soil Type",
    "pest.temperature": "Temperature °C",
    "pest.humidity": "Humidity %",
    "pest.rainfall": "Rainfall (mm)",
    "pest.analyze": "Analyze Pest Risk",

    // History
    "hist.title": "My Recommendations",
    "hist.desc": "View previous recommendations and farming history",
    "hist.export": "Export CSV",
    "hist.noData": "No recommendations yet. Use AI Recommendations to get started!",
    "hist.analytics": "Analytics",

    // Offline
    "offline.title": "Offline Mode",
    "offline.desc": "Use the app without internet. Data syncs automatically.",
    "offline.connectionStatus": "Connection Status",
    "offline.online": "You are online — All features available",
    "offline.offlineMsg": "You're offline. Changes will sync when connection is restored.",
    "offline.offlineData": "Offline Data",
    "offline.offlineInfo": "When offline, recommendations use saved data. Unsynced entries upload when you reconnect.",
    "offline.savedRecs": "Saved recommendations",
    "offline.pendingSync": "Pending sync",
    "offline.syncNow": "Sync Now",

    // Profile & Settings
    "profile.title": "Profile & Settings",
    "profile.desc": "Manage profile, view history, and configure app settings",
    "profile.profileTab": "Profile",
    "profile.farmHistTab": "Farm History",
    "profile.settingsTab": "Settings",
    "profile.personalInfo": "Personal Information",
    "profile.farmerName": "Farmer Name",
    "profile.farmName": "Farm Name",
    "profile.email": "Email (Optional)",
    "profile.location": "Location",
    "profile.experience": "Experience Level",
    "profile.farmSize": "Farm Size (hectares)",
    "profile.regionLabel": "Region",
    "profile.saveProfile": "Save Profile",
    "profile.recentRecs": "Recent Recommendations",
    "profile.noRecs": "No recommendations yet.",
    "profile.sustainHistory": "Sustainability Score History",
    "profile.langVoice": "Language & Voice",
    "profile.prefLang": "Preferred Language",
    "profile.voiceInterface": "Voice Interface",
    "profile.enabled": "Enabled",
    "profile.disabled": "Disabled",
    "profile.notifications": "Notifications",
    "profile.weatherAlerts": "Weather Alerts",
    "profile.pestWarnings": "Pest Warnings",
    "profile.marketUpdates": "Market Price Updates",
    "profile.dataManagement": "Data Management",
    "profile.exportJSON": "Export Data (JSON)",
    "profile.exportCSV": "Export Recommendations (CSV)",
    "profile.account": "Account",
    "profile.beginner": "Beginner",
    "profile.intermediate": "Intermediate",
    "profile.advanced": "Advanced",
    "profile.expert": "Expert",

    // Loading
    "loading.processing": "Processing...",
    "loading.aiAnalyzing": "AI agents are analyzing your data",

    // Misc
    "offline.banner": "You're offline. Changes will sync when connection is restored.",
},

// ═══════════════════════════════════════
//  HINDI
// ═══════════════════════════════════════
hi: {
    "auth.appName": "एग्रीस्मार्ट AI",
    "auth.tagline": "स्मार्ट टिकाऊ खेती",
    "auth.createAccount": "खाता बनाएं",
    "auth.login": "लॉगिन",
    "auth.yourName": "आपका नाम *",
    "auth.farmName": "खेत का नाम *",
    "auth.phone": "फ़ोन",
    "auth.location": "स्थान",
    "auth.getStarted": "शुरू करें",
    "auth.phoneNumber": "फ़ोन नंबर",
    "auth.password": "पासवर्ड",
    "auth.loginBtn": "लॉगिन",
    "auth.namePlaceholder": "अपना नाम दर्ज करें",
    "auth.farmPlaceholder": "जैसे हरी घाटी फार्म",
    "auth.phonePlaceholder": "फ़ोन नंबर",
    "auth.locationPlaceholder": "गाँव / शहर",
    "auth.loginPhonePlaceholder": "फ़ोन दर्ज करें",

    "nav.dashboard": "डैशबोर्ड",
    "nav.farmSetup": "खेत सेटअप",
    "nav.recommendations": "AI सुझाव",
    "nav.cropPlanner": "फसल योजना",
    "nav.fertilizer": "उर्वरक कैलकुलेटर",
    "nav.farmMap": "खेत का नक्शा",
    "nav.sustainability": "सतत विकास",
    "nav.community": "समुदाय",
    "nav.market": "बाज़ार पूर्वानुमान",
    "nav.chatbot": "AI सहायक",
    "nav.weather": "मौसम",
    "nav.soilAnalysis": "मिट्टी विश्लेषण",
    "nav.pestPrediction": "कीट पूर्वानुमान",
    "nav.history": "मेरा इतिहास",
    "nav.offline": "ऑफ़लाइन मोड",
    "nav.settings": "सेटिंग्स",
    "nav.logout": "लॉगआउट",
    "nav.smartFarming": "स्मार्ट खेती",

    "mob.menu": "मेनू",
    "mob.home": "होम",
    "mob.ai": "AI",
    "mob.chat": "चैट",
    "mob.profile": "प्रोफ़ाइल",

    "dash.goodMorning": "सुप्रभात,",
    "dash.goodAfternoon": "नमस्कार,",
    "dash.goodEvening": "शुभ संध्या,",
    "dash.farmSize": "खेत का आकार",
    "dash.sustainability": "सतत विकास",
    "dash.recommendations": "सुझाव",
    "dash.farmers": "किसान",
    "dash.quickActions": "त्वरित कार्य",
    "dash.setupFarm": "खेत सेटअप करें",
    "dash.setupFarmDesc": "व्यक्तिगत AI सलाह के लिए खेत का विवरण दर्ज करें",
    "dash.aiRec": "AI सुझाव",
    "dash.aiRecDesc": "अपने खेत के आधार पर स्मार्ट फसल सुझाव पाएं",
    "dash.cropRotation": "फसल चक्र योजना",
    "dash.cropRotationDesc": "बेहतर उपज के लिए मौसमी चक्र की योजना बनाएं",
    "dash.fertCalc": "उर्वरक कैलकुलेटर",
    "dash.fertCalcDesc": "इष्टतम NPK आवश्यकताओं की गणना करें",
    "dash.farmMap": "खेत का नक्शा",
    "dash.farmMapDesc": "मिट्टी क्षेत्र और जोखिम के साथ इंटरैक्टिव मानचित्र",
    "dash.exploreMore": "और जानें",
    "dash.marketForecast": "बाज़ार पूर्वानुमान",
    "dash.communityLabel": "समुदाय",
    "dash.weatherLabel": "मौसम",
    "dash.aiChat": "AI चैट",
    "dash.sustainLabel": "सतत विकास",
    "dash.pestAlert": "कीट चेतावनी",
    "dash.howToUse": "📋 ऐप का उपयोग कैसे करें",
    "dash.step1Title": "खेत का विवरण दर्ज करें",
    "dash.step1Desc": "अपनी मिट्टी का प्रकार, खेत का आकार और स्थान जोड़ें",
    "dash.step2Title": "AI सुझाव पाएं",
    "dash.step2Desc": "4 AI एजेंट सर्वोत्तम फसलों के लिए आपके डेटा का विश्लेषण करते हैं",
    "dash.step3Title": "मौसम की योजना बनाएं",
    "dash.step3Desc": "फसल चक्र, उर्वरक कैलकुलेटर और बाज़ार जानकारी का उपयोग करें",
    "dash.step4Title": "ट्रैक करें और सुधारें",
    "dash.step4Desc": "सतत विकास डेटा लॉग करें और समुदाय से सीखें",

    "setup.title": "खेत सेटअप",
    "setup.desc": "व्यक्तिगत सुझावों के लिए अपने खेत का विवरण दर्ज करें",
    "setup.locationSettings": "स्थान सेटिंग्स",
    "setup.default": "डिफ़ॉल्ट (बैंगलोर)",
    "setup.coordinates": "निर्देशांक",
    "setup.cityName": "शहर का नाम",
    "setup.latitude": "अक्षांश",
    "setup.longitude": "देशांतर",
    "setup.city": "शहर",
    "setup.cityPlaceholder": "जैसे बैंगलोर, भारत",
    "setup.farmDetails": "खेत विवरण",
    "setup.farmSizeLabel": "खेत का आकार",
    "setup.cropPreference": "फसल वरीयता",
    "setup.soilType": "मिट्टी का प्रकार",
    "setup.soilClimate": "मिट्टी और जलवायु पैरामीटर",
    "setup.nitrogen": "नाइट्रोजन (N)",
    "setup.phosphorus": "फॉस्फोरस (P)",
    "setup.potassium": "पोटैशियम (K)",
    "setup.temperature": "तापमान °C",
    "setup.humidity": "आर्द्रता %",
    "setup.phLevel": "pH स्तर",
    "setup.rainfall": "वर्षा (मिमी)",
    "setup.saveFarm": "खेत विवरण सहेजें",
    "setup.grains": "🌾 अनाज (गेहूँ, चावल, मक्का)",
    "setup.vegetables": "🥬 सब्ज़ियाँ",
    "setup.fruits": "🍎 फल",

    "rec.title": "AI सुझाव",
    "rec.desc": "आपके खेत के डेटा पर आधारित स्मार्ट फसल सुझाव",
    "rec.regenerate": "फिर से बनाएं",
    "rec.noRec": "अभी तक कोई सुझाव नहीं",
    "rec.noRecDesc": "पहले अपने खेत का विवरण सेट करें, फिर AI सुझाव बनाएं।",
    "rec.generateNow": "अभी बनाएं",

    "rot.title": "फसल चक्र योजना",
    "rot.desc": "बेहतर उपज और मिट्टी स्वास्थ्य के लिए टिकाऊ चक्र की योजना",
    "rot.currentCrop": "वर्तमान फसल",
    "rot.generatePlan": "चक्र योजना बनाएं",
    "rot.timeline": "चक्र समयरेखा",

    "fert.title": "उर्वरक कैलकुलेटर",
    "fert.desc": "अपने खेत के लिए सटीक NPK आवश्यकता की गणना करें",
    "fert.farmDetails": "खेत विवरण",
    "fert.soilType": "मिट्टी का प्रकार",
    "fert.crop": "फसल",
    "fert.landSize": "भूमि आकार (हेक्टेयर)",
    "fert.calculate": "गणना करें",
    "fert.nutrientBreakdown": "पोषक तत्व विश्लेषण",

    "map.title": "इंटरैक्टिव खेत का नक्शा",
    "map.desc": "मिट्टी क्षेत्र, जोखिम क्षेत्र देखें और स्थान-विशिष्ट सलाह पाएं",
    "map.settings": "नक्शा सेटिंग्स",
    "map.create": "नक्शा बनाएं",
    "map.loadSaved": "सहेजा हुआ लोड करें",
    "map.saveMap": "नक्शा सहेजें",
    "map.legend": "लेजेंड",
    "map.claySoil": "चिकनी मिट्टी",
    "map.sandySoil": "रेतीली मिट्टी",
    "map.loamySoil": "दोमट मिट्टी",
    "map.erosionRisk": "कटाव जोखिम",
    "map.waterlogging": "जलभराव",
    "map.locationRecs": "स्थान-विशिष्ट सुझाव",

    "sust.title": "सतत विकास ट्रैकर",
    "sust.desc": "अपने पर्यावरणीय प्रभाव की निगरानी और सुधार करें",
    "sust.logPractices": "मौसम प्रथाओं को लॉग करें",
    "sust.waterUsage": "पानी का उपयोग (ML/हेक्टेयर)",
    "sust.fertilizerUse": "उर्वरक (टन/हेक्टेयर)",
    "sust.cropRotation": "फसल चक्र?",
    "sust.yesRotation": "हाँ, चक्र अपनाया",
    "sust.noRotation": "इस मौसम चक्र नहीं",
    "sust.logData": "डेटा लॉग करें",
    "sust.scoreOverTime": "समय के साथ स्कोर",
    "sust.improvementTips": "सुधार सुझाव",
    "sust.logFirst": "व्यक्तिगत सतत विकास सुझाव पाने के लिए अपना डेटा लॉग करें।",

    "comm.title": "समुदाय जानकारी",
    "comm.desc": "गुमनाम रूप से डेटा साझा करें और अन्य किसानों से सीखें",
    "comm.shareData": "अपना डेटा साझा करें (गुमनाम)",
    "comm.shareDesc": "अपनी उपज और मूल्य डेटा साझा करके साथी किसानों की मदद करें।",
    "comm.crop": "फसल",
    "comm.yield": "उपज (टन/हेक्टेयर)",
    "comm.marketPrice": "बाज़ार मूल्य (₹/टन)",
    "comm.region": "क्षेत्र",
    "comm.season": "मौसम",
    "comm.practice": "प्रथा",
    "comm.shareBtn": "डेटा साझा करें",
    "comm.regionalInsights": "क्षेत्रीय जानकारी",
    "comm.avgYield": "औसत उपज (टन/हेक्टेयर)",
    "comm.avgPrice": "औसत मूल्य (प्रति क्विंटल)",
    "comm.topPractices": "किसानों की शीर्ष प्रथाएँ",

    "mkt.title": "बाज़ार पूर्वानुमान",
    "mkt.desc": "AI-संचालित मूल्य पूर्वानुमान और बाज़ार जानकारी",
    "mkt.forecastSettings": "पूर्वानुमान सेटिंग्स",
    "mkt.crop": "फसल",
    "mkt.period": "अवधि",
    "mkt.months3": "3 महीने",
    "mkt.months6": "6 महीने",
    "mkt.months12": "12 महीने",
    "mkt.generate": "पूर्वानुमान बनाएं",
    "mkt.priceForecast": "मूल्य पूर्वानुमान",
    "mkt.insights": "बाज़ार जानकारी",
    "mkt.insightsPlaceholder": "जानकारी और सुझाव देखने के लिए पूर्वानुमान बनाएं।",

    "chat.title": "AI खेती सहायक",
    "chat.desc": "कोई भी खेती का सवाल पूछें और तुरंत जवाब पाएं",
    "chat.welcome": "नमस्ते! मैं आपका AI खेती सहायक हूँ 🌾। फसलों, मिट्टी, मौसम, कीट, उर्वरक या किसी भी खेती विषय पर पूछें!",
    "chat.placeholder": "खेती का सवाल पूछें...",

    "weather.title": "मौसम जानकारी",
    "weather.desc": "कृषि जोखिम मूल्यांकन के साथ रीयल-टाइम मौसम",
    "weather.location": "स्थान",
    "weather.cropType": "फसल का प्रकार",
    "weather.getForecast": "पूर्वानुमान प्राप्त करें",
    "weather.7day": "7-दिन का पूर्वानुमान",

    "soil.title": "मिट्टी विश्लेषण",
    "soil.desc": "AI विश्लेषण के लिए फ़ोटो अपलोड करें या मैन्युअल चुनें",
    "soil.uploadTitle": "📸 मिट्टी की फ़ोटो अपलोड करें",
    "soil.uploadDesc": "यहाँ क्लिक करें या मिट्टी की फ़ोटो खींचें",
    "soil.uploadHint": "JPG, PNG — स्पष्ट क्लोज़-अप सबसे अच्छा",
    "soil.analyze": "मिट्टी का विश्लेषण करें",
    "soil.manualTitle": "📝 मैन्युअल चयन",
    "soil.loamy": "दोमट",
    "soil.loamyDesc": "अधिकतर फसलों के लिए सर्वश्रेष्ठ। अच्छी जल निकासी।",
    "soil.sandy": "रेतीली",
    "soil.sandyDesc": "तेज़ जल निकासी। जड़ फसलों के लिए अच्छी।",
    "soil.clay": "चिकनी",
    "soil.clayDesc": "पानी रोकती है। चावल, गेहूँ के लिए अच्छी।",
    "soil.black": "काली",
    "soil.blackDesc": "खनिजों से भरपूर। कपास के लिए सर्वश्रेष्ठ।",
    "soil.red": "लाल",
    "soil.redDesc": "लौह-समृद्ध। दालों के लिए अच्छी।",

    "pest.title": "कीट एवं रोग पूर्वानुमान",
    "pest.desc": "कीट प्रकोप के लिए AI प्रारंभिक चेतावनी प्रणाली",
    "pest.conditions": "खेत की स्थिति",
    "pest.crop": "फसल",
    "pest.soilType": "मिट्टी का प्रकार",
    "pest.temperature": "तापमान °C",
    "pest.humidity": "आर्द्रता %",
    "pest.rainfall": "वर्षा (मिमी)",
    "pest.analyze": "कीट जोखिम विश्लेषण",

    "hist.title": "मेरे सुझाव",
    "hist.desc": "पिछले सुझाव और खेती इतिहास देखें",
    "hist.export": "CSV डाउनलोड करें",
    "hist.noData": "अभी तक कोई सुझाव नहीं। शुरू करने के लिए AI सुझाव का उपयोग करें!",
    "hist.analytics": "विश्लेषण",

    "offline.title": "ऑफ़लाइन मोड",
    "offline.desc": "इंटरनेट के बिना ऐप का उपयोग करें। डेटा स्वचालित सिंक होता है।",
    "offline.connectionStatus": "कनेक्शन स्थिति",
    "offline.online": "आप ऑनलाइन हैं — सभी सुविधाएँ उपलब्ध",
    "offline.offlineData": "ऑफ़लाइन डेटा",
    "offline.offlineInfo": "ऑफ़लाइन होने पर, सुझाव सहेजे गए डेटा का उपयोग करते हैं।",
    "offline.savedRecs": "सहेजे गए सुझाव",
    "offline.pendingSync": "सिंक बाकी",
    "offline.syncNow": "अभी सिंक करें",

    "profile.title": "प्रोफ़ाइल और सेटिंग्स",
    "profile.desc": "प्रोफ़ाइल प्रबंधित करें, इतिहास देखें और ऐप सेटिंग्स कॉन्फ़िगर करें",
    "profile.profileTab": "प्रोफ़ाइल",
    "profile.farmHistTab": "खेती इतिहास",
    "profile.settingsTab": "सेटिंग्स",
    "profile.personalInfo": "व्यक्तिगत जानकारी",
    "profile.farmerName": "किसान का नाम",
    "profile.farmName": "खेत का नाम",
    "profile.email": "ईमेल (वैकल्पिक)",
    "profile.location": "स्थान",
    "profile.experience": "अनुभव स्तर",
    "profile.farmSize": "खेत का आकार (हेक्टेयर)",
    "profile.regionLabel": "क्षेत्र",
    "profile.saveProfile": "प्रोफ़ाइल सहेजें",
    "profile.langVoice": "भाषा और आवाज़",
    "profile.prefLang": "पसंदीदा भाषा",
    "profile.voiceInterface": "वॉइस इंटरफ़ेस",
    "profile.enabled": "चालू",
    "profile.disabled": "बंद",
    "profile.notifications": "सूचनाएँ",
    "profile.weatherAlerts": "मौसम चेतावनी",
    "profile.pestWarnings": "कीट चेतावनी",
    "profile.marketUpdates": "बाज़ार मूल्य अपडेट",
    "profile.dataManagement": "डेटा प्रबंधन",
    "profile.exportJSON": "डेटा निर्यात (JSON)",
    "profile.exportCSV": "सुझाव निर्यात (CSV)",
    "profile.account": "खाता",
    "profile.beginner": "शुरुआती",
    "profile.intermediate": "मध्यवर्ती",
    "profile.advanced": "उन्नत",
    "profile.expert": "विशेषज्ञ",

    "loading.processing": "प्रक्रिया हो रही है...",
    "loading.aiAnalyzing": "AI एजेंट आपके डेटा का विश्लेषण कर रहे हैं",
    "offline.banner": "आप ऑफ़लाइन हैं। कनेक्शन बहाल होने पर बदलाव सिंक होंगे।",
},

// ═══════════════════════════════════════
//  TELUGU
// ═══════════════════════════════════════
te: {
    "auth.appName": "ఆగ్రీస్మార్ట్ AI",
    "auth.tagline": "స్మార్ట్ సుస్థిర వ్యవసాయం",
    "auth.createAccount": "ఖాతా సృష్టించు",
    "auth.login": "లాగిన్",
    "auth.yourName": "మీ పేరు *",
    "auth.farmName": "పొలం పేరు *",
    "auth.phone": "ఫోన్",
    "auth.location": "ప్రదేశం",
    "auth.getStarted": "ప్రారంభించండి",
    "auth.phoneNumber": "ఫోన్ నంబర్",
    "auth.password": "పాస్‌వర్డ్",
    "auth.loginBtn": "లాగిన్",

    "nav.dashboard": "డాష్‌బోర్డ్",
    "nav.farmSetup": "పొలం సెటప్",
    "nav.recommendations": "AI సిఫార్సులు",
    "nav.cropPlanner": "పంట ప్లానర్",
    "nav.fertilizer": "ఎరువుల కాలిక్యులేటర్",
    "nav.farmMap": "పొలం మ్యాప్",
    "nav.sustainability": "సుస్థిరత",
    "nav.community": "సమాజం",
    "nav.market": "మార్కెట్ అంచనా",
    "nav.chatbot": "AI సహాయకుడు",
    "nav.weather": "వాతావరణం",
    "nav.soilAnalysis": "నేల విశ్లేషణ",
    "nav.pestPrediction": "పురుగుల అంచనా",
    "nav.history": "నా చరిత్ర",
    "nav.offline": "ఆఫ్‌లైన్ మోడ్",
    "nav.settings": "సెట్టింగ్‌లు",
    "nav.logout": "లాగ్‌అవుట్",
    "nav.smartFarming": "స్మార్ట్ వ్యవసాయం",

    "mob.menu": "మెనూ",
    "mob.home": "హోమ్",
    "mob.ai": "AI",
    "mob.chat": "చాట్",
    "mob.profile": "ప్రొఫైల్",

    "dash.goodMorning": "శుభోదయం,",
    "dash.goodAfternoon": "శుభ మధ్యాహ్నం,",
    "dash.goodEvening": "శుభ సాయంత్రం,",
    "dash.farmSize": "పొలం పరిమాణం",
    "dash.sustainability": "సుస్థిరత",
    "dash.recommendations": "సిఫార్సులు",
    "dash.farmers": "రైతులు",
    "dash.quickActions": "త్వరిత చర్యలు",
    "dash.setupFarm": "పొలం సెటప్ చేయండి",
    "dash.setupFarmDesc": "వ్యక్తిగత AI సలహా కోసం పొలం వివరాలు నమోదు చేయండి",
    "dash.aiRec": "AI సిఫార్సులు",
    "dash.aiRecDesc": "మీ పొలం ఆధారంగా స్మార్ట్ పంట సూచనలు పొందండి",
    "dash.howToUse": "📋 ఈ యాప్ ఎలా ఉపయోగించాలి",
    "dash.exploreMore": "మరింత అన్వేషించండి",

    "chat.title": "AI వ్యవసాయ సహాయకుడు",
    "chat.desc": "ఏదైనా వ్యవసాయ ప్రశ్న అడగండి మరియు తక్షణ సమాధానాలు పొందండి",
    "chat.welcome": "నమస్కారం! నేను మీ AI వ్యవసాయ సహాయకుడిని 🌾। పంటలు, నేల, వాతావరణం, పురుగులు, ఎరువులు లేదా ఏదైనా వ్యవసాయ అంశం గురించి అడగండి!",
    "chat.placeholder": "వ్యవసాయ ప్రశ్న అడగండి...",

    "loading.processing": "ప్రాసెస్ అవుతోంది...",
    "loading.aiAnalyzing": "AI ఏజెంట్లు మీ డేటాను విశ్లేషిస్తున్నారు",
},

// ═══════════════════════════════════════
//  KANNADA
// ═══════════════════════════════════════
kn: {
    "auth.appName": "ಆಗ್ರಿಸ್ಮಾರ್ಟ್ AI",
    "auth.tagline": "ಸ್ಮಾರ್ಟ್ ಸುಸ್ಥಿರ ಕೃಷಿ",
    "auth.createAccount": "ಖಾತೆ ರಚಿಸಿ",
    "auth.login": "ಲಾಗಿನ್",
    "auth.yourName": "ನಿಮ್ಮ ಹೆಸರು *",
    "auth.farmName": "ಹೊಲದ ಹೆಸರು *",
    "auth.phone": "ಫೋನ್",
    "auth.location": "ಸ್ಥಳ",
    "auth.getStarted": "ಪ್ರಾರಂಭಿಸಿ",

    "nav.dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    "nav.farmSetup": "ಹೊಲ ಸೆಟಪ್",
    "nav.recommendations": "AI ಶಿಫಾರಸುಗಳು",
    "nav.cropPlanner": "ಬೆಳೆ ಯೋಜಕ",
    "nav.fertilizer": "ಗೊಬ್ಬರ ಕ್ಯಾಲ್ಕುಲೇಟರ್",
    "nav.farmMap": "ಹೊಲದ ನಕ್ಷೆ",
    "nav.sustainability": "ಸುಸ್ಥಿರತೆ",
    "nav.community": "ಸಮುದಾಯ",
    "nav.market": "ಮಾರುಕಟ್ಟೆ ಮುನ್ಸೂಚನೆ",
    "nav.chatbot": "AI ಸಹಾಯಕ",
    "nav.weather": "ಹವಾಮಾನ",
    "nav.soilAnalysis": "ಮಣ್ಣು ವಿಶ್ಲೇಷಣೆ",
    "nav.pestPrediction": "ಕೀಟ ಮುನ್ಸೂಚನೆ",
    "nav.history": "ನನ್ನ ಇತಿಹಾಸ",
    "nav.offline": "ಆಫ್‌ಲೈನ್ ಮೋಡ್",
    "nav.settings": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
    "nav.logout": "ಲಾಗ್‌ಔಟ್",
    "nav.smartFarming": "ಸ್ಮಾರ್ಟ್ ಕೃಷಿ",

    "mob.menu": "ಮೆನು",
    "mob.home": "ಹೋಮ್",
    "mob.ai": "AI",
    "mob.chat": "ಚಾಟ್",
    "mob.profile": "ಪ್ರೊಫೈಲ್",

    "dash.goodMorning": "ಶುಭೋದಯ,",
    "dash.goodAfternoon": "ಶುಭ ಮಧ್ಯಾಹ್ನ,",
    "dash.goodEvening": "ಶುಭ ಸಂಜೆ,",
    "dash.farmSize": "ಹೊಲದ ಗಾತ್ರ",
    "dash.sustainability": "ಸುಸ್ಥಿರತೆ",
    "dash.recommendations": "ಶಿಫಾರಸುಗಳು",
    "dash.farmers": "ರೈತರು",
    "dash.quickActions": "ತ್ವರಿತ ಕಾರ್ಯಗಳು",
    "dash.exploreMore": "ಇನ್ನಷ್ಟು ಅನ್ವೇಷಿಸಿ",
    "dash.howToUse": "📋 ಈ ಅಪ್ಲಿಕೇಶನ್ ಹೇಗೆ ಬಳಸುವುದು",

    "chat.title": "AI ಕೃಷಿ ಸಹಾಯಕ",
    "chat.desc": "ಯಾವುದೇ ಕೃಷಿ ಪ್ರಶ್ನೆ ಕೇಳಿ ಮತ್ತು ತಕ್ಷಣ ಉತ್ತರ ಪಡೆಯಿರಿ",
    "chat.welcome": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ AI ಕೃಷಿ ಸಹಾಯಕ 🌾. ಬೆಳೆಗಳು, ಮಣ್ಣು, ಹವಾಮಾನ, ಕೀಟಗಳು, ಗೊಬ್ಬರ ಅಥವಾ ಯಾವುದೇ ಕೃಷಿ ವಿಷಯದ ಬಗ್ಗೆ ಕೇಳಿ!",
    "chat.placeholder": "ಕೃಷಿ ಪ್ರಶ್ನೆ ಕೇಳಿ...",

    "loading.processing": "ಪ್ರಕ್ರಿಯೆ ನಡೆಯುತ್ತಿದೆ...",
    "loading.aiAnalyzing": "AI ಏಜೆಂಟ್‌ಗಳು ನಿಮ್ಮ ಡೇಟಾವನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತಿದ್ದಾರೆ",
},

// ═══════════════════════════════════════
//  TAMIL
// ═══════════════════════════════════════
ta: {
    "auth.appName": "ஆக்ரிஸ்மார்ட் AI",
    "auth.tagline": "ஸ்மார்ட் நிலையான விவசாயம்",
    "auth.createAccount": "கணக்கை உருவாக்கு",
    "auth.login": "உள்நுழை",
    "auth.yourName": "உங்கள் பெயர் *",
    "auth.farmName": "பண்ணை பெயர் *",
    "auth.phone": "தொலைபேசி",
    "auth.location": "இடம்",
    "auth.getStarted": "தொடங்குங்கள்",

    "nav.dashboard": "டாஷ்போர்ட்",
    "nav.farmSetup": "பண்ணை அமைப்பு",
    "nav.recommendations": "AI பரிந்துரைகள்",
    "nav.cropPlanner": "பயிர் திட்டமிடல்",
    "nav.fertilizer": "உர கணிப்பான்",
    "nav.farmMap": "பண்ணை வரைபடம்",
    "nav.sustainability": "நிலைத்தன்மை",
    "nav.community": "சமூகம்",
    "nav.market": "சந்தை முன்னறிவிப்பு",
    "nav.chatbot": "AI உதவியாளர்",
    "nav.weather": "வானிலை",
    "nav.soilAnalysis": "மண் பகுப்பாய்வு",
    "nav.pestPrediction": "பூச்சி முன்னறிவிப்பு",
    "nav.history": "எனது வரலாறு",
    "nav.offline": "ஆஃப்லைன் பயன்முறை",
    "nav.settings": "அமைப்புகள்",
    "nav.logout": "வெளியேறு",
    "nav.smartFarming": "ஸ்மார்ட் விவசாயம்",

    "mob.menu": "மெனு",
    "mob.home": "முகப்பு",
    "mob.ai": "AI",
    "mob.chat": "அரட்டை",
    "mob.profile": "சுயவிவரம்",

    "dash.goodMorning": "காலை வணக்கம்,",
    "dash.goodAfternoon": "மதிய வணக்கம்,",
    "dash.goodEvening": "மாலை வணக்கம்,",
    "dash.farmSize": "பண்ணை அளவு",
    "dash.sustainability": "நிலைத்தன்மை",
    "dash.recommendations": "பரிந்துரைகள்",
    "dash.farmers": "விவசாயிகள்",
    "dash.quickActions": "விரைவு செயல்கள்",
    "dash.exploreMore": "மேலும் ஆராயுங்கள்",
    "dash.howToUse": "📋 இந்த ஆப்பை எவ்வாறு பயன்படுத்துவது",

    "chat.title": "AI விவசாய உதவியாளர்",
    "chat.desc": "எந்த விவசாய கேள்வியையும் கேளுங்கள்",
    "chat.welcome": "வணக்கம்! நான் உங்கள் AI விவசாய உதவியாளர் 🌾. பயிர்கள், மண், வானிலை, பூச்சிகள், உரங்கள் அல்லது எந்த விவசாய தலைப்பிலும் கேளுங்கள்!",
    "chat.placeholder": "விவசாய கேள்வி கேளுங்கள்...",

    "loading.processing": "செயலாக்கப்படுகிறது...",
    "loading.aiAnalyzing": "AI முகவர்கள் உங்கள் தரவை பகுப்பாய்வு செய்கிறார்கள்",
},

// ═══════════════════════════════════════
//  MALAYALAM
// ═══════════════════════════════════════
ml: {
    "auth.appName": "ആഗ്രിസ്മാർട്ട് AI",
    "auth.tagline": "സ്മാർട്ട് സുസ്ഥിര കൃഷി",
    "auth.createAccount": "അക്കൗണ്ട് സൃഷ്ടിക്കുക",
    "auth.login": "ലോഗിൻ",
    "auth.yourName": "നിങ്ങളുടെ പേര് *",
    "auth.farmName": "ഫാം പേര് *",

    "nav.dashboard": "ഡാഷ്ബോർഡ്",
    "nav.farmSetup": "ഫാം സെറ്റപ്പ്",
    "nav.recommendations": "AI ശുപാർശകൾ",
    "nav.cropPlanner": "വിള ആസൂത്രണം",
    "nav.fertilizer": "വളം കാൽക്കുലേറ്റർ",
    "nav.farmMap": "ഫാം മാപ്പ്",
    "nav.sustainability": "സുസ്ഥിരത",
    "nav.community": "സമൂഹം",
    "nav.market": "വിപണി പ്രവചനം",
    "nav.chatbot": "AI സഹായി",
    "nav.weather": "കാലാവസ്ഥ",
    "nav.soilAnalysis": "മണ്ണ് വിശകലനം",
    "nav.pestPrediction": "കീട പ്രവചനം",
    "nav.history": "എന്റെ ചരിത്രം",
    "nav.offline": "ഓഫ്‌ലൈൻ മോഡ്",
    "nav.settings": "ക്രമീകരണങ്ങൾ",
    "nav.logout": "ലോഗ്ഔട്ട്",
    "nav.smartFarming": "സ്മാർട്ട് കൃഷി",

    "dash.goodMorning": "സുപ്രഭാതം,",
    "dash.goodAfternoon": "ശുഭ ഉച്ച,",
    "dash.goodEvening": "ശുഭ സായാഹ്നം,",
    "dash.quickActions": "ദ്രുത പ്രവർത്തനങ്ങൾ",
    "dash.exploreMore": "കൂടുതൽ പര്യവേക്ഷിക്കൂ",

    "chat.title": "AI കൃഷി സഹായി",
    "chat.welcome": "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ AI കൃഷി സഹായിയാണ് 🌾. വിളകൾ, മണ്ണ്, കാലാവസ്ഥ, കീടങ്ങൾ, വളങ്ങൾ എന്നിവയെക്കുറിച്ച് ചോദിക്കൂ!",
    "chat.placeholder": "കൃഷി ചോദ്യം ചോദിക്കൂ...",

    "loading.processing": "പ്രോസസ്സ് ചെയ്യുന്നു...",
    "loading.aiAnalyzing": "AI ഏജന്റുകൾ നിങ്ങളുടെ ഡാറ്റ വിശകലനം ചെയ്യുന്നു",
},

// ═══════════════════════════════════════
//  BENGALI
// ═══════════════════════════════════════
bn: {
    "auth.appName": "এগ্রিস্মার্ট AI",
    "auth.tagline": "স্মার্ট টেকসই কৃষি",
    "auth.createAccount": "অ্যাকাউন্ট তৈরি করুন",
    "auth.login": "লগইন",
    "auth.yourName": "আপনার নাম *",
    "auth.farmName": "খামারের নাম *",

    "nav.dashboard": "ড্যাশবোর্ড",
    "nav.farmSetup": "খামার সেটআপ",
    "nav.recommendations": "AI সুপারিশ",
    "nav.cropPlanner": "ফসল পরিকল্পনা",
    "nav.fertilizer": "সার ক্যালকুলেটর",
    "nav.farmMap": "খামার মানচিত্র",
    "nav.sustainability": "স্থায়িত্ব",
    "nav.community": "সম্প্রদায়",
    "nav.market": "বাজার পূর্বাভাস",
    "nav.chatbot": "AI সহকারী",
    "nav.weather": "আবহাওয়া",
    "nav.soilAnalysis": "মাটি বিশ্লেষণ",
    "nav.pestPrediction": "কীটপতঙ্গ পূর্বাভাস",
    "nav.history": "আমার ইতিহাস",
    "nav.offline": "অফলাইন মোড",
    "nav.settings": "সেটিংস",
    "nav.logout": "লগআউট",
    "nav.smartFarming": "স্মার্ট কৃষি",

    "dash.goodMorning": "সুপ্রভাত,",
    "dash.goodAfternoon": "শুভ অপরাহ্ন,",
    "dash.goodEvening": "শুভ সন্ধ্যা,",
    "dash.quickActions": "দ্রুত কার্যক্রম",
    "dash.exploreMore": "আরও অন্বেষণ করুন",

    "chat.title": "AI কৃষি সহকারী",
    "chat.welcome": "নমস্কার! আমি আপনার AI কৃষি সহকারী 🌾। ফসল, মাটি, আবহাওয়া, কীটপতঙ্গ, সার বা যেকোনো কৃষি বিষয়ে জিজ্ঞাসা করুন!",
    "chat.placeholder": "কৃষি প্রশ্ন করুন...",

    "loading.processing": "প্রক্রিয়াকরণ হচ্ছে...",
    "loading.aiAnalyzing": "AI এজেন্টরা আপনার ডেটা বিশ্লেষণ করছে",
},

// ═══════════════════════════════════════
//  GUJARATI
// ═══════════════════════════════════════
gu: {
    "auth.appName": "એગ્રીસ્માર્ટ AI",
    "auth.tagline": "સ્માર્ટ ટકાઉ ખેતી",
    "auth.createAccount": "ખાતું બનાવો",
    "auth.login": "લૉગિન",
    "auth.yourName": "તમારું નામ *",
    "auth.farmName": "ખેતરનું નામ *",

    "nav.dashboard": "ડેશબોર્ડ",
    "nav.farmSetup": "ખેતર સેટઅપ",
    "nav.recommendations": "AI ભલામણો",
    "nav.cropPlanner": "પાક આયોજક",
    "nav.fertilizer": "ખાતર કેલ્ક્યુલેટર",
    "nav.farmMap": "ખેતર નકશો",
    "nav.sustainability": "ટકાઉપણું",
    "nav.community": "સમુદાય",
    "nav.market": "બજાર આગાહી",
    "nav.chatbot": "AI સહાયક",
    "nav.weather": "હવામાન",
    "nav.soilAnalysis": "માટી વિશ્લેષણ",
    "nav.pestPrediction": "જીવાત આગાહી",
    "nav.history": "મારો ઇતિહાસ",
    "nav.offline": "ઑફલાઇન મોડ",
    "nav.settings": "સેટિંગ્સ",
    "nav.logout": "લૉગઆઉટ",
    "nav.smartFarming": "સ્માર્ટ ખેતી",

    "dash.goodMorning": "સુપ્રભાત,",
    "dash.goodAfternoon": "શુભ બપોર,",
    "dash.goodEvening": "શુભ સાંજ,",
    "dash.quickActions": "ઝડપી ક્રિયાઓ",
    "dash.exploreMore": "વધુ અન્વેષણ કરો",

    "chat.title": "AI ખેતી સહાયક",
    "chat.welcome": "નમસ્તે! હું તમારો AI ખેતી સહાયક છું 🌾. પાક, માટી, હવામાન, જીવાત, ખાતર કે કોઈપણ ખેતી વિષય વિશે પૂછો!",
    "chat.placeholder": "ખેતી વિષયક પ્રશ્ન પૂછો...",

    "loading.processing": "પ્રક્રિયા ચાલી રહી છે...",
    "loading.aiAnalyzing": "AI એજન્ટો તમારા ડેટાનું વિશ્લેષણ કરી રહ્યા છે",
},

// ═══════════════════════════════════════
//  MARATHI
// ═══════════════════════════════════════
mr: {
    "auth.appName": "ॲग्रीस्मार्ट AI",
    "auth.tagline": "स्मार्ट शाश्वत शेती",
    "auth.createAccount": "खाते तयार करा",
    "auth.login": "लॉगिन",
    "auth.yourName": "तुमचे नाव *",
    "auth.farmName": "शेताचे नाव *",

    "nav.dashboard": "डॅशबोर्ड",
    "nav.farmSetup": "शेत सेटअप",
    "nav.recommendations": "AI शिफारसी",
    "nav.cropPlanner": "पीक नियोजक",
    "nav.fertilizer": "खत कॅल्क्युलेटर",
    "nav.farmMap": "शेत नकाशा",
    "nav.sustainability": "शाश्वतता",
    "nav.community": "समुदाय",
    "nav.market": "बाजार अंदाज",
    "nav.chatbot": "AI सहाय्यक",
    "nav.weather": "हवामान",
    "nav.soilAnalysis": "माती विश्लेषण",
    "nav.pestPrediction": "कीड अंदाज",
    "nav.history": "माझा इतिहास",
    "nav.offline": "ऑफलाइन मोड",
    "nav.settings": "सेटिंग्ज",
    "nav.logout": "लॉगआउट",
    "nav.smartFarming": "स्मार्ट शेती",

    "dash.goodMorning": "सुप्रभात,",
    "dash.goodAfternoon": "शुभ दुपार,",
    "dash.goodEvening": "शुभ संध्याकाळ,",
    "dash.quickActions": "जलद कृती",
    "dash.exploreMore": "अधिक शोधा",

    "chat.title": "AI शेती सहाय्यक",
    "chat.welcome": "नमस्कार! मी तुमचा AI शेती सहाय्यक आहे 🌾. पिके, माती, हवामान, कीटक, खते किंवा कोणत्याही शेती विषयावर विचारा!",
    "chat.placeholder": "शेती विषयक प्रश्न विचारा...",

    "loading.processing": "प्रक्रिया सुरू आहे...",
    "loading.aiAnalyzing": "AI एजंट तुमच्या डेटाचे विश्लेषण करत आहेत",
},

// ═══════════════════════════════════════
//  PUNJABI
// ═══════════════════════════════════════
pa: {
    "auth.appName": "ਐਗਰੀਸਮਾਰਟ AI",
    "auth.tagline": "ਸਮਾਰਟ ਟਿਕਾਊ ਖੇਤੀ",
    "auth.createAccount": "ਖਾਤਾ ਬਣਾਓ",
    "auth.login": "ਲਾਗਇਨ",
    "auth.yourName": "ਤੁਹਾਡਾ ਨਾਮ *",
    "auth.farmName": "ਖੇਤ ਦਾ ਨਾਮ *",

    "nav.dashboard": "ਡੈਸ਼ਬੋਰਡ",
    "nav.farmSetup": "ਖੇਤ ਸੈਟਅਪ",
    "nav.recommendations": "AI ਸਿਫਾਰਸ਼ਾਂ",
    "nav.cropPlanner": "ਫਸਲ ਯੋਜਨਾ",
    "nav.fertilizer": "ਖਾਦ ਕੈਲਕੁਲੇਟਰ",
    "nav.farmMap": "ਖੇਤ ਨਕਸ਼ਾ",
    "nav.sustainability": "ਟਿਕਾਊਪਣ",
    "nav.community": "ਭਾਈਚਾਰਾ",
    "nav.market": "ਮੰਡੀ ਅੰਦਾਜ਼ਾ",
    "nav.chatbot": "AI ਸਹਾਇਕ",
    "nav.weather": "ਮੌਸਮ",
    "nav.soilAnalysis": "ਮਿੱਟੀ ਵਿਸ਼ਲੇਸ਼ਣ",
    "nav.pestPrediction": "ਕੀੜੇ ਅੰਦਾਜ਼ਾ",
    "nav.history": "ਮੇਰਾ ਇਤਿਹਾਸ",
    "nav.offline": "ਆਫਲਾਈਨ ਮੋਡ",
    "nav.settings": "ਸੈਟਿੰਗਜ਼",
    "nav.logout": "ਲਾਗ ਆਊਟ",
    "nav.smartFarming": "ਸਮਾਰਟ ਖੇਤੀ",

    "dash.goodMorning": "ਸ਼ੁਭ ਸਵੇਰ,",
    "dash.goodAfternoon": "ਸ਼ੁਭ ਦੁਪਹਿਰ,",
    "dash.goodEvening": "ਸ਼ੁਭ ਸ਼ਾਮ,",
    "dash.quickActions": "ਤੁਰੰਤ ਕਾਰਵਾਈਆਂ",
    "dash.exploreMore": "ਹੋਰ ਖੋਜੋ",

    "chat.title": "AI ਖੇਤੀ ਸਹਾਇਕ",
    "chat.welcome": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡਾ AI ਖੇਤੀ ਸਹਾਇਕ ਹਾਂ 🌾. ਫਸਲਾਂ, ਮਿੱਟੀ, ਮੌਸਮ, ਕੀੜੇ, ਖਾਦ ਜਾਂ ਕਿਸੇ ਵੀ ਖੇਤੀ ਵਿਸ਼ੇ ਬਾਰੇ ਪੁੱਛੋ!",
    "chat.placeholder": "ਖੇਤੀ ਬਾਰੇ ਸਵਾਲ ਪੁੱਛੋ...",

    "loading.processing": "ਪ੍ਰੋਸੈਸ ਹੋ ਰਿਹਾ ਹੈ...",
    "loading.aiAnalyzing": "AI ਏਜੰਟ ਤੁਹਾਡੇ ਡੇਟਾ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਹੇ ਹਨ",
},

// ═══════════════════════════════════════
//  ODIA
// ═══════════════════════════════════════
or: {
    "auth.appName": "ଆଗ୍ରୀସ୍ମାର୍ଟ AI",
    "auth.tagline": "ସ୍ମାର୍ଟ ସ୍ଥାୟୀ ଚାଷ",
    "auth.createAccount": "ଆକାଉଣ୍ଟ ସୃଷ୍ଟି କରନ୍ତୁ",
    "auth.login": "ଲଗଇନ",
    "auth.yourName": "ଆପଣଙ୍କ ନାମ *",
    "auth.farmName": "ଜମି ନାମ *",

    "nav.dashboard": "ଡ୍ୟାସବୋର୍ଡ",
    "nav.farmSetup": "ଜମି ସେଟଅପ",
    "nav.recommendations": "AI ସୁପାରିଶ",
    "nav.cropPlanner": "ଫସଲ ଯୋଜନା",
    "nav.fertilizer": "ସାର କ୍ୟାଲକୁଲେଟର",
    "nav.farmMap": "ଜମି ମ୍ୟାପ",
    "nav.sustainability": "ସ୍ଥାୟୀତ୍ୱ",
    "nav.community": "ସମୁଦାୟ",
    "nav.market": "ବଜାର ପୂର୍ବାନୁମାନ",
    "nav.chatbot": "AI ସହାୟକ",
    "nav.weather": "ପାଣିପାଗ",
    "nav.soilAnalysis": "ମାଟି ବିଶ୍ଳେଷଣ",
    "nav.pestPrediction": "କୀଟ ପୂର୍ବାନୁମାନ",
    "nav.history": "ମୋ ଇତିହାସ",
    "nav.offline": "ଅଫଲାଇନ ମୋଡ",
    "nav.settings": "ସେଟିଙ୍ଗ",
    "nav.logout": "ଲଗଆଉଟ",
    "nav.smartFarming": "ସ୍ମାର୍ଟ ଚାଷ",

    "dash.goodMorning": "ଶୁଭ ସକାଳ,",
    "dash.goodAfternoon": "ଶୁଭ ଅପରାହ୍ନ,",
    "dash.goodEvening": "ଶୁଭ ସନ୍ଧ୍ୟା,",
    "dash.quickActions": "ଦ୍ରୁତ କାର୍ଯ୍ୟ",
    "dash.exploreMore": "ଅଧିକ ଅନ୍ୱେଷଣ କରନ୍ତୁ",

    "chat.title": "AI ଚାଷ ସହାୟକ",
    "chat.welcome": "ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କ AI ଚାଷ ସହାୟକ 🌾। ଫସଲ, ମାଟି, ପାଣିପାଗ, କୀଟ, ସାର ବା ଯେକୌଣସି ଚାଷ ବିଷୟରେ ପଚାରନ୍ତୁ!",
    "chat.placeholder": "ଚାଷ ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ...",

    "loading.processing": "ପ୍ରକ୍ରିୟାକରଣ ହେଉଛି...",
    "loading.aiAnalyzing": "AI ଏଜେଣ୍ଟମାନେ ଆପଣଙ୍କ ଡାଟା ବିଶ୍ଳେଷଣ କରୁଛନ୍ତି",
},

}; // end TRANSLATIONS


// ═══════════════════════════════════════
//  Translation Engine
// ═══════════════════════════════════════

/**
 * Get a translated string for the given key and language.
 * Falls back to English if key is missing in the target language.
 */
function t(key, lang) {
    lang = lang || (typeof state !== 'undefined' ? state.language : 'en') || 'en';
    const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
    return dict[key] || TRANSLATIONS.en[key] || key;
}

/**
 * Apply translations to all elements with data-i18n attributes.
 * Supports:
 *   data-i18n="key"                  → sets textContent
 *   data-i18n-placeholder="key"      → sets placeholder
 *   data-i18n-title="key"            → sets title attribute
 *   data-i18n-html="key"             → sets innerHTML (use cautiously)
 */
function applyTranslations(lang) {
    lang = lang || state.language || 'en';

    // Text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const val = t(key, lang);
        if (val && val !== key) {
            el.textContent = val;
        }
    });

    // Placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const val = t(key, lang);
        if (val && val !== key) {
            el.placeholder = val;
        }
    });

    // Title attr
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        const val = t(key, lang);
        if (val && val !== key) {
            el.title = val;
        }
    });

    // innerHTML
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
        const key = el.getAttribute('data-i18n-html');
        const val = t(key, lang);
        if (val && val !== key) {
            el.innerHTML = val;
        }
    });

    // Update greeting with correct language
    updateGreetingLang(lang);
}

/**
 * Update the dashboard greeting in the correct language.
 */
function updateGreetingLang(lang) {
    const h = new Date().getHours();
    let greetKey = h < 12 ? 'dash.goodMorning' : h < 17 ? 'dash.goodAfternoon' : 'dash.goodEvening';
    const el = document.getElementById('dash-greeting');
    if (el) el.textContent = t(greetKey, lang);
}
