/* ══════════════════════════════════════════════════
   AgriSmart AI — Application Logic
   Complete JS for all pages & features
   ══════════════════════════════════════════════════ */

// ─── State ───
const state = {
    user: null,
    farmSetup: null,
    recommendations: [],
    leafletMap: null,
    mapMarkers: [],
    currentPage: 'dashboard',
    language: localStorage.getItem('agri_lang') || 'en',
    isOffline: !navigator.onLine
};

const API = window.API_BASE || 'http://127.0.0.1:8001';

// ─── Initialise on Load ───
document.addEventListener('DOMContentLoaded', () => {
    restoreSession();
    setupNetworkListeners();
    updateOfflineUI();
    setGreeting();
    // Apply saved language on load
    applyTranslations(state.language);
    // Sync lang label
    const labels = { en: 'EN', hi: 'हि', kn: 'ಕ', te: 'తె', ta: 'த', ml: 'മ', bn: 'বা', gu: 'ગુ', mr: 'म', pa: 'ਪ', or: 'ଓ' };
    const langLbl = document.getElementById('lang-label');
    if (langLbl) langLbl.textContent = labels[state.language] || 'EN';
    if (document.getElementById('settings-language')) {
        document.getElementById('settings-language').value = state.language;
    }
    // Restore Simple Mode
    if (localStorage.getItem('agri_simple_mode') === '1') {
        activateSimpleMode(false);
    }
    // Show walkthrough for first-time users
    if (!localStorage.getItem('agri_walkthrough_done')) {
        setTimeout(() => startWalkthrough(), 800);
    }
});

// ═══════════════════════════════════════════════════════════════
//  SIMPLE MODE — For Illiterate Farmers
//  Voice-first, picture-first, minimal text, big buttons
// ═══════════════════════════════════════════════════════════════

function toggleSimpleMode() {
    const isSimple = document.body.classList.contains('simple-mode');
    if (isSimple) {
        deactivateSimpleMode();
    } else {
        activateSimpleMode(true);
    }
}

function activateSimpleMode(announce = true) {
    document.body.classList.add('simple-mode');
    localStorage.setItem('agri_simple_mode', '1');
    
    // Show simple-only elements, hide advanced-only
    document.querySelectorAll('.simple-only').forEach(el => el.style.display = '');
    document.querySelectorAll('.advanced-only').forEach(el => el.style.display = 'none');
    
    // Update toggle button appearance
    const toggle = document.getElementById('simple-mode-toggle');
    if (toggle) {
        toggle.classList.add('active');
        toggle.querySelector('.smt-label').textContent = '✓ Simple Mode ON';
    }
    
    // Show picture nav on dashboard
    const picNav = document.getElementById('picture-nav');
    if (picNav) picNav.style.display = '';
    
    // Show one-tap section
    const oneTap = document.getElementById('one-tap-section');
    if (oneTap) oneTap.style.display = '';
    
    // Show simple weather
    const simpleWeather = document.getElementById('simple-weather');
    if (simpleWeather) simpleWeather.style.display = '';
    
    // Show emergency button
    const emergBtn = document.getElementById('emergency-pest-btn');
    if (emergBtn) emergBtn.style.display = '';
    
    // Show visual pickers
    const vcPicker = document.getElementById('visual-crop-picker');
    if (vcPicker) vcPicker.style.display = '';
    const vsPicker = document.getElementById('visual-soil-picker');
    if (vsPicker) vsPicker.style.display = '';
    
    if (announce) {
        speakText(getSimpleText('simple.activated', 'Simple Mode activated! I will now speak everything aloud and show pictures instead of text. Tap the big pictures to use the app.'));
        toast('🌾 Simple Mode ON — Pictures & Voice!', 'success');
    }
}

function deactivateSimpleMode() {
    document.body.classList.remove('simple-mode');
    localStorage.setItem('agri_simple_mode', '0');
    
    document.querySelectorAll('.simple-only').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.advanced-only').forEach(el => el.style.display = '');
    
    const toggle = document.getElementById('simple-mode-toggle');
    if (toggle) {
        toggle.classList.remove('active');
        toggle.querySelector('.smt-label').textContent = 'Simple Mode';
    }
    
    // Hide picture nav, one-tap, etc.
    ['picture-nav', 'one-tap-section', 'simple-weather', 'emergency-pest-btn', 'visual-crop-picker', 'visual-soil-picker'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });
    
    window.speechSynthesis?.cancel();
    toast('Advanced Mode restored', 'info');
}

// ═══════════════════════════════════════
//  TEXT-TO-SPEECH ENGINE
// ═══════════════════════════════════════

const ttsLangMap = {
    'en': 'en-IN', 'hi': 'hi-IN', 'kn': 'kn-IN', 'te': 'te-IN',
    'ta': 'ta-IN', 'ml': 'ml-IN', 'bn': 'bn-IN', 'gu': 'gu-IN',
    'mr': 'mr-IN', 'pa': 'pa-IN', 'or': 'or-IN'
};

function speakText(text, lang) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    
    // Clean HTML tags and markdown
    const cleanText = text.replace(/<[^>]*>/g, '').replace(/\*\*/g, '').replace(/\*/g, '').replace(/#{1,6}\s/g, '').replace(/\n{2,}/g, '. ').replace(/\n/g, ', ').substring(0, 2000);
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = ttsLangMap[lang || state.language] || 'en-IN';
    utterance.rate = 0.85;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    // Try to find a voice for the language
    const voices = window.speechSynthesis.getVoices();
    const targetLang = utterance.lang;
    const matchedVoice = voices.find(v => v.lang === targetLang) || voices.find(v => v.lang.startsWith(targetLang.split('-')[0]));
    if (matchedVoice) utterance.voice = matchedVoice;
    
    window.speechSynthesis.speak(utterance);
    return utterance;
}

function autoSpeak(text) {
    // Only auto-speak if simple mode is active
    if (document.body.classList.contains('simple-mode')) {
        speakText(text);
    }
}

function stopSpeaking() {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
}

// Pre-load voices
if (window.speechSynthesis) {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

// Add speaker buttons to result sections
function addSpeakerButton(container, text) {
    const btn = document.createElement('button');
    btn.className = 'speaker-btn';
    btn.innerHTML = '🔊';
    btn.title = 'Listen';
    btn.onclick = (e) => {
        e.stopPropagation();
        speakText(text);
        btn.classList.add('speaking');
        const utterances = window.speechSynthesis;
        const checkDone = setInterval(() => {
            if (!utterances.speaking) {
                btn.classList.remove('speaking');
                clearInterval(checkDone);
            }
        }, 300);
    };
    if (container.querySelector('.speaker-btn')) return; // Don't add duplicate
    container.style.position = 'relative';
    container.appendChild(btn);
}

// ═══════════════════════════════════════
//  ONE-TAP SMART ADVICE
// ═══════════════════════════════════════

async function oneTapAdvice() {
    const progressEl = document.getElementById('one-tap-progress');
    const resultEl = document.getElementById('one-tap-result');
    const btnEl = document.getElementById('one-tap-btn');
    
    if (progressEl) progressEl.style.display = '';
    if (resultEl) { resultEl.style.display = 'none'; resultEl.innerHTML = ''; }
    if (btnEl) { btnEl.disabled = true; btnEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Working...'; }
    
    // Navigate to dashboard first
    navigate('dashboard');
    
    function setOTPStep(step, status) {
        const el = document.getElementById(`otp-step-${step}`);
        if (!el) return;
        el.className = `otp-step ${status}`; // 'active', 'done', 'error'
    }
    
    try {
        // Step 1: Detect Location
        setOTPStep(1, 'active');
        autoSpeak('Finding your location...');
        
        const pos = await new Promise((resolve, reject) => {
            if (!navigator.geolocation) reject(new Error('No GPS'));
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true, timeout: 15000, maximumAge: 300000
            });
        });
        
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        document.getElementById('user-lat').value = lat;
        document.getElementById('user-lon').value = lon;
        
        let placeName = `${lat.toFixed(2)}°N`;
        try {
            const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&zoom=10`);
            const geoData = await geoRes.json();
            placeName = geoData.address?.village || geoData.address?.town || geoData.address?.city || placeName;
        } catch {}
        
        setOTPStep(1, 'done');
        
        // Step 2: Fetch Weather
        setOTPStep(2, 'active');
        autoSpeak('Checking weather for ' + placeName);
        
        const weatherData = await fetchAPI('/weather', { lat, lon });
        const temp = Math.round(weatherData.current_weather?.temperature || 25);
        const hum = weatherData.current_weather?.humidity || 60;
        const rain = Math.round(weatherData.metrics?.total_rainfall || 0);
        
        // Update hidden fields
        document.getElementById('temperature').value = temp;
        document.getElementById('humidity').value = hum;
        document.getElementById('rainfall').value = rain;
        
        // Update simple weather display
        const simpleIcon = document.getElementById('simple-weather-icon');
        const simpleTemp = document.getElementById('simple-weather-temp');
        if (simpleIcon) simpleIcon.textContent = temp > 35 ? '🔥' : temp > 25 ? '☀️' : temp > 15 ? '⛅' : '❄️';
        if (simpleTemp) simpleTemp.textContent = temp + '°';
        
        setOTPStep(2, 'done');
        
        // Step 3: Get AI Recommendation
        setOTPStep(3, 'active');
        autoSpeak('AI is analyzing your farm data...');
        
        const soilType = state.farmSetup?.soil_type || document.getElementById('soil-type').value || 'Loamy';
        const cropPref = state.farmSetup?.crop_preference || document.getElementById('crop-preference').value || 'Grains';
        
        // Auto-save farm setup
        state.farmSetup = {
            land_size: state.farmSetup?.land_size || 5,
            soil_type: soilType,
            crop_preference: cropPref,
            nitrogen: state.farmSetup?.nitrogen || 0,
            phosphorus: state.farmSetup?.phosphorus || 0,
            potassium: state.farmSetup?.potassium || 0,
            temperature: temp, humidity: hum, ph: 6.5, rainfall: rain,
            lat, lon, locMethod: 'gps', city: placeName
        };
        localStorage.setItem('agri_farm_setup', JSON.stringify(state.farmSetup));
        
        const data = await fetchAPI('/multi_agent_recommendation', {
            username: state.user?.username || 'anonymous',
            land_size: state.farmSetup.land_size,
            soil_type: soilType, crop_preference: cropPref,
            nitrogen: state.farmSetup.nitrogen, phosphorus: state.farmSetup.phosphorus,
            potassium: state.farmSetup.potassium,
            temperature: temp, humidity: hum, ph: 6.5, rainfall: rain
        });
        
        setOTPStep(3, 'done');
        
        // Step 4: Show & Speak Result
        setOTPStep(4, 'active');
        
        const topCrop = data.central_coordinator?.final_crop || 'Unknown crop';
        const score = data.central_coordinator?.overall_score || 0;
        const confidence = data.central_coordinator?.confidence_level || 'Medium';
        const scoreColor = score >= 7 ? '#16a34a' : score >= 5 ? '#eab308' : '#dc2626';
        const trafficEmoji = score >= 7 ? '🟢' : score >= 5 ? '🟡' : '🔴';
        
        // Build simple visual result
        let resultHTML = `
            <div class="one-tap-result-card" style="border-color:${scoreColor}">
                <div class="otr-traffic">${trafficEmoji}</div>
                <div class="otr-crop-name">${topCrop}</div>
                <div class="otr-score" style="color:${scoreColor}">${score}/10</div>
                <div class="otr-location">📍 ${placeName} | 🌡️ ${temp}° | 💧 ${hum}%</div>
            </div>`;
        
        // Add simple advice cards
        const agents = data.agents || {};
        if (agents.farmer_advisor?.advice) {
            resultHTML += `<div class="simple-advice-card"><span class="sac-icon">🚜</span><p>${agents.farmer_advisor.advice}</p></div>`;
        }
        if (agents.weather_analyst?.advice) {
            resultHTML += `<div class="simple-advice-card"><span class="sac-icon">🌤️</span><p>${agents.weather_analyst.advice}</p></div>`;
        }
        
        if (resultEl) {
            resultEl.innerHTML = resultHTML;
            resultEl.style.display = '';
        }
        
        // Build speech text
        let speechText = `Great news! Based on your location in ${placeName}, with temperature ${temp} degrees and ${hum} percent humidity, our AI recommends growing ${topCrop}. `;
        speechText += `The confidence score is ${score} out of 10. `;
        if (agents.farmer_advisor?.advice) speechText += agents.farmer_advisor.advice + '. ';
        if (agents.weather_analyst?.advice) speechText += agents.weather_analyst.advice + '. ';
        
        speakText(speechText);
        
        setOTPStep(4, 'done');
        celebrateSuccess();
        
        // Save recommendation
        const rec = { ...data, timestamp: new Date().toISOString() };
        state.recommendations.unshift(rec);
        if (state.recommendations.length > 20) state.recommendations.pop();
        localStorage.setItem('agri_recommendations', JSON.stringify(state.recommendations));
        
    } catch (err) {
        const failStep = document.querySelector('.otp-step.active');
        if (failStep) failStep.className = 'otp-step error';
        
        let errorMsg = 'Something went wrong. Please try again.';
        if (err.code === 1) errorMsg = 'Please allow location access and try again.';
        if (resultEl) {
            resultEl.innerHTML = `<div class="one-tap-result-card" style="border-color:#ef4444"><div class="otr-traffic">❌</div><div class="otr-crop-name">${errorMsg}</div></div>`;
            resultEl.style.display = '';
        }
        autoSpeak(errorMsg);
    } finally {
        if (btnEl) { btnEl.disabled = false; btnEl.innerHTML = '<i class="fas fa-magic"></i> Tap Here!'; }
    }
}

// ═══════════════════════════════════════
//  VISUAL CROP & SOIL PICKERS
// ═══════════════════════════════════════

function selectVisualCrop(crop, btn) {
    // Update visual selection
    document.querySelectorAll('.visual-crop-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    
    // Map visual crop to form value
    const cropMapping = {
        'Rice': 'Grains', 'Wheat': 'Grains', 'Corn': 'Grains',
        'Tomato': 'Vegetables', 'Potato': 'Vegetables', 'Vegetables': 'Vegetables',
        'Cotton': 'Grains', 'Soybean': 'Grains', 'Fruits': 'Fruits'
    };
    const selectVal = cropMapping[crop] || 'Grains';
    document.getElementById('crop-preference').value = selectVal;
    
    // Store specific crop for recommendation
    state.selectedSpecificCrop = crop;
    
    autoSpeak('You selected ' + crop);
    toast(`Selected: ${crop} ✓`, 'success');
}

function selectVisualSoil(soil, btn) {
    document.querySelectorAll('.visual-soil-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    document.getElementById('soil-type').value = soil;
    
    autoSpeak('You selected ' + soil + ' soil');
    toast(`Soil: ${soil} ✓`, 'success');
}

// ═══════════════════════════════════════
//  EMERGENCY PEST HELP
// ═══════════════════════════════════════

function emergencyPestHelp() {
    document.getElementById('emergency-modal').style.display = '';
    document.getElementById('emergency-result').style.display = 'none';
    document.getElementById('emergency-result').innerHTML = '';
    autoSpeak('Which crop needs help? Tap the picture of your crop.');
}

function closeEmergencyModal() {
    document.getElementById('emergency-modal').style.display = 'none';
    stopSpeaking();
}

async function runEmergencyPest(crop) {
    const resultEl = document.getElementById('emergency-result');
    resultEl.innerHTML = '<div style="text-align:center;padding:1rem"><i class="fas fa-spinner fa-spin" style="font-size:2rem;color:#ef4444"></i><p>Checking pest danger...</p></div>';
    resultEl.style.display = '';
    
    autoSpeak('Checking pest danger for ' + crop + '...');
    
    try {
        const temp = state.farmSetup?.temperature || 25;
        const humidity = state.farmSetup?.humidity || 65;
        const rainfall = state.farmSetup?.rainfall || 500;
        const soil = state.farmSetup?.soil_type || 'Loamy';
        
        const data = await fetchAPI('/pest_prediction', {
            crop_type: crop, soil_type: soil,
            temperature: temp, humidity: humidity, rainfall: rainfall
        });
        
        const risk = (data.overall_risk || 'low').toLowerCase();
        const riskEmoji = risk === 'high' ? '🔴' : risk === 'medium' ? '🟡' : '🟢';
        const riskLabel = risk === 'high' ? 'DANGER!' : risk === 'medium' ? 'Watch Out' : 'Safe';
        const riskColor = risk === 'high' ? '#ef4444' : risk === 'medium' ? '#eab308' : '#16a34a';
        
        let html = `<div class="emergency-result-card" style="border-color:${riskColor}">
            <div class="er-traffic">${riskEmoji}</div>
            <div class="er-label" style="color:${riskColor}">${riskLabel}</div>
            <div class="er-crop">${crop}</div>
        </div>`;
        
        // Show top pests visually
        if (data.predictions?.length) {
            html += '<div class="er-pests">';
            data.predictions.slice(0, 3).forEach(p => {
                const sev = (p.severity || 'low').toLowerCase();
                const icon = sev === 'high' ? '🔴' : sev === 'medium' ? '🟡' : '🟢';
                html += `<div class="er-pest-item"><span>${icon}</span><strong>${p.pest}</strong><span>${Math.round(p.probability * 100)}%</span></div>`;
            });
            html += '</div>';
        }
        
        // Prevention tips (first 2)
        if (data.prevention_tips?.length) {
            html += '<div class="er-tips">';
            data.prevention_tips.slice(0, 2).forEach(tip => {
                html += `<div class="er-tip">💡 ${tip}</div>`;
            });
            html += '</div>';
        }
        
        resultEl.innerHTML = html;
        
        // Speak the result
        let speech = `${riskLabel} for ${crop}! `;
        if (data.predictions?.length) {
            speech += 'Main pests: ' + data.predictions.slice(0, 2).map(p => p.pest).join(' and ') + '. ';
        }
        if (data.prevention_tips?.length) {
            speech += 'Tip: ' + data.prevention_tips[0];
        }
        speakText(speech);
        
    } catch (err) {
        resultEl.innerHTML = `<div class="emergency-result-card" style="border-color:#ef4444">
            <div class="er-traffic">❌</div><div class="er-label" style="color:#ef4444">Could not check. Try again.</div></div>`;
        autoSpeak('Could not check pest danger. Please try again.');
    }
}

// ═══════════════════════════════════════
//  AUDIO PAGE NARRATION
// ═══════════════════════════════════════

const pageNarrations = {
    'dashboard': 'simple.narrate.dashboard|Welcome to your farm dashboard. Tap the big green button to get AI advice, or tap the pictures below to navigate.',
    'farm-setup': 'simple.narrate.farmSetup|This is Farm Setup. First, tap Detect My Location. Then tap a crop picture to choose what you want to grow. Finally tap Save.',
    'recommendation': 'simple.narrate.recommendation|This page shows AI recommendations. Tap Generate Now to get crop advice from our AI experts.',
    'weather': 'simple.narrate.weather|This page shows weather for your farm. Tap Get Forecast to see the weather.',
    'pest-prediction': 'simple.narrate.pest|This page checks for pest and disease danger. Select your crop and tap Analyze.',
    'soil-analysis': 'simple.narrate.soil|Take a photo of your soil or tap a soil type to analyze it.',
    'community': 'simple.narrate.community|Share your farming data with other farmers and learn from them.'
};

function narratePage(pageId) {
    if (!document.body.classList.contains('simple-mode')) return;
    const entry = pageNarrations[pageId];
    if (!entry) return;
    const [, fallback] = entry.split('|');
    // Small delay so speech doesn't overlap with navigation
    setTimeout(() => speakText(fallback), 500);
}

// ═══════════════════════════════════════
//  HELPER: Get simple mode text
// ═══════════════════════════════════════
function getSimpleText(key, fallback) {
    // Try translations first, fall back to English
    if (typeof t === 'function') {
        const translated = t(key, state.language);
        if (translated && translated !== key) return translated;
    }
    return fallback;
}

// ═══════════════════════════════════════
//  WALKTHROUGH / ONBOARDING
// ═══════════════════════════════════════
const walkthroughSteps = [
    {
        illustration: 'farm',
        title: 'Welcome to AgriSmart AI!',
        desc: 'Your smart farming assistant powered by AI. Let us guide you through the app — it takes just 30 seconds!',
        color: '#16a34a'
    },
    {
        illustration: 'gps',
        title: 'Step 1: Detect Your Location',
        desc: 'Go to Farm Setup and tap "Detect My Location". We automatically get your weather, temperature, and rainfall — no typing needed!',
        color: '#0ea5e9'
    },
    {
        illustration: 'plant',
        title: 'Step 2: Tell Us About Fertilizer',
        desc: 'Just tap emoji buttons — None, Little, Medium, or A Lot — for each fertilizer type. Simple and quick!',
        color: '#f59e0b'
    },
    {
        illustration: 'ai',
        title: 'Step 3: Get AI Recommendations',
        desc: '5 AI agents analyze your data together — crop advisor, market researcher, weather analyst, sustainability expert, and coordinator. Watch them discuss!',
        color: '#8b5cf6'
    },
    {
        illustration: 'charts',
        title: 'Explore More Features',
        desc: 'Soil analysis from photos, pest prediction, weather alerts, community insights, crop rotation planner — all powered by AI for your farm!',
        color: '#ec4899'
    }
];
let walkthroughStep = 0;

function startWalkthrough() {
    walkthroughStep = 0;
    const overlay = document.getElementById('walkthrough-overlay');
    if (!overlay) return;
    overlay.style.display = '';
    renderWalkthroughStep();
}

function renderWalkthroughStep() {
    const step = walkthroughSteps[walkthroughStep];
    // Render animated SVG illustration
    const illustrationEl = document.getElementById('walkthrough-illustration');
    if (illustrationEl) {
        illustrationEl.innerHTML = getWalkthroughSVG(step.illustration, step.color);
    }
    document.getElementById('walkthrough-title').textContent = step.title;
    document.getElementById('walkthrough-desc').textContent = step.desc;
    const pct = ((walkthroughStep + 1) / walkthroughSteps.length) * 100;
    document.getElementById('walkthrough-progress-bar').style.width = pct + '%';
    document.getElementById('walkthrough-progress-bar').style.background = step.color;
    const dotsEl = document.getElementById('walkthrough-dots');
    dotsEl.innerHTML = walkthroughSteps.map((_, i) =>
        `<span class="wt-dot${i === walkthroughStep ? ' active' : ''}" style="${i === walkthroughStep ? 'background:' + step.color : ''}"></span>`
    ).join('');
    const nextBtn = document.getElementById('walkthrough-next');
    nextBtn.textContent = walkthroughStep === walkthroughSteps.length - 1 ? "Let's Go! 🚀" : 'Next →';
    const card = document.getElementById('walkthrough-card');
    card.classList.remove('animate-scale-in');
    void card.offsetWidth;
    card.classList.add('animate-scale-in');
}

function nextWalkthroughStep() {
    walkthroughStep++;
    if (walkthroughStep >= walkthroughSteps.length) {
        closeWalkthrough();
        return;
    }
    renderWalkthroughStep();
}

function closeWalkthrough() {
    const overlay = document.getElementById('walkthrough-overlay');
    if (overlay) overlay.style.display = 'none';
    localStorage.setItem('agri_walkthrough_done', '1');
    // Celebrate completion with confetti!
    launchConfetti();
}

// ═══════════════════════════════════════
//  ANIMATED SVG ILLUSTRATIONS
// ═══════════════════════════════════════
function getWalkthroughSVG(type, color) {
    const svgs = {
        farm: `<svg viewBox="0 0 200 200" width="140" height="140" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#87CEEB"/><stop offset="100%" stop-color="#E0F4FF"/></linearGradient>
            </defs>
            <rect width="200" height="200" rx="24" fill="url(#sky)"/>
            <!-- Sun -->
            <circle cx="160" cy="40" r="20" fill="#FDB813">
                <animate attributeName="r" values="18;22;18" dur="3s" repeatCount="indefinite"/>
            </circle>
            <g stroke="#FDB813" stroke-width="2" fill="none">
                <line x1="160" y1="10" x2="160" y2="6"><animate attributeName="y2" values="6;2;6" dur="3s" repeatCount="indefinite"/></line>
                <line x1="190" y1="40" x2="194" y2="40"><animate attributeName="x2" values="194;198;194" dur="3s" repeatCount="indefinite"/></line>
                <line x1="180" y1="20" x2="184" y2="16"><animate attributeName="x2" values="184;188;184" dur="3s" repeatCount="indefinite"/></line>
                <line x1="180" y1="60" x2="184" y2="64"><animate attributeName="x2" values="184;188;184" dur="3s" repeatCount="indefinite"/></line>
            </g>
            <!-- Ground -->
            <ellipse cx="100" cy="175" rx="90" ry="20" fill="#8B6914"/>
            <ellipse cx="100" cy="172" rx="88" ry="16" fill="#16a34a"/>
            <!-- Barn -->
            <rect x="30" y="105" width="50" height="55" rx="3" fill="#C23B22"/>
            <polygon points="30,105 55,80 80,105" fill="#8B2500"/>
            <rect x="48" y="130" width="14" height="30" rx="2" fill="#5C3317"/>
            <!-- Wheat stalks -->
            <g>
                <line x1="120" y1="155" x2="120" y2="110" stroke="#DAA520" stroke-width="2">
                    <animate attributeName="x2" values="118;122;118" dur="2.5s" repeatCount="indefinite"/>
                </line>
                <ellipse cx="120" cy="108" rx="4" ry="8" fill="#DAA520">
                    <animate attributeName="cx" values="118;122;118" dur="2.5s" repeatCount="indefinite"/>
                </ellipse>
            </g>
            <g>
                <line x1="140" y1="155" x2="140" y2="105" stroke="#DAA520" stroke-width="2">
                    <animate attributeName="x2" values="142;138;142" dur="2.8s" repeatCount="indefinite"/>
                </line>
                <ellipse cx="140" cy="103" rx="4" ry="8" fill="#DAA520">
                    <animate attributeName="cx" values="142;138;142" dur="2.8s" repeatCount="indefinite"/>
                </ellipse>
            </g>
            <g>
                <line x1="160" y1="155" x2="160" y2="112" stroke="#DAA520" stroke-width="2">
                    <animate attributeName="x2" values="158;162;158" dur="2.3s" repeatCount="indefinite"/>
                </line>
                <ellipse cx="160" cy="110" rx="4" ry="8" fill="#DAA520">
                    <animate attributeName="cx" values="158;162;158" dur="2.3s" repeatCount="indefinite"/>
                </ellipse>
            </g>
            <!-- Cloud -->
            <g opacity="0.8">
                <animateTransform attributeName="transform" type="translate" values="0,0;15,0;0,0" dur="8s" repeatCount="indefinite"/>
                <circle cx="50" cy="35" r="12" fill="white"/><circle cx="65" cy="30" r="16" fill="white"/><circle cx="80" cy="35" r="12" fill="white"/>
            </g>
        </svg>`,
        gps: `<svg viewBox="0 0 200 200" width="140" height="140" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" rx="24" fill="#EFF6FF"/>
            <!-- Map grid -->
            <g stroke="#CBD5E1" stroke-width="0.5" opacity="0.5">
                <line x1="40" y1="40" x2="40" y2="180"/><line x1="80" y1="40" x2="80" y2="180"/>
                <line x1="120" y1="40" x2="120" y2="180"/><line x1="160" y1="40" x2="160" y2="180"/>
                <line x1="20" y1="60" x2="180" y2="60"/><line x1="20" y1="100" x2="180" y2="100"/>
                <line x1="20" y1="140" x2="180" y2="140"/>
            </g>
            <!-- Location pin -->
            <g>
                <animateTransform attributeName="transform" type="translate" values="0,0;0,-8;0,0" dur="1.5s" repeatCount="indefinite"/>
                <path d="M100,60 C80,60 68,78 68,92 C68,115 100,145 100,145 C100,145 132,115 132,92 C132,78 120,60 100,60Z" fill="#0ea5e9"/>
                <circle cx="100" cy="90" r="12" fill="white"/>
                <circle cx="100" cy="90" r="5" fill="#0ea5e9"/>
            </g>
            <!-- Pulse rings -->
            <circle cx="100" cy="145" rx="1" fill="none" stroke="#0ea5e9" stroke-width="2">
                <animate attributeName="r" values="5;35;5" dur="2s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite"/>
            </circle>
            <circle cx="100" cy="145" fill="none" stroke="#0ea5e9" stroke-width="1.5">
                <animate attributeName="r" values="5;25;5" dur="2s" begin="0.5s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="0.4;0;0.4" dur="2s" begin="0.5s" repeatCount="indefinite"/>
            </circle>
            <!-- Satellite -->
            <g>
                <animateTransform attributeName="transform" type="rotate" values="0 100 50;360 100 50" dur="6s" repeatCount="indefinite"/>
                <rect x="140" y="45" width="12" height="8" rx="2" fill="#64748B"/>
                <rect x="134" y="47" width="6" height="4" fill="#0EA5E9"/>
                <rect x="152" y="47" width="6" height="4" fill="#0EA5E9"/>
            </g>
        </svg>`,
        plant: `<svg viewBox="0 0 200 200" width="140" height="140" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" rx="24" fill="#FFFBEB"/>
            <!-- Pot -->
            <path d="M65,145 L75,180 L125,180 L135,145 Z" fill="#D97706"/>
            <rect x="60" y="138" width="80" height="12" rx="4" fill="#F59E0B"/>
            <!-- Soil -->
            <ellipse cx="100" cy="145" rx="30" ry="5" fill="#92400E"/>
            <!-- Plant stem -->
            <path d="M100,140 Q100,90 100,70" stroke="#16a34a" stroke-width="3" fill="none">
                <animate attributeName="d" values="M100,140 Q100,90 100,80;M100,140 Q100,90 100,65;M100,140 Q100,90 100,80" dur="3s" repeatCount="indefinite"/>
            </path>
            <!-- Leaves -->
            <g>
                <animateTransform attributeName="transform" type="rotate" values="-5 100 100;5 100 100;-5 100 100" dur="3s" repeatCount="indefinite"/>
                <ellipse cx="80" cy="95" rx="18" ry="8" fill="#22c55e" transform="rotate(-30 80 95)"/>
                <ellipse cx="120" cy="90" rx="18" ry="8" fill="#16a34a" transform="rotate(25 120 90)"/>
                <ellipse cx="85" cy="75" rx="14" ry="6" fill="#4ade80" transform="rotate(-20 85 75)"/>
                <ellipse cx="115" cy="72" rx="14" ry="6" fill="#22c55e" transform="rotate(15 115 72)"/>
            </g>
            <!-- Sparkles -->
            <g fill="#F59E0B">
                <circle cx="60" cy="60" r="3"><animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite"/></circle>
                <circle cx="145" cy="55" r="2"><animate attributeName="opacity" values="0;1;0" dur="2.5s" begin="0.5s" repeatCount="indefinite"/></circle>
                <circle cx="50" cy="95" r="2"><animate attributeName="opacity" values="0;1;0" dur="1.8s" begin="1s" repeatCount="indefinite"/></circle>
                <circle cx="155" cy="100" r="3"><animate attributeName="opacity" values="0;1;0" dur="2.2s" begin="0.3s" repeatCount="indefinite"/></circle>
            </g>
            <!-- Water drops -->
            <g fill="#38BDF8">
                <circle cx="75" cy="125" r="2.5">
                    <animate attributeName="cy" values="115;135;115" dur="2s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="1;0;1" dur="2s" repeatCount="indefinite"/>
                </circle>
                <circle cx="125" cy="120" r="2">
                    <animate attributeName="cy" values="110;130;110" dur="2.3s" begin="0.5s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="1;0;1" dur="2.3s" begin="0.5s" repeatCount="indefinite"/>
                </circle>
            </g>
        </svg>`,
        ai: `<svg viewBox="0 0 200 200" width="140" height="140" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" rx="24" fill="#F5F3FF"/>
            <!-- Brain outline -->
            <g transform="translate(55,35)" fill="none" stroke="#8b5cf6" stroke-width="2.5">
                <path d="M45,0 C65,0 80,15 80,30 C80,40 75,48 68,53 C72,58 75,65 75,73 C75,90 60,100 45,100 C30,100 15,90 15,73 C15,65 18,58 22,53 C15,48 10,40 10,30 C10,15 25,0 45,0Z">
                    <animate attributeName="stroke-dasharray" values="0 350;350 0" dur="2s" fill="freeze"/>
                </path>
                <!-- Center line -->
                <line x1="45" y1="10" x2="45" y2="90" stroke-dasharray="3 5">
                    <animate attributeName="stroke-dashoffset" values="0;-16" dur="1s" repeatCount="indefinite"/>
                </line>
                <!-- Neural connections -->
                <circle cx="30" cy="35" r="4" fill="#8b5cf6"><animate attributeName="fill-opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite"/></circle>
                <circle cx="60" cy="35" r="4" fill="#8b5cf6"><animate attributeName="fill-opacity" values="0.3;1;0.3" dur="1.5s" begin="0.3s" repeatCount="indefinite"/></circle>
                <circle cx="25" cy="60" r="4" fill="#8b5cf6"><animate attributeName="fill-opacity" values="0.3;1;0.3" dur="1.5s" begin="0.6s" repeatCount="indefinite"/></circle>
                <circle cx="65" cy="60" r="4" fill="#8b5cf6"><animate attributeName="fill-opacity" values="0.3;1;0.3" dur="1.5s" begin="0.9s" repeatCount="indefinite"/></circle>
                <circle cx="45" cy="50" r="5" fill="#8b5cf6"><animate attributeName="fill-opacity" values="0.5;1;0.5" dur="1s" repeatCount="indefinite"/></circle>
                <!-- Firing synapses -->
                <line x1="30" y1="35" x2="45" y2="50" stroke-width="1.5"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="1.5s" repeatCount="indefinite"/></line>
                <line x1="60" y1="35" x2="45" y2="50" stroke-width="1.5"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="1.5s" begin="0.3s" repeatCount="indefinite"/></line>
                <line x1="25" y1="60" x2="45" y2="50" stroke-width="1.5"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="1.5s" begin="0.6s" repeatCount="indefinite"/></line>
                <line x1="65" y1="60" x2="45" y2="50" stroke-width="1.5"><animate attributeName="stroke-opacity" values="0.2;1;0.2" dur="1.5s" begin="0.9s" repeatCount="indefinite"/></line>
            </g>
            <!-- Orbiting dots -->
            <g>
                <circle cx="100" cy="25" r="4" fill="#EC4899">
                    <animateTransform attributeName="transform" type="rotate" values="0 100 100;360 100 100" dur="4s" repeatCount="indefinite"/>
                </circle>
            </g>
            <g>
                <circle cx="175" cy="100" r="3" fill="#F59E0B">
                    <animateTransform attributeName="transform" type="rotate" values="120 100 100;480 100 100" dur="5s" repeatCount="indefinite"/>
                </circle>
            </g>
        </svg>`,
        charts: `<svg viewBox="0 0 200 200" width="140" height="140" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" rx="24" fill="#FDF2F8"/>
            <!-- Chart axes -->
            <line x1="35" y1="30" x2="35" y2="160" stroke="#CBD5E1" stroke-width="2"/>
            <line x1="35" y1="160" x2="175" y2="160" stroke="#CBD5E1" stroke-width="2"/>
            <!-- Bars growing up -->
            <rect x="50" y="160" width="20" height="0" rx="3" fill="#16a34a">
                <animate attributeName="height" values="0;90;90" dur="1s" fill="freeze"/>
                <animate attributeName="y" values="160;70;70" dur="1s" fill="freeze"/>
            </rect>
            <rect x="80" y="160" width="20" height="0" rx="3" fill="#0ea5e9">
                <animate attributeName="height" values="0;60;60" dur="1s" begin="0.2s" fill="freeze"/>
                <animate attributeName="y" values="160;100;100" dur="1s" begin="0.2s" fill="freeze"/>
            </rect>
            <rect x="110" y="160" width="20" height="0" rx="3" fill="#f59e0b">
                <animate attributeName="height" values="0;110;110" dur="1s" begin="0.4s" fill="freeze"/>
                <animate attributeName="y" values="160;50;50" dur="1s" begin="0.4s" fill="freeze"/>
            </rect>
            <rect x="140" y="160" width="20" height="0" rx="3" fill="#ec4899">
                <animate attributeName="height" values="0;75;75" dur="1s" begin="0.6s" fill="freeze"/>
                <animate attributeName="y" values="160;85;85" dur="1s" begin="0.6s" fill="freeze"/>
            </rect>
            <!-- Trend line -->
            <polyline points="60,70 90,100 120,50 150,85" fill="none" stroke="#8b5cf6" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="200" stroke-dashoffset="200">
                <animate attributeName="stroke-dashoffset" values="200;0" dur="1.5s" begin="0.8s" fill="freeze"/>
            </polyline>
            <!-- Dots on trend -->
            <circle cx="60" cy="70" r="4" fill="#8b5cf6" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.3s" begin="1.5s" fill="freeze"/></circle>
            <circle cx="90" cy="100" r="4" fill="#8b5cf6" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.3s" begin="1.7s" fill="freeze"/></circle>
            <circle cx="120" cy="50" r="4" fill="#8b5cf6" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.3s" begin="1.9s" fill="freeze"/></circle>
            <circle cx="150" cy="85" r="4" fill="#8b5cf6" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.3s" begin="2.1s" fill="freeze"/></circle>
            <!-- Sparkle -->
            <circle cx="120" cy="45" r="3" fill="#F59E0B" opacity="0">
                <animate attributeName="opacity" values="0;1;0" dur="1.5s" begin="2s" repeatCount="indefinite"/>
                <animate attributeName="r" values="2;4;2" dur="1.5s" begin="2s" repeatCount="indefinite"/>
            </circle>
        </svg>`
    };
    return svgs[type] || `<div style="font-size:3.5rem">🌾</div>`;
}

// ═══════════════════════════════════════
function launchConfetti(duration = 2500) {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colors = ['#16a34a', '#f59e0b', '#ec4899', '#8b5cf6', '#0ea5e9', '#ef4444', '#22d3ee', '#facc15'];
    const particles = [];
    const count = 150;

    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height - canvas.height,
            w: Math.random() * 10 + 5,
            h: Math.random() * 6 + 3,
            color: colors[Math.floor(Math.random() * colors.length)],
            vx: (Math.random() - 0.5) * 4,
            vy: Math.random() * 3 + 2,
            rot: Math.random() * 360,
            vr: (Math.random() - 0.5) * 8,
            opacity: 1
        });
    }

    const startTime = Date.now();
    function animateConfetti() {
        const elapsed = Date.now() - startTime;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const fadeRatio = elapsed > duration * 0.7 ? 1 - (elapsed - duration * 0.7) / (duration * 0.3) : 1;

        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.05;
            p.rot += p.vr;
            p.opacity = Math.max(0, fadeRatio);

            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rot * Math.PI / 180);
            ctx.globalAlpha = p.opacity;
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
            ctx.restore();
        });

        if (elapsed < duration) {
            requestAnimationFrame(animateConfetti);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }
    requestAnimationFrame(animateConfetti);
}

// ═══════════════════════════════════════
//  SUCCESS CELEBRATION (smaller burst)
// ═══════════════════════════════════════
function celebrateSuccess() {
    launchConfetti(1800);
    // Also show a success pulse ring on the page
    const ring = document.createElement('div');
    ring.className = 'success-ring-burst';
    document.body.appendChild(ring);
    setTimeout(() => ring.remove(), 1200);
}

// ═══════════════════════════════════════
//  ANIMATED COUNTER (count-up effect)
// ═══════════════════════════════════════
function animateCounter(element, target, duration = 1200, suffix = '') {
    const start = 0;
    const startTime = performance.now();
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * eased);
        element.textContent = current + suffix;
        if (progress < 1) requestAnimationFrame(updateCounter);
    }
    requestAnimationFrame(updateCounter);
}

// ═══════════════════════════════════════
//  RIPPLE EFFECT ON BUTTONS
// ═══════════════════════════════════════
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn');
    if (!btn) return;
    const ripple = document.createElement('span');
    ripple.className = 'btn-ripple';
    const rect = btn.getBoundingClientRect();
    ripple.style.left = (e.clientX - rect.left) + 'px';
    ripple.style.top = (e.clientY - rect.top) + 'px';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
});

// ═══════════════════════════════════════
//  INTERSECTION OBSERVER — ANIMATE ON SCROLL
// ═══════════════════════════════════════
const scrollAnimObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-visible');
            scrollAnimObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.card, .feature-guide, .empty-state').forEach(el => {
        el.classList.add('animate-on-scroll');
        scrollAnimObserver.observe(el);
    });
});

// ═══════════════════════════════════════
//  SKELETON LOADING HELPER
// ═══════════════════════════════════════
function showSkeleton(containerId, rows = 3) {
    const container = document.getElementById(containerId);
    if (!container) return;
    let skeletonHTML = '<div class="skeleton-loader">';
    for (let i = 0; i < rows; i++) {
        const w = 60 + Math.random() * 35;
        skeletonHTML += `<div class="skeleton-line" style="width:${w}%;animation-delay:${i*0.1}s"></div>`;
    }
    skeletonHTML += '</div>';
    container.innerHTML = skeletonHTML;
}

function hideSkeleton(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const sk = container.querySelector('.skeleton-loader');
    if (sk) sk.remove();
}

// ═══════════════════════════════════════
//  TYPING ANIMATION (for AI responses)
// ═══════════════════════════════════════
function typeText(element, text, speed = 15) {
    return new Promise(resolve => {
        let i = 0;
        element.textContent = '';
        element.style.visibility = 'visible';
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                resolve();
            }
        }
        type();
    });
}

// ═══════════════════════════════════════

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.toggle('active', f.id === `${tab}-form`));
}

async function handleSignup(e) {
    e.preventDefault();
    const username = document.getElementById('signup-name').value.trim();
    const farm_name = document.getElementById('signup-farm').value.trim();
    const phone = document.getElementById('signup-phone').value.trim();
    const location = document.getElementById('signup-location').value.trim();
    if (!username || !farm_name) return toast('Please fill required fields', 'error');
    showLoading('Creating your account...');
    try {
        const res = await fetchAPI('/signup', { username, farm_name, profile_picture: null });
        state.user = { username, farm_name, phone, location };
        localStorage.setItem('agri_user', JSON.stringify(state.user));
        toast('Welcome to AgriSmart AI! 🌱', 'success');
        enterApp();
    } catch (err) {
        // If user already exists, try login
        if (err.message && err.message.includes('already exists')) {
            toast('Username exists — logging you in', 'info');
            state.user = { username, farm_name, phone, location };
            localStorage.setItem('agri_user', JSON.stringify(state.user));
            enterApp();
        } else {
            toast(err.message || 'Signup failed', 'error');
        }
    } finally {
        hideLoading();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const phone = document.getElementById('login-phone').value.trim();
    if (!phone) return toast('Enter your phone number', 'error');
    showLoading('Logging in...');
    try {
        const res = await fetchAPI('/login', { username: phone });
        state.user = res;
        localStorage.setItem('agri_user', JSON.stringify(state.user));
        toast(`Welcome back, ${res.username}! 🌾`, 'success');
        enterApp();
    } catch {
        toast('User not found — please sign up first', 'error');
    } finally {
        hideLoading();
    }
}

function restoreSession() {
    const saved = localStorage.getItem('agri_user');
    if (saved) {
        state.user = JSON.parse(saved);
        enterApp();
    }
    const savedSetup = localStorage.getItem('agri_farm_setup');
    if (savedSetup) state.farmSetup = JSON.parse(savedSetup);
    const savedRecs = localStorage.getItem('agri_recommendations');
    if (savedRecs) state.recommendations = JSON.parse(savedRecs);
}

function enterApp() {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('app-shell').style.display = 'flex';
    updateSidebarProfile();
    updateDashboard();
    loadDashboardWeather();
    navigate('dashboard');
}

function logout() {
    localStorage.removeItem('agri_user');
    state.user = null;
    document.getElementById('app-shell').style.display = 'none';
    document.getElementById('auth-screen').style.display = '';
    toast('Logged out', 'info');
}

// ═══════════════════════════════════════
//  NAVIGATION
// ═══════════════════════════════════════

function navigate(pageId) {
    state.currentPage = pageId;
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById(`${pageId}-page`);
    if (target) {
        target.classList.add('active');
        target.classList.add('animate-fade-in');
        setTimeout(() => target.classList.remove('animate-fade-in'), 400);
    }
    // Sidebar active
    document.querySelectorAll('.sidebar-link').forEach(l => l.classList.toggle('active', l.dataset.page === pageId));
    // Mobile bottom nav active
    document.querySelectorAll('.mob-item').forEach(m => m.classList.toggle('active', m.dataset.page === pageId));
    // Picture nav active
    document.querySelectorAll('.pic-nav-btn').forEach(b => b.classList.toggle('active', b.dataset.page === pageId));
    closeMobileMenu();
    // Audio narration for illiterate farmers (Simple Mode)
    narratePage(pageId);
    // Lazy-load actions
    if (pageId === 'history') loadHistory();
    if (pageId === 'profile') loadProfileData();
    if (pageId === 'offline') updateOfflinePage();
    if (pageId === 'community') loadCommunityInsights();
    if (pageId === 'sustainability') loadSustainabilityChart();
    // Auto-fill pest prediction with farm setup data
    if (pageId === 'pest-prediction' && state.farmSetup) {
        const pt = document.getElementById('pest-temp');
        const ph = document.getElementById('pest-humidity');
        const pr = document.getElementById('pest-rainfall');
        const ps = document.getElementById('pest-soil');
        if (pt && state.farmSetup.temperature) pt.value = state.farmSetup.temperature;
        if (ph && state.farmSetup.humidity) ph.value = state.farmSetup.humidity;
        if (pr && state.farmSetup.rainfall) pr.value = state.farmSetup.rainfall;
        if (ps && state.farmSetup.soil_type) ps.value = state.farmSetup.soil_type;
    }
}

// ─── Mobile menu ───
function openMobileMenu() {
    document.getElementById('sidebar').classList.add('mobile-open');
    document.getElementById('sidebar-overlay').classList.add('open');
}
function closeMobileMenu() {
    document.getElementById('sidebar').classList.remove('mobile-open');
    document.getElementById('sidebar-overlay').classList.remove('open');
}

// ═══════════════════════════════════════
//  SIDEBAR / DASHBOARD
// ═══════════════════════════════════════

function updateSidebarProfile() {
    if (!state.user) return;
    const initial = (state.user.username || 'F')[0].toUpperCase();
    document.getElementById('sidebar-avatar').textContent = initial;
    document.getElementById('sidebar-username').textContent = state.user.username || 'Farmer';
    document.getElementById('sidebar-farmname').textContent = state.user.farm_name || 'My Farm';
}

function setGreeting() {
    const h = new Date().getHours();
    const greetKey = h < 12 ? 'dash.goodMorning' : h < 17 ? 'dash.goodAfternoon' : 'dash.goodEvening';
    const el = document.getElementById('dash-greeting');
    if (el) el.textContent = t(greetKey, state.language);
}

function updateDashboard() {
    if (!state.user) return;
    document.getElementById('dash-name').textContent = `${state.user.username} 🌾`;
    document.getElementById('dash-farm').textContent = state.user.farm_name || '';
    // Stats
    if (state.farmSetup) {
        document.getElementById('stat-farm-size').textContent = `${state.farmSetup.land_size || '—'} ha`;
    }
    document.getElementById('stat-recs').textContent = state.recommendations.length;
}

async function loadDashboardWeather() {
    try {
        const lat = state.farmSetup?.lat || 12.9716;
        const lon = state.farmSetup?.lon || 77.5946;
        const data = await fetchAPI('/weather', { lat, lon });
        if (data.current_weather) {
            const temp = Math.round(data.current_weather.temperature);
            const hum = data.current_weather.humidity;
            const wind = data.current_weather.wind_speed;
            const desc = data.current_weather.description || 'Clear';
            document.getElementById('dash-temp').textContent = `${temp}°C`;
            document.getElementById('dash-humidity').textContent = `${hum}%`;
            document.getElementById('dash-wind').textContent = `${wind} km/h`;
            // Enhanced dashboard weather
            const bigTemp = document.getElementById('dash-big-temp');
            const bigDesc = document.getElementById('dash-big-desc');
            const detHum = document.getElementById('dash-det-hum');
            const detWind = document.getElementById('dash-det-wind');
            const detRain = document.getElementById('dash-det-rain');
            if (bigTemp) bigTemp.textContent = `${temp}°`;
            if (bigDesc) bigDesc.textContent = desc.charAt(0).toUpperCase() + desc.slice(1);
            if (detHum) detHum.textContent = `${hum}%`;
            if (detWind) detWind.textContent = `${wind} km/h`;
            if (detRain && data.metrics) detRain.textContent = `${data.metrics.total_rainfall || 0} mm`;
        }
    } catch { /* fallback defaults */ }
}

// ═══════════════════════════════════════
//  FARM SETUP
// ═══════════════════════════════════════

// NPK simple emoji selector
function setNPK(type, val, btn) {
    const row = btn.parentElement;
    row.querySelectorAll('.npk-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    const map = { n: 'nitrogen', p: 'phosphorus', k: 'potassium' };
    document.getElementById(map[type]).value = val;
}

// GPS Location Detection
async function detectMyLocation() {
    const statusEl = document.getElementById('gps-status');
    const statusText = document.getElementById('gps-status-text');
    const btn = document.getElementById('gps-detect-btn');
    
    statusEl.className = 'gps-status-box loading';
    statusText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting your location...';
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting...';

    try {
        // Get GPS coordinates
        const pos = await new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('GPS not supported on this device'));
                return;
            }
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 300000 // 5 min cache
            });
        });

        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        document.getElementById('user-lat').value = lat;
        document.getElementById('user-lon').value = lon;

        // Reverse geocode (simple - using Open-Meteo geocoding API)
        let placeName = `${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E`;
        try {
            const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&zoom=10`);
            const geoData = await geoRes.json();
            if (geoData.address) {
                placeName = geoData.address.village || geoData.address.town || geoData.address.city || geoData.address.county || placeName;
                document.getElementById('city-name').value = placeName;
            }
        } catch { /* use coordinates as fallback */ }

        // Fetch weather from Open-Meteo
        statusText.innerHTML = '<i class="fas fa-cloud-sun"></i> Fetching weather data...';
        const weatherData = await fetchAPI('/weather', { lat, lon });
        
        const temp = Math.round(weatherData.current_weather?.temperature || 25);
        const hum = weatherData.current_weather?.humidity || 60;
        const rain = Math.round(weatherData.metrics?.total_rainfall || 0);

        // Update hidden form fields
        document.getElementById('temperature').value = temp;
        document.getElementById('humidity').value = hum;
        document.getElementById('rainfall').value = rain;

        // Set pH based on soil type (smart default)
        const soilPh = { Loamy: 6.5, Sandy: 6.0, Clay: 7.0, Black: 7.5, Red: 5.5, Silty: 6.8 };
        const currentSoil = document.getElementById('soil-type').value;
        const ph = soilPh[currentSoil] || 6.5;
        document.getElementById('ph').value = ph;

        // Show result chips
        document.getElementById('gps-place-name').textContent = placeName;
        document.getElementById('gps-temp').textContent = `${temp}°C`;
        document.getElementById('gps-hum').textContent = `${hum}%`;
        document.getElementById('gps-rain').textContent = `${rain} mm/week`;
        document.getElementById('gps-result').style.display = '';

        // Show auto-weather card
        const autoCard = document.getElementById('auto-weather-card');
        if (autoCard) {
            autoCard.style.display = '';
            document.getElementById('auto-temp-val').textContent = `${temp}°C`;
            document.getElementById('auto-hum-val').textContent = `${hum}%`;
            document.getElementById('auto-rain-val').textContent = `${rain} mm`;
            document.getElementById('auto-ph-val').textContent = ph;
        }

        // Also update pest prediction fields
        const pestTemp = document.getElementById('pest-temp');
        const pestHum = document.getElementById('pest-humidity');
        const pestRain = document.getElementById('pest-rainfall');
        if (pestTemp) pestTemp.value = temp;
        if (pestHum) pestHum.value = hum;
        if (pestRain) pestRain.value = rain;

        statusEl.className = 'gps-status-box success';
        statusText.innerHTML = `<i class="fas fa-check-circle"></i> Location detected: <strong>${placeName}</strong>`;
        btn.innerHTML = '<i class="fas fa-check"></i> Location Detected!';
        btn.className = 'btn btn-success btn-large';
        toast(`Location detected: ${placeName} — weather data loaded! 📍`, 'success');
        autoSpeak(`Location detected: ${placeName}. Temperature ${temp} degrees, humidity ${hum} percent.`);

    } catch (err) {
        statusEl.className = 'gps-status-box error';
        let msg = 'Could not detect location.';
        if (err.code === 1) msg = 'Permission denied. Please allow location access.';
        else if (err.code === 2) msg = 'Location unavailable. Check GPS/network.';
        else if (err.code === 3) msg = 'Location request timed out. Try again.';
        statusText.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${msg}`;
        btn.innerHTML = '<i class="fas fa-redo"></i> Try Again';
        btn.disabled = false;
        btn.className = 'btn btn-primary btn-large';
        toast(msg, 'error');
    }
}

function convertLandUnit() {
    const val = parseFloat(document.getElementById('land-size').value) || 0;
    const unit = document.getElementById('land-unit').value;
    let hectares = val;
    if (unit === 'acres') hectares = val * 0.4047;
    else if (unit === 'cents') hectares = val * 0.004047;
    const el = document.getElementById('land-converted');
    if (unit !== 'hectares') {
        el.textContent = `≈ ${hectares.toFixed(2)} hectares`;
    } else {
        el.textContent = '';
    }
}

async function saveFarmSetup() {
    const land_size_raw = parseFloat(document.getElementById('land-size').value) || 5;
    const unit = document.getElementById('land-unit').value;
    let land_size = land_size_raw;
    if (unit === 'acres') land_size = land_size_raw * 0.4047;
    else if (unit === 'cents') land_size = land_size_raw * 0.004047;

    const lat = parseFloat(document.getElementById('user-lat').value) || 12.9716;
    const lon = parseFloat(document.getElementById('user-lon').value) || 77.5946;

    state.farmSetup = {
        land_size: Math.round(land_size * 100) / 100,
        soil_type: document.getElementById('soil-type').value,
        crop_preference: document.getElementById('crop-preference').value,
        nitrogen: +document.getElementById('nitrogen').value,
        phosphorus: +document.getElementById('phosphorus').value,
        potassium: +document.getElementById('potassium').value,
        temperature: +document.getElementById('temperature').value,
        humidity: +document.getElementById('humidity').value,
        ph: +document.getElementById('ph').value,
        rainfall: +document.getElementById('rainfall').value,
        lat, lon,
        locMethod: 'gps',
        city: document.getElementById('city-name')?.value || ''
    };
    localStorage.setItem('agri_farm_setup', JSON.stringify(state.farmSetup));

    // Send to backend
    try {
        await fetchAPI('/farm_details', {
            username: state.user?.username || 'anonymous',
            land_size: state.farmSetup.land_size,
            soil_type: state.farmSetup.soil_type,
            crop_preference: state.farmSetup.crop_preference
        });
    } catch { /* offline ok */ }

    // Add to recent activity
    addActivity('Farm details saved', 'green');
    updateDashboard();
    toast('Farm details saved! 🚜', 'success');
}

// Track recent activity on dashboard
function addActivity(text, color = 'green') {
    const feed = document.getElementById('dash-recent-activity');
    if (!feed) return;
    const item = document.createElement('div');
    item.className = 'activity-item animate-fade-in';
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    item.innerHTML = `<div class="activity-dot ${color}"></div><span>${text}</span><small>${timeStr}</small>`;
    feed.prepend(item);
    // Keep max 10 items
    while (feed.children.length > 10) feed.removeChild(feed.lastChild);
}

// ═══════════════════════════════════════
//  AI RECOMMENDATION (Multi-Agent)
// ═══════════════════════════════════════

async function getRecommendation() {
    if (!state.farmSetup) { toast('Please set up farm details first', 'info'); navigate('farm-setup'); return; }
    showLoading('4 AI agents are analyzing your farm data...');
    showSkeleton('recommendation-results', 5);
    const container = document.getElementById('recommendation-results');
    try {
        const data = await fetchAPI('/multi_agent_recommendation', {
            username: state.user?.username || 'anonymous',
            land_size: state.farmSetup.land_size,
            soil_type: state.farmSetup.soil_type,
            crop_preference: state.farmSetup.crop_preference,
            nitrogen: state.farmSetup.nitrogen,
            phosphorus: state.farmSetup.phosphorus,
            potassium: state.farmSetup.potassium,
            temperature: state.farmSetup.temperature,
            humidity: state.farmSetup.humidity,
            ph: state.farmSetup.ph,
            rainfall: state.farmSetup.rainfall
        });
        renderRecommendation(data, container);
        celebrateSuccess();
        // Auto-speak result for illiterate farmers
        const topCropSpeak = data.central_coordinator?.final_crop || 'crop';
        const scoreSpeak = data.central_coordinator?.overall_score || '';
        autoSpeak(`AI recommends growing ${topCropSpeak}! Score: ${scoreSpeak} out of 10. ${data.central_coordinator?.reasoning || ''}`);
        // Add speaker button
        addSpeakerButton(container, `Recommended crop: ${topCropSpeak}. Score: ${scoreSpeak} out of 10. ${data.agents?.farmer_advisor?.advice || ''}`);
        // Save locally
        const rec = { ...data, timestamp: new Date().toISOString() };
        state.recommendations.unshift(rec);
        if (state.recommendations.length > 20) state.recommendations.pop();
        localStorage.setItem('agri_recommendations', JSON.stringify(state.recommendations));
        document.getElementById('stat-recs').textContent = state.recommendations.length;
    } catch (err) {
        // Try fallback simple recommendation
        try {
            const data = await fetchAPI('/recommendation', {
                username: state.user?.username || 'anonymous',
                land_size: state.farmSetup.land_size,
                soil_type: state.farmSetup.soil_type,
                crop_preference: state.farmSetup.crop_preference
            });
            renderSimpleRecommendation(data, container);
            state.recommendations.unshift({ ...data, timestamp: new Date().toISOString() });
            localStorage.setItem('agri_recommendations', JSON.stringify(state.recommendations));
        } catch (err2) {
            container.innerHTML = `<div class="card" style="color:var(--farm-red)"><p><i class="fas fa-exclamation-triangle"></i> Could not get recommendations. ${err2.message || 'Please try again.'}</p></div>`;
        }
    } finally {
        hideLoading();
    }
}

function renderRecommendation(data, container) {
    let html = '';
    const topCrop = data.central_coordinator?.final_crop || 'Unknown';
    const finalScore = data.central_coordinator?.overall_score || 0;
    const confidence = data.central_coordinator?.confidence_level || 'Medium';
    const agents = data.agents || {};
    const coord = data.central_coordinator || {};

    // ── 1. Visual Score Hero (icon-heavy for illiterate farmers) ──
    const scoreColor = finalScore >= 7 ? '#16a34a' : finalScore >= 5 ? '#eab308' : '#dc2626';
    html += `<div class="rec-hero animate-scale-in" style="background:linear-gradient(135deg,${scoreColor}15,${scoreColor}05);border:2px solid ${scoreColor}30;border-radius:20px;padding:1.5rem;margin-bottom:1.5rem">
        <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
            <div style="width:80px;height:80px;border-radius:50%;background:${scoreColor};color:#fff;display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:800;flex-shrink:0">${finalScore}</div>
            <div style="flex:1;min-width:150px">
                <div style="font-size:1.5rem;font-weight:800;color:#1e293b">🌾 ${topCrop}</div>
                <div style="font-size:0.95rem;color:#64748b;margin-top:4px">
                    ${confidence === 'High' ? '✅' : confidence === 'Medium' ? '⚠️' : '❌'} ${confidence} Confidence
                </div>
            </div>
        </div>
    </div>`;

    // ── 2. Visual Score Bars (understandable without reading) ──
    const scoreData = [];
    if (agents.farmer_advisor?.confidence) scoreData.push({ emoji: '🚜', label: 'Crop Match', val: agents.farmer_advisor.confidence, max: 100 });
    if (agents.market_researcher?.market_score) scoreData.push({ emoji: '💰', label: 'Market', val: agents.market_researcher.market_score * 10, max: 100 });
    if (agents.weather_analyst?.weather_score) scoreData.push({ emoji: '🌤️', label: 'Weather', val: agents.weather_analyst.weather_score * 10, max: 100 });
    if (agents.sustainability_expert?.sustainability_score) scoreData.push({ emoji: '🌱', label: 'Sustainability', val: agents.sustainability_expert.sustainability_score * 10, max: 100 });

    if (scoreData.length) {
        html += `<div class="card mb-4" style="margin-bottom:1.5rem"><h3 class="card-title"><i class="fas fa-chart-bar"></i> ${t('dash.recommendations', state.language)} — Visual Scores</h3>`;
        html += '<div class="visual-scores" style="display:grid;gap:0.75rem;padding:0.5rem 0">';
        scoreData.forEach(s => {
            const pct = Math.min(100, Math.max(0, s.val));
            const barColor = pct >= 70 ? '#16a34a' : pct >= 50 ? '#eab308' : '#dc2626';
            html += `<div class="score-bar-row" style="display:flex;align-items:center;gap:0.75rem">
                <span style="font-size:1.5rem;width:2rem;text-align:center">${s.emoji}</span>
                <span style="width:90px;font-size:0.85rem;font-weight:600;color:#334155">${s.label}</span>
                <div style="flex:1;height:22px;background:#f1f5f9;border-radius:12px;overflow:hidden;position:relative">
                    <div style="height:100%;width:${pct}%;background:${barColor};border-radius:12px;transition:width 1s ease"></div>
                </div>
                <span style="width:40px;font-weight:700;font-size:0.9rem;color:${barColor};text-align:right">${Math.round(pct)}%</span>
            </div>`;
        });
        html += '</div></div>';
    }

    // ── 3. Charts row: Radar + Bar ──
    html += `<div class="rec-charts-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-bottom:1.5rem">`;
    if (data.chart_data?.length) {
        html += `<div class="card"><h3 class="card-title"><i class="fas fa-chart-pie"></i> Score Analysis</h3><div id="rec-radar-chart" class="chart-container" style="min-height:300px"></div></div>`;
        html += `<div class="card"><h3 class="card-title"><i class="fas fa-chart-bar"></i> Agent Comparison</h3><div id="rec-bar-chart" class="chart-container" style="min-height:300px"></div></div>`;
    }
    html += '</div>';

    // ── 4. Agent Discussion Panel — shows a natural "conversation" ──
    html += `<div class="card mb-4" style="margin-bottom:1.5rem">
        <h3 class="card-title"><i class="fas fa-comments"></i> Agent Discussion</h3>
        <p style="font-size:0.85rem;color:#64748b;margin-bottom:1rem">5 AI experts analysed your farm data and discussed to reach this recommendation:</p>
        <div class="agent-discussion" style="display:flex;flex-direction:column;gap:0.75rem">`;

    const agentMeta = {
        farmer_advisor:        { icon: '🚜', color: '#16a34a', label: 'Farmer Advisor',  bg: '#f0fdf4' },
        market_researcher:     { icon: '💰', color: '#d97706', label: 'Market Researcher', bg: '#fffbeb' },
        weather_analyst:       { icon: '🌤️', color: '#2563eb', label: 'Weather Analyst',  bg: '#eff6ff' },
        sustainability_expert: { icon: '🌱', color: '#059669', label: 'Sustainability Expert', bg: '#ecfdf5' }
    };

    // Farmer Advisor speaks first
    if (agents.farmer_advisor) {
        const a = agents.farmer_advisor;
        html += buildDiscussionBubble(agentMeta.farmer_advisor,
            `Based on your soil and climate data, I recommend <strong>${a.recommended_crop}</strong> with ${a.confidence}% confidence. ${a.advice || ''} ${a.reasoning || ''}`);
    }

    // Market Researcher responds
    if (agents.market_researcher) {
        const a = agents.market_researcher;
        html += buildDiscussionBubble(agentMeta.market_researcher,
            `Looking at market trends for ${topCrop}: Market score is <strong>${a.market_score}/10</strong>, price trend is <strong>${a.price_trend}</strong>. ${a.advice || ''} ${a.reasoning || ''}`);
    }

    // Weather Analyst weighs in
    if (agents.weather_analyst) {
        const a = agents.weather_analyst;
        html += buildDiscussionBubble(agentMeta.weather_analyst,
            `Weather suitability: <strong>${a.weather_score}/10</strong>, risk level: <strong>${a.risk_level}</strong>. ${a.forecast || ''} ${a.advice || ''} ${a.reasoning || ''}`);
    }

    // Sustainability Expert
    if (agents.sustainability_expert) {
        const a = agents.sustainability_expert;
        html += buildDiscussionBubble(agentMeta.sustainability_expert,
            `Sustainability score: <strong>${a.sustainability_score}/10</strong>, environmental impact: <strong>${a.environmental_impact}</strong>. ${a.recommendations || ''} ${a.advice || ''}`);
    }

    // Central Coordinator synthesis — the final word
    if (coord.reasoning || coord.action_plan) {
        html += `<div style="border-left:3px solid #7c3aed;padding:1rem;background:#f5f3ff;border-radius:0 12px 12px 0;margin-top:0.5rem">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem">
                <span style="font-size:1.3rem">🧠</span>
                <strong style="color:#7c3aed">Central Coordinator (Final Synthesis)</strong>
            </div>
            <div style="font-size:0.9rem;color:#334155;line-height:1.6">
                ${coord.reasoning || ''}
                ${coord.risk_summary ? `<br><strong>⚠️ Risk Summary:</strong> ${coord.risk_summary}` : ''}
                ${coord.conflicts_resolved && coord.conflicts_resolved !== 'None' ? `<br><strong>🔄 Conflicts Resolved:</strong> ${coord.conflicts_resolved}` : ''}
            </div>
        </div>`;
    }

    html += '</div></div>';

    // ── 5. Action Plan (visual steps) ──
    if (coord.action_plan) {
        html += `<div class="card mb-4" style="margin-bottom:1.5rem">
            <h3 class="card-title"><i class="fas fa-clipboard-list"></i> Action Plan</h3>
            <div style="white-space:pre-line;font-size:0.9rem;line-height:1.7;color:#334155">${coord.action_plan}</div>
        </div>`;
    }

    // ── 6. Key Factors & Warnings ──
    if (coord.key_factors?.length || coord.action_items?.length) {
        html += '<div class="rec-info-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin-bottom:1.5rem">';
        if (coord.key_factors?.length) {
            html += `<div class="card"><h3 class="card-title"><i class="fas fa-key"></i> Key Factors</h3><ul style="padding-left:1.25rem;margin:0">`;
            coord.key_factors.forEach(f => { if (f) html += `<li style="margin-bottom:0.4rem;font-size:0.9rem">${f}</li>`; });
            html += '</ul></div>';
        }
        if (coord.action_items?.length) {
            html += `<div class="card"><h3 class="card-title"><i class="fas fa-exclamation-triangle" style="color:#d97706"></i> Warnings & Alerts</h3><ul style="padding-left:1.25rem;margin:0">`;
            coord.action_items.forEach(item => { if (item) html += `<li style="margin-bottom:0.4rem;font-size:0.9rem;color:#92400e">${item}</li>`; });
            html += '</ul></div>';
        }
        html += '</div>';
    }

    // ── 7. Agent detail cards (expandable) ──
    html += '<div class="agent-results-grid">';
    for (const [key, agent] of Object.entries(agents)) {
        const meta = agentMeta[key] || { icon: '🤖', color: '#16a34a', label: key, bg: '#f0fdf4' };
        html += `<div class="agent-card animate-fade-in">
            <div class="agent-card-header">
                <div class="agent-avatar" style="background:${meta.color};color:#fff;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem">${meta.icon}</div>
                <span class="agent-name">${meta.label}</span>
            </div>
            <div class="agent-body">${formatAgentContent(agent)}</div>
        </div>`;
    }
    html += '</div>';

    container.innerHTML = html;

    // ── Draw Charts ──
    if (data.chart_data?.length) {
        const cd = data.chart_data[0];
        // Radar chart
        Plotly.newPlot('rec-radar-chart', [{
            type: 'scatterpolar',
            r: [...cd.values, cd.values[0]],
            theta: [...cd.labels, cd.labels[0]],
            fill: 'toself',
            fillcolor: 'rgba(22,163,74,0.15)',
            line: { color: '#16a34a', width: 2 },
            marker: { size: 6 }
        }], {
            polar: { radialaxis: { visible: true, range: [0, 100] } },
            margin: { t: 20, b: 20, l: 50, r: 50 },
            paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
            font: { family: 'Inter', size: 11 }
        }, { responsive: true, displayModeBar: false });

        // Bar chart — visual comparison
        const barLabels = cd.labels;
        const barValues = cd.values;
        const barColors = barValues.map(v => v >= 70 ? '#16a34a' : v >= 50 ? '#eab308' : '#dc2626');
        Plotly.newPlot('rec-bar-chart', [{
            x: barLabels,
            y: barValues,
            type: 'bar',
            marker: { color: barColors, cornerradius: 8 },
            text: barValues.map(v => `${v}%`),
            textposition: 'outside',
            textfont: { size: 12, color: '#334155' }
        }], {
            yaxis: { range: [0, 110], title: '', showgrid: true, gridcolor: '#f1f5f9' },
            xaxis: { title: '' },
            margin: { t: 20, b: 60, l: 40, r: 20 },
            paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
            font: { family: 'Inter', size: 11 },
            bargap: 0.3
        }, { responsive: true, displayModeBar: false });
    }
}

function buildDiscussionBubble(meta, message) {
    return `<div style="display:flex;gap:0.75rem;align-items:flex-start">
        <div style="width:40px;height:40px;border-radius:50%;background:${meta.bg};display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0;border:2px solid ${meta.color}30">${meta.icon}</div>
        <div style="flex:1;background:${meta.bg};border:1px solid ${meta.color}20;border-radius:4px 16px 16px 16px;padding:0.75rem 1rem">
            <div style="font-weight:700;font-size:0.8rem;color:${meta.color};margin-bottom:0.3rem">${meta.label}</div>
            <div style="font-size:0.88rem;line-height:1.55;color:#334155">${message}</div>
        </div>
    </div>`;
}

function formatAgentContent(agent) {
    let lines = [];
    if (agent.recommended_crop) lines.push(`<strong>Crop:</strong> ${agent.recommended_crop}`);
    if (agent.confidence) lines.push(`<strong>Confidence:</strong> ${agent.confidence}%`);
    if (agent.market_score) lines.push(`<strong>Market Score:</strong> ${agent.market_score}/10`);
    if (agent.price_trend) lines.push(`<strong>Price Trend:</strong> ${agent.price_trend}`);
    if (agent.weather_score) lines.push(`<strong>Weather Score:</strong> ${agent.weather_score}/10`);
    if (agent.risk_level) lines.push(`<strong>Risk:</strong> ${agent.risk_level}`);
    if (agent.forecast) lines.push(`${agent.forecast}`);
    if (agent.sustainability_score) lines.push(`<strong>Sustainability:</strong> ${agent.sustainability_score}/10`);
    if (agent.environmental_impact) lines.push(`<strong>Impact:</strong> ${agent.environmental_impact}`);
    if (agent.advice) lines.push(`${agent.advice}`);
    if (agent.reasoning) lines.push(`<em>${agent.reasoning}</em>`);
    return lines.join('<br>');
}

function renderSimpleRecommendation(data, container) {
    let html = `<div class="card"><h3 class="card-title"><i class="fas fa-clipboard-check"></i> AI Recommendation</h3>`;
    html += `<div class="agent-body" style="white-space:pre-line">${data.recommendation || 'No data'}</div></div>`;
    if (data.chart_data?.length) {
        html += '<div class="card mt-4"><h3 class="card-title"><i class="fas fa-chart-bar"></i> Crop Analysis</h3><div id="rec-simple-chart" class="chart-container"></div></div>';
    }
    container.innerHTML = html;
    if (data.chart_data?.length) {
        const traces = data.chart_data.map(cd => ({
            type: 'scatterpolar',
            name: cd.crop,
            r: [...cd.values, cd.values[0]],
            theta: [...cd.labels, cd.labels[0]],
            fill: 'toself'
        }));
        Plotly.newPlot('rec-simple-chart', traces, {
            polar: { radialaxis: { visible: true, range: [0, 100] } },
            margin: { t: 30, b: 30, l: 50, r: 50 },
            paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
            font: { family: 'Inter' }
        }, { responsive: true, displayModeBar: false });
    }
}

// ═══════════════════════════════════════
//  CROP ROTATION
// ═══════════════════════════════════════

async function generateRotationPlan() {
    const crop = document.getElementById('current-crop').value;
    showLoading('Generating rotation plan...');
    try {
        const data = await fetchAPI('/crop_rotation', { current_crop: crop, years: 4 });
        const container = document.getElementById('rotation-results');
        let html = `<div class="card mt-4"><h3 class="card-title"><i class="fas fa-calendar-check"></i> Rotation Plan for ${crop}</h3>`;
        html += `<div class="agent-body" style="white-space:pre-line">${data.plan}</div></div>`;
        container.innerHTML = html;

        // Timeline chart
        if (data.timeline) {
            Plotly.newPlot('rotation-timeline-chart', [{
                x: data.timeline.years,
                y: data.timeline.scores,
                type: 'bar',
                marker: {
                    color: data.timeline.scores.map((_, i) => ['#16a34a', '#0ea5e9', '#eab308', '#8b5cf6'][i % 4]),
                    cornerradius: 8
                },
                text: data.timeline.crops.map(c => c.split(': ')[1] || c),
                textposition: 'outside'
            }], {
                yaxis: { title: 'Soil Health Score', range: [0, 100] },
                margin: { t: 20, b: 40, l: 50, r: 20 },
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                font: { family: 'Inter' }
            }, { responsive: true, displayModeBar: false });
        }
    } catch (err) {
        toast('Failed to generate rotation plan', 'error');
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════
//  FERTILIZER CALCULATOR
// ═══════════════════════════════════════

async function calculateFertilizer() {
    const soil = document.getElementById('fert-soil').value;
    const crop = document.getElementById('fert-crop').value;
    const land = parseFloat(document.getElementById('fert-land').value) || 5;
    showLoading('Calculating fertilizer needs...');
    try {
        const data = await fetchAPI('/fertilizer', { land_size: land, soil_type: soil, crop_type: crop });
        const container = document.getElementById('fertilizer-results');
        container.innerHTML = `<div class="npk-cards mt-4">
            <div class="npk-card n-card"><div class="npk-value">${data.nitrogen_kg}</div><div class="npk-label">Nitrogen (kg)</div></div>
            <div class="npk-card p-card"><div class="npk-value">${data.phosphorus_kg}</div><div class="npk-label">Phosphorus (kg)</div></div>
            <div class="npk-card k-card"><div class="npk-value">${data.potassium_kg}</div><div class="npk-label">Potassium (kg)</div></div>
        </div>`;

        Plotly.react('fertilizer-chart', [{
            values: [data.nitrogen_kg, data.phosphorus_kg, data.potassium_kg],
            labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'],
            type: 'pie',
            marker: { colors: ['#16a34a', '#0ea5e9', '#8b5cf6'] },
            hole: 0.45,
            textinfo: 'label+percent'
        }], {
            margin: { t: 20, b: 20, l: 20, r: 20 },
            paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
            font: { family: 'Inter' },
            showlegend: false
        }, { responsive: true, displayModeBar: false });
    } catch {
        toast('Failed to calculate fertilizer', 'error');
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════
//  FARM MAP (Leaflet)
// ═══════════════════════════════════════

function createFarmMap() {
    const lat = parseFloat(document.getElementById('farm-lat').value) || 12.9716;
    const lon = parseFloat(document.getElementById('farm-lon').value) || 77.5946;
    const container = document.getElementById('farm-map-container');
    container.innerHTML = ''; // reset

    if (state.leafletMap) { state.leafletMap.remove(); state.leafletMap = null; }

    state.leafletMap = L.map(container).setView([lat, lon], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(state.leafletMap);

    // Farm center marker
    L.marker([lat, lon]).addTo(state.leafletMap)
        .bindPopup(`<b>Farm Center</b><br>Lat: ${lat}<br>Lon: ${lon}`).openPopup();

    // Simulated soil zones
    const zones = [
        { offset: [0.005, 0.005], color: '#8B4513', label: 'Clay Zone', radius: 200 },
        { offset: [-0.004, 0.006], color: '#C2B280', label: 'Sandy Zone', radius: 180 },
        { offset: [0.003, -0.004], color: '#228B22', label: 'Loamy Zone', radius: 250 },
        { offset: [-0.006, -0.003], color: '#dc2626', label: 'Erosion Risk', radius: 120 },
        { offset: [0.007, 0.002], color: '#2563eb', label: 'Waterlogging Risk', radius: 100 }
    ];
    zones.forEach(z => {
        L.circle([lat + z.offset[0], lon + z.offset[1]], { color: z.color, fillColor: z.color, fillOpacity: 0.25, radius: z.radius })
            .addTo(state.leafletMap).bindPopup(z.label);
    });

    // Show recommendations
    const recCard = document.getElementById('map-recs-card');
    recCard.style.display = '';
    document.getElementById('map-rec-content').innerHTML = `
        <ul style="padding-left:1.25rem;font-size:0.9rem;line-height:1.8">
            <li><strong>Clay zone:</strong> Good for rice and wheat — ensure drainage</li>
            <li><strong>Sandy zone:</strong> Ideal for root crops — add organic matter</li>
            <li><strong>Loamy zone:</strong> Versatile — great for most crops</li>
            <li><strong>Erosion risk:</strong> Plant cover crops, build terraces</li>
            <li><strong>Waterlogging:</strong> Improve drainage; avoid flood-sensitive crops</li>
        </ul>`;
    toast('Farm map created! 🗺️', 'success');
}

async function loadSavedMap() {
    try {
        const data = await fetch(`${API}/farm_map/${state.user?.username || 'anonymous'}`).then(r => r.json());
        if (data.map_data) {
            document.getElementById('farm-lat').value = data.map_data.lat || 12.9716;
            document.getElementById('farm-lon').value = data.map_data.lon || 77.5946;
            createFarmMap();
            toast('Map loaded', 'success');
        } else {
            toast('No saved map found', 'info');
        }
    } catch { toast('Could not load map', 'error'); }
}

async function saveFarmMap() {
    try {
        await fetchAPI('/farm_map', {
            username: state.user?.username || 'anonymous',
            farm_name: state.user?.farm_name || 'My Farm',
            map_data: { lat: parseFloat(document.getElementById('farm-lat').value), lon: parseFloat(document.getElementById('farm-lon').value) },
            recommendations: [],
            risk_areas: []
        });
        toast('Map saved! 💾', 'success');
    } catch { toast('Could not save map', 'error'); }
}

// ═══════════════════════════════════════
//  SUSTAINABILITY
// ═══════════════════════════════════════

async function logSustainability() {
    const water_score = parseFloat(document.getElementById('water-usage').value) || 2;
    const fertilizer_use = parseFloat(document.getElementById('fertilizer-use').value) || 1.5;
    const rotation = document.getElementById('crop-rotation').value === 'yes';
    showLoading('Logging sustainability data...');
    try {
        const data = await fetchAPI('/sustainability', {
            username: state.user?.username || 'anonymous',
            water_score, fertilizer_use, rotation
        });
        document.getElementById('stat-sustain').textContent = `${data.score}%`;

        // Tips
        const tipsEl = document.getElementById('sustainability-tips');
        let tipsHtml = '<h3 class="card-title"><i class="fas fa-lightbulb"></i> Improvement Tips</h3>';
        if (data.tips?.length) {
            tipsHtml += '<ul style="padding-left:1.25rem;font-size:0.9rem;line-height:1.8">';
            data.tips.forEach(t => tipsHtml += `<li>${t}</li>`);
            tipsHtml += '</ul>';
        } else {
            tipsHtml += '<p style="color:var(--farm-green);font-weight:600">🎉 Great work! Your practices are sustainable.</p>';
        }
        tipsEl.innerHTML = tipsHtml;
        loadSustainabilityChart();
        toast(`Sustainability score: ${data.score}%`, 'success');
    } catch {
        toast('Failed to log data', 'error');
    } finally {
        hideLoading();
    }
}

async function loadSustainabilityChart() {
    try {
        const data = await fetch(`${API}/sustainability/scores?username=${state.user?.username || 'anonymous'}`).then(r => r.json());
        if (data.timestamps?.length) {
            requestAnimationFrame(() => {
                Plotly.react('sustainability-trend-chart', [{
                    x: data.timestamps, y: data.scores,
                    type: 'scatter', mode: 'lines+markers',
                    line: { color: '#16a34a', width: 3, shape: 'spline' },
                    marker: { size: 8, color: '#16a34a' },
                    fill: 'tozeroy', fillcolor: 'rgba(22,163,74,0.08)'
                }], {
                    yaxis: { title: 'Score', range: [0, 100] },
                    xaxis: { title: 'Date' },
                    margin: { t: 10, b: 40, l: 50, r: 20 },
                    paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                    font: { family: 'Inter' }
                }, { responsive: true, displayModeBar: false, staticPlot: false });
            });
        }
    } catch { /* offline ok */ }
}

// ═══════════════════════════════════════
//  COMMUNITY
// ═══════════════════════════════════════

async function shareCommunityData() {
    showLoading('Sharing your data...');
    try {
        await fetchAPI('/community', {
            username: state.user?.username || 'anonymous',
            crop_type: document.getElementById('community-crop').value,
            yield_data: parseFloat(document.getElementById('community-yield').value) || 0,
            market_price: parseFloat(document.getElementById('community-price').value) || 0,
            region: document.getElementById('community-region').value,
            season: document.getElementById('community-season').value,
            sustainability_practice: document.getElementById('community-practice').value
        });
        toast('Data shared with the community! 🤝', 'success');
        addActivity('Shared data with community', 'blue');
        loadCommunityInsights();
        loadMyPosts();
    } catch {
        toast('Could not share data', 'error');
    } finally {
        hideLoading();
    }
}

async function loadCommunityInsights() {
    try {
        const data = await fetch(`${API}/community/insights`).then(r => r.json());
        if (!data.insights?.length) return;
        const crops = data.insights.map(i => i.crop_type);
        const yields = data.insights.map(i => i.avg_yield);
        requestAnimationFrame(() => {
            Plotly.newPlot('community-chart', [{
                x: crops, y: yields,
                type: 'bar',
                marker: { color: crops.map((_, i) => ['#16a34a', '#0ea5e9', '#eab308', '#8b5cf6', '#ef4444'][i % 5]), cornerradius: 8 },
                text: yields.map(y => `${y} t/ha`),
                textposition: 'outside'
            }], {
                yaxis: { title: 'Avg Yield (t/ha)' },
                margin: { t: 10, b: 40, l: 50, r: 20 },
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                font: { family: 'Inter' }
            }, { responsive: true, displayModeBar: false });
        });
    } catch { /* offline ok */ }
    // Also load user's posts
    loadMyPosts();
}

async function loadMyPosts() {
    const container = document.getElementById('my-community-posts');
    if (!container) return;
    try {
        const data = await fetch(`${API}/community/my_posts?username=${encodeURIComponent(state.user?.username || 'anonymous')}`).then(r => r.json());
        if (!data.posts?.length) {
            container.innerHTML = '<p class="muted-text">You haven\'t shared any data yet. Share your first post above!</p>';
            return;
        }
        let html = '<div class="my-posts-list">';
        data.posts.forEach(p => {
            const date = p.created_at ? new Date(p.created_at).toLocaleDateString() : '';
            html += `<div class="my-post-card">
                <div class="my-post-header">
                    <strong>${p.crop_type}</strong>
                    <small>${date}</small>
                </div>
                <div class="my-post-details">
                    <span><i class="fas fa-wheat-awn"></i> ${p.yield_data} t/ha</span>
                    <span><i class="fas fa-rupee-sign"></i> ₹${p.market_price?.toLocaleString()}/ton</span>
                    <span><i class="fas fa-map-marker-alt"></i> ${p.region}</span>
                    <span><i class="fas fa-leaf"></i> ${p.practice}</span>
                </div>
            </div>`;
        });
        html += '</div>';
        container.innerHTML = html;
    } catch {
        container.innerHTML = '<p class="muted-text">Could not load your posts.</p>';
    }
}

// ═══════════════════════════════════════
//  MARKET FORECAST
// ═══════════════════════════════════════

async function generateMarketForecast() {
    const crop = document.getElementById('market-crop').value;
    const period = document.getElementById('forecast-period').value;
    showLoading('Generating market forecast...');
    try {
        const data = await fetch(`${API}/market/dashboard?crop=${encodeURIComponent(crop)}&period=${period}%20months`).then(r => r.json());
        if (data.forecast?.length) {
            const months = data.forecast.map(f => f.month_name || f.month);
            const prices = data.forecast.map(f => f.price);
            const confs = data.forecast.map(f => f.confidence * 100);
            Plotly.newPlot('market-price-chart', [
                { x: months, y: prices, type: 'scatter', mode: 'lines+markers', name: 'Price (₹/ton)', line: { color: '#16a34a', width: 3, shape: 'spline' }, marker: { size: 8 } },
                { x: months, y: confs, type: 'scatter', mode: 'lines', name: 'Confidence %', line: { color: '#0ea5e9', width: 2, dash: 'dot' }, yaxis: 'y2' }
            ], {
                yaxis: { title: '₹/ton' },
                yaxis2: { title: 'Confidence %', overlaying: 'y', side: 'right', range: [0, 100] },
                margin: { t: 10, b: 40, l: 60, r: 60 },
                legend: { orientation: 'h', y: -0.15 },
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                font: { family: 'Inter' }
            }, { responsive: true, displayModeBar: false });
        }
        // Insights
        const insEl = document.getElementById('market-insights');
        insEl.innerHTML = `<h3 class="card-title"><i class="fas fa-lightbulb"></i> Market Insights</h3>
            <ul style="padding-left:1.25rem;font-size:0.9rem;line-height:1.8">
                <li><strong>Current Price:</strong> ₹${data.current_price?.toLocaleString()}/ton</li>
                <li><strong>Predicted:</strong> ₹${data.predicted_price?.toLocaleString()}/ton</li>
                <li><strong>Change:</strong> <span style="color:${data.price_change_percent >= 0 ? 'var(--farm-green)' : 'var(--farm-red)'}">${data.price_change_percent >= 0 ? '▲' : '▼'} ${Math.abs(data.price_change_percent)}%</span></li>
                <li><strong>Recommendation:</strong> ${data.recommendation}</li>
                <li>${data.analysis}</li>
            </ul>`;
        toast('Market forecast generated 📈', 'success');
    } catch {
        toast('Could not generate forecast', 'error');
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════
//  CHATBOT
// ═══════════════════════════════════════

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query) return;
    input.value = '';
    const messages = document.getElementById('chat-messages');

    // User message
    messages.innerHTML += `<div class="chat-msg user"><div class="chat-avatar"><i class="fas fa-user"></i></div><div class="chat-bubble">${escapeHtml(query)}</div></div>`;
    // Typing indicator
    messages.innerHTML += `<div class="chat-msg ai" id="typing-indicator"><div class="chat-avatar"><i class="fas fa-robot"></i></div><div class="chat-bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div></div>`;
    messages.scrollTop = messages.scrollHeight;

    try {
        const data = await fetchAPI('/chatbot/ask', { username: state.user?.username || 'anonymous', query });
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
        const responseHtml = (data.response || 'Sorry, I could not process that.').replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        messages.innerHTML += `<div class="chat-msg ai animate-fade-in"><div class="chat-avatar"><i class="fas fa-robot"></i></div><div class="chat-bubble">${responseHtml}</div></div>`;
    } catch {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
        messages.innerHTML += `<div class="chat-msg ai"><div class="chat-avatar"><i class="fas fa-robot"></i></div><div class="chat-bubble">Sorry, I'm offline right now. Please try again when connected.</div></div>`;
    }
    messages.scrollTop = messages.scrollHeight;
}

// ═══════════════════════════════════════
//  WEATHER
// ═══════════════════════════════════════

async function getWeatherForecast() {
    const lat = parseFloat(document.getElementById('weather-lat').value) || 12.9716;
    const lon = parseFloat(document.getElementById('weather-lon').value) || 77.5946;
    const crop = document.getElementById('weather-crop').value;
    showLoading('Fetching real-time weather...');
    try {
        const data = await fetchAPI('/weather', { lat, lon, crop_type: crop });
        const container = document.getElementById('weather-results');
        // Current weather card
        let html = `<div class="card"><h3 class="card-title"><i class="fas fa-sun"></i> Current Weather — ${data.current_weather?.city || ''}</h3>
            <div class="stat-grid">
                <div class="stat-card stat-green"><i class="fas fa-thermometer-half stat-icon"></i><div class="stat-value">${Math.round(data.current_weather?.temperature || 0)}°C</div><div class="stat-label">Temperature</div></div>
                <div class="stat-card stat-blue"><i class="fas fa-tint stat-icon"></i><div class="stat-value">${data.current_weather?.humidity || 0}%</div><div class="stat-label">Humidity</div></div>
                <div class="stat-card stat-amber"><i class="fas fa-wind stat-icon"></i><div class="stat-value">${data.current_weather?.wind_speed || 0}</div><div class="stat-label">Wind (m/s)</div></div>
                <div class="stat-card stat-purple"><i class="fas fa-cloud stat-icon"></i><div class="stat-value">${data.current_weather?.clouds || 0}%</div><div class="stat-label">Clouds</div></div>
            </div></div>`;

        // Agricultural conditions
        const risk = data.agricultural_conditions?.overall_risk || 'unknown';
        const riskClass = risk === 'low' ? 'low-risk' : risk === 'medium' ? 'medium-risk' : 'high-risk';
        html += `<div class="weather-risk-cards">
            <div class="risk-card ${riskClass}"><i class="fas fa-shield-alt"></i><br>Risk: ${risk.toUpperCase()}</div>
            <div class="risk-card low-risk"><i class="fas fa-thermometer-half"></i><br>Avg: ${data.metrics?.avg_temperature || '—'}°C</div>
            <div class="risk-card low-risk"><i class="fas fa-cloud-rain"></i><br>Rain: ${data.metrics?.total_rainfall || '0'}mm</div>
        </div>`;

        // Recommendations
        if (data.recommendations?.length) {
            html += `<div class="card mt-4"><h3 class="card-title"><i class="fas fa-exclamation-circle"></i> Agricultural Advisories</h3><ul style="padding-left:1.25rem;font-size:0.9rem;line-height:1.8">`;
            data.recommendations.forEach(r => html += `<li>${r}</li>`);
            html += '</ul></div>';
        }
        container.innerHTML = html;

        // Forecast chart
        if (data.forecast?.length) {
            const times = data.forecast.map(f => f.datetime);
            const temps = data.forecast.map(f => f.temperature);
            const hums = data.forecast.map(f => f.humidity);
            Plotly.newPlot('weather-forecast-chart', [
                { x: times, y: temps, name: 'Temp °C', type: 'scatter', mode: 'lines+markers', line: { color: '#ef4444', width: 2 } },
                { x: times, y: hums, name: 'Humidity %', type: 'scatter', mode: 'lines', line: { color: '#0ea5e9', width: 2, dash: 'dot' }, yaxis: 'y2' }
            ], {
                yaxis: { title: 'Temperature (°C)' },
                yaxis2: { title: 'Humidity (%)', overlaying: 'y', side: 'right' },
                margin: { t: 10, b: 40, l: 50, r: 50 },
                legend: { orientation: 'h', y: -0.15 },
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                font: { family: 'Inter' }
            }, { responsive: true, displayModeBar: false });
        }
        toast('Weather data updated 🌤️', 'success');
        // Auto-speak weather for illiterate farmers
        const weatherSpeech = `Current temperature is ${Math.round(data.current_weather?.temperature || 0)} degrees, humidity ${data.current_weather?.humidity || 0} percent. Risk level: ${data.agricultural_conditions?.overall_risk || 'unknown'}. ${data.recommendations?.[0] || ''}`;
        autoSpeak(weatherSpeech);
        addSpeakerButton(container, weatherSpeech);
    } catch {
        toast('Weather service unavailable', 'error');
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════
//  SOIL ANALYSIS
// ═══════════════════════════════════════

function previewSoilPhoto(input) {
    if (!input.files?.[0]) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('soil-preview');
        preview.innerHTML = `<img src="${e.target.result}" alt="Soil" style="max-height:180px;border-radius:12px;margin:0 auto">`;
        preview.style.display = '';
    };
    reader.readAsDataURL(input.files[0]);
}

async function analyzeSoil() {
    const fileInput = document.getElementById('soil-photo');
    if (!fileInput.files?.[0]) { toast('Please upload a soil photo', 'info'); return; }
    showLoading('AI is analyzing your soil...');
    try {
        const formData = new FormData();
        formData.append('soil_photo', fileInput.files[0]);
        const res = await fetch(`${API}/soil_analysis`, { method: 'POST', body: formData });
        const text = await res.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch {
            throw new Error('Server error — please try again later');
        }
        if (!res.ok) throw new Error(data.detail || 'Analysis failed');
        showSoilResult(data.soil_type);
        celebrateSuccess();
        addActivity('Soil analysis completed', 'green');
    } catch (err) {
        toast(err.message || 'Soil analysis failed', 'error');
    } finally {
        hideLoading();
    }
}

function selectSoilType(type) {
    document.querySelectorAll('.soil-opt').forEach(o => o.classList.remove('selected'));
    event.currentTarget.classList.add('selected');
    showSoilResult(type);
}

function showSoilResult(soilType) {
    const info = {
        Loamy: { color: '#8B7355', desc: 'Best all-around soil. Rich in nutrients with good drainage. Ideal for wheat, corn, vegetables.' },
        Sandy: { color: '#C2B280', desc: 'Drains quickly, warms fast in spring. Good for root crops, groundnut, watermelon.' },
        Clay: { color: '#8B4513', desc: 'Heavy, retains water. Excellent for rice and wheat. Add organic matter for better structure.' },
        Black: { color: '#3B3131', desc: 'Rich in calcium and magnesium. Ideal for cotton, soybean, and citrus. Good water retention.' },
        Red: { color: '#A0522D', desc: 'Iron-rich, slightly acidic. Good for pulses, millets, and groundnut. Add lime to improve pH.' }
    };
    const i = info[soilType] || { color: '#888', desc: 'Unknown soil type.' };
    document.getElementById('soil-results').innerHTML = `
        <div class="card animate-scale-in">
            <h3 class="card-title"><i class="fas fa-check-circle" style="color:var(--farm-green)"></i> Soil Type Detected: <strong>${soilType}</strong></h3>
            <div style="display:flex;align-items:center;gap:1rem;margin:1rem 0">
                <div style="width:64px;height:64px;border-radius:16px;background:${i.color}"></div>
                <p style="font-size:0.92rem;flex:1">${i.desc}</p>
            </div>
            <p class="muted-text">Tip: You can use this soil type in Farm Setup for better AI recommendations.</p>
        </div>`;
    autoSpeak(`Soil type is ${soilType}. ${i.desc}`);
    // Auto-set soil type in farm setup
    const sel = document.getElementById('soil-type');
    for (const opt of sel.options) {
        if (opt.value === soilType) { sel.value = soilType; break; }
    }
}

// ═══════════════════════════════════════
//  PEST PREDICTION
// ═══════════════════════════════════════

async function predictPests() {
    const crop = document.getElementById('pest-crop').value;
    const soil = document.getElementById('pest-soil').value;
    const temp = parseFloat(document.getElementById('pest-temp').value) || 25;
    const humidity = parseFloat(document.getElementById('pest-humidity').value) || 65;
    const rainfall = parseFloat(document.getElementById('pest-rainfall').value) || 500;
    showLoading('Analyzing pest risks...');
    try {
        const data = await fetchAPI('/pest_prediction', { crop_type: crop, soil_type: soil, temperature: temp, humidity, rainfall });
        const container = document.getElementById('pest-results');
        const risk = data.overall_risk || 'low';
        let html = `<div class="card"><h3 class="card-title"><i class="fas fa-shield-alt"></i> Overall Risk: <span style="color:${risk === 'high' ? 'var(--farm-red)' : risk === 'medium' ? 'var(--farm-yellow)' : 'var(--farm-green)'}">${risk.toUpperCase()}</span></h3>
            <p class="muted-text">${data.analysis || ''}</p></div>`;

        if (data.predictions?.length) {
            html += '<div class="pest-grid mt-4">';
            data.predictions.forEach(p => {
                const sev = p.severity || 'low';
                html += `<div class="pest-card ${sev}-risk">
                    <h4>${p.pest}</h4>
                    <span class="pest-risk-badge ${sev}">${sev} risk</span>
                    <p style="margin-top:0.5rem;font-size:0.85rem">Probability: <strong>${Math.round(p.probability * 100)}%</strong></p>
                    <p style="font-size:0.82rem;color:var(--fg-muted);margin-top:0.25rem">${p.recommendation || ''}</p>
                </div>`;
            });
            html += '</div>';
        }

        if (data.prevention_tips?.length) {
            html += `<div class="card mt-4"><h3 class="card-title"><i class="fas fa-lightbulb"></i> Prevention Tips</h3>
                <ul style="padding-left:1.25rem;font-size:0.9rem;line-height:1.8">`;
            data.prevention_tips.forEach(t => html += `<li>${t}</li>`);
            html += '</ul></div>';
        }
        container.innerHTML = html;
        celebrateSuccess();
        toast('Pest analysis complete 🐛', 'success');
        // Auto-speak pest result for illiterate farmers
        let pestSpeech = `Pest risk for ${crop} is ${risk}. `;
        if (data.predictions?.length) pestSpeech += 'Main risks: ' + data.predictions.slice(0, 2).map(p => p.pest).join(' and ') + '. ';
        if (data.prevention_tips?.length) pestSpeech += 'Tip: ' + data.prevention_tips[0];
        autoSpeak(pestSpeech);
        addSpeakerButton(container, pestSpeech);
    } catch {
        toast('Failed to predict pests', 'error');
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════
//  HISTORY
// ═══════════════════════════════════════

async function loadHistory() {
    const container = document.getElementById('history-table-container');
    try {
        const recs = await fetch(`${API}/previous_recommendations?username=${state.user?.username || 'anonymous'}`).then(r => r.json());
        if (recs?.length) {
            let html = '<table class="history-table"><thead><tr><th>Date</th><th>Crop / Type</th><th>Score</th><th>Details</th></tr></thead><tbody>';
            recs.forEach(r => {
                html += `<tr><td>${r.timestamp || '—'}</td><td>${r.crop || '—'}</td><td>${r.score ? Math.round(r.score) : '—'}</td><td style="max-width:300px;font-size:0.82rem">${(r.recommendation || '').substring(0, 120)}...</td></tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;

            // Analytics chart
            Plotly.newPlot('history-analytics-chart', [{
                x: recs.map(r => r.timestamp),
                y: recs.map(r => r.score || 0),
                type: 'scatter', mode: 'lines+markers',
                line: { color: '#16a34a', width: 3 },
                marker: { size: 8 }
            }], {
                yaxis: { title: 'Score' },
                margin: { t: 10, b: 40, l: 50, r: 20 },
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                font: { family: 'Inter' }
            }, { responsive: true, displayModeBar: false });
        } else if (state.recommendations.length) {
            // Use local data
            let html = '<table class="history-table"><thead><tr><th>Date</th><th>Crop</th><th>Score</th></tr></thead><tbody>';
            state.recommendations.forEach(r => {
                const crop = r.central_coordinator?.final_crop || r.recommendation?.substring(0, 30) || '—';
                const score = r.central_coordinator?.overall_score || '—';
                html += `<tr><td>${r.timestamp || '—'}</td><td>${crop}</td><td>${score}</td></tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }
    } catch {
        if (state.recommendations.length) {
            let html = '<table class="history-table"><thead><tr><th>Date</th><th>Crop</th><th>Score</th></tr></thead><tbody>';
            state.recommendations.slice(0, 10).forEach(r => {
                const crop = r.central_coordinator?.final_crop || '—';
                const score = r.central_coordinator?.overall_score || '—';
                html += `<tr><td>${new Date(r.timestamp).toLocaleDateString()}</td><td>${crop}</td><td>${score}</td></tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }
    }
}

function exportRecommendations() {
    if (!state.recommendations.length) { toast('No recommendations to export', 'info'); return; }
    let csv = 'Date,Crop,Score,Details\n';
    state.recommendations.forEach(r => {
        const crop = r.central_coordinator?.final_crop || '—';
        const score = r.central_coordinator?.overall_score || '';
        const details = (r.central_coordinator?.reasoning || '').replace(/,/g, ';').replace(/\n/g, ' ');
        csv += `"${r.timestamp}","${crop}","${score}","${details}"\n`;
    });
    downloadFile(csv, 'agrismart_recommendations.csv', 'text/csv');
    toast('Exported as CSV', 'success');
}

// ═══════════════════════════════════════
//  OFFLINE
// ═══════════════════════════════════════

function setupNetworkListeners() {
    window.addEventListener('online', () => { state.isOffline = false; updateOfflineUI(); toast('Back online! 🌐', 'success'); });
    window.addEventListener('offline', () => { state.isOffline = true; updateOfflineUI(); toast('You are offline — data will sync later', 'info'); });
}

function updateOfflineUI() {
    const bar = document.getElementById('offline-bar');
    if (bar) bar.style.display = state.isOffline ? '' : 'none';
}

function updateOfflinePage() {
    const box = document.getElementById('offline-status-box');
    if (state.isOffline) {
        box.className = 'status-box offline';
        box.innerHTML = '<i class="fas fa-wifi-slash"></i><span>You are offline — basic features available</span>';
    } else {
        box.className = 'status-box online';
        box.innerHTML = '<i class="fas fa-wifi text-green"></i><span>You are online — All features available</span>';
    }
    document.getElementById('offline-recs-count').textContent = state.recommendations.length;
    const pending = JSON.parse(localStorage.getItem('agri_pending_sync') || '[]');
    document.getElementById('offline-pending-count').textContent = pending.length;
}

async function syncOfflineData() {
    if (state.isOffline) { toast('Cannot sync while offline', 'info'); return; }
    showLoading('Syncing data...');
    try {
        const res = await fetch(`${API}/offline/sync/${state.user?.username || 'anonymous'}`, { method: 'POST' });
        const data = await res.json();
        localStorage.setItem('agri_pending_sync', '[]');
        updateOfflinePage();
        toast(`Synced ${data.synced_count || 0} items ✅`, 'success');
    } catch {
        toast('Sync failed — try again later', 'error');
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════
//  PROFILE
// ═══════════════════════════════════════

function switchProfileTab(tab) {
    document.querySelectorAll('.ptab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.ptab-content').forEach(c => c.classList.remove('active'));
    event.currentTarget.classList.add('active');
    document.getElementById(`ptab-${tab}`).classList.add('active');
}

async function loadProfileData() {
    if (!state.user) return;
    // Fill fields
    document.getElementById('farmer-name').value = state.user.username || '';
    document.getElementById('farm-name').value = state.user.farm_name || '';
    document.getElementById('profile-phone').value = state.user.phone || '';
    document.getElementById('profile-email').value = state.user.email || '';
    document.getElementById('profile-location').value = state.user.location || '';
    if (state.farmSetup) {
        document.getElementById('profile-farm-size').value = state.farmSetup.land_size || 5;
    }

    // Try loading from server
    try {
        const data = await fetch(`${API}/user/profile/${state.user.username}`).then(r => r.json());
        if (data.username) {
            document.getElementById('profile-email').value = data.email || '';
            document.getElementById('profile-phone').value = data.phone || '';
            document.getElementById('profile-location').value = data.location || '';
            if (data.experience_level) {
                document.getElementById('experience-level').value = data.experience_level;
            }
            if (data.farm_size) {
                document.getElementById('profile-farm-size').value = data.farm_size;
            }
        }
    } catch { /* offline ok */ }

    // Recent recs
    const recsEl = document.getElementById('profile-recent-recs');
    if (state.recommendations.length) {
        let html = '';
        state.recommendations.slice(0, 5).forEach(r => {
            const crop = r.central_coordinator?.final_crop || r.recommendation?.substring(0, 40) || '—';
            const score = r.central_coordinator?.overall_score || '';
            html += `<div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid var(--border);font-size:0.9rem">
                <span>${crop}</span><span style="font-weight:600">${score ? score + '/10' : ''}</span></div>`;
        });
        recsEl.innerHTML = html;
    }
}

async function saveProfile() {
    showLoading('Saving profile...');
    try {
        await fetchAPI('/user/profile', {
            username: state.user?.username,
            new_username: document.getElementById('farmer-name').value.trim() || undefined,
            farm_name: document.getElementById('farm-name').value.trim() || undefined,
            email: document.getElementById('profile-email').value.trim() || undefined,
            phone: document.getElementById('profile-phone').value.trim() || undefined,
            location: document.getElementById('profile-location').value.trim() || undefined,
            experience_level: document.getElementById('experience-level').value || undefined,
            farm_size: parseFloat(document.getElementById('profile-farm-size').value) || undefined
        }, 'PUT');
        // Update local state
        state.user.farm_name = document.getElementById('farm-name').value.trim();
        state.user.phone = document.getElementById('profile-phone').value.trim();
        state.user.location = document.getElementById('profile-location').value.trim();
        localStorage.setItem('agri_user', JSON.stringify(state.user));
        updateSidebarProfile();
        toast('Profile saved! ✅', 'success');
    } catch {
        toast('Could not save profile', 'error');
    } finally {
        hideLoading();
    }
}

function exportProfileData() {
    const data = {
        user: state.user,
        farmSetup: state.farmSetup,
        recommendations: state.recommendations,
        exportDate: new Date().toISOString()
    };
    downloadFile(JSON.stringify(data, null, 2), 'agrismart_data.json', 'application/json');
    toast('Data exported as JSON', 'success');
}

// ═══════════════════════════════════════
//  LANGUAGE
// ═══════════════════════════════════════

function toggleLangMenu() {
    document.getElementById('lang-menu').classList.toggle('open');
}

function changeLanguage(lang) {
    state.language = lang;
    localStorage.setItem('agri_lang', lang);
    const labels = { en: 'EN', hi: 'हि', kn: 'ಕ', te: 'తె', ta: 'த', ml: 'മ', bn: 'বা', gu: 'ગુ', mr: 'म', pa: 'ਪ', or: 'ଓ' };
    document.getElementById('lang-label').textContent = labels[lang] || lang.toUpperCase();
    document.getElementById('lang-menu').classList.remove('open');
    if (document.getElementById('settings-language')) {
        document.getElementById('settings-language').value = lang;
    }
    // Apply translations to entire UI
    applyTranslations(lang);
    const langNames = { en: 'English', hi: 'हिंदी', kn: 'ಕನ್ನಡ', te: 'తెలుగు', ta: 'தமிழ்', ml: 'മലയാളം', bn: 'বাংলা', gu: 'ગુજરાતી', mr: 'मराठी', pa: 'ਪੰਜਾਬੀ', or: 'ଓଡ଼ିଆ' };
    toast(`${langNames[lang] || lang.toUpperCase()} ✓`, 'info');
}

// Close lang menu on outside click
document.addEventListener('click', (e) => {
    const langFloat = document.getElementById('lang-float');
    if (langFloat && !langFloat.contains(e.target)) {
        document.getElementById('lang-menu').classList.remove('open');
    }
});

// ═══════════════════════════════════════
//  VOICE ASSISTANT PANEL
// ═══════════════════════════════════════

let voicePanelOpen = false;
let lastVoiceResponse = '';

function toggleVoicePanel() {
    const panel = document.getElementById('voice-panel');
    if (!panel) return;
    if (voicePanelOpen) {
        closeVoicePanel();
    } else {
        openVoicePanel();
    }
}

function openVoicePanel() {
    const panel = document.getElementById('voice-panel');
    if (!panel) return;
    panel.style.display = 'flex';
    voicePanelOpen = true;
    document.getElementById('voice-btn').classList.add('panel-open');
    // Reset state
    setVoiceState('idle');
    document.getElementById('vp-transcript').style.display = 'none';
    document.getElementById('vp-response').style.display = 'none';
    // Update command labels for current language
    updateVoiceCommandLabels();
}

function closeVoicePanel() {
    const panel = document.getElementById('voice-panel');
    if (!panel) return;
    panel.style.display = 'none';
    voicePanelOpen = false;
    document.getElementById('voice-btn').classList.remove('panel-open');
    // Stop any ongoing listening/speaking
    if (window.voiceInterface) {
        window.voiceInterface.stopListening();
        window.voiceInterface.stopSpeaking();
    }
    if (window.speechSynthesis) window.speechSynthesis.cancel();
}

function toggleVoiceListening() {
    if (!window.voiceInterface) {
        toast('Voice not supported in this browser', 'error');
        return;
    }
    if (window.voiceInterface.isListening) {
        window.voiceInterface.stopListening();
        setVoiceState('idle');
    } else {
        // Sync language from app's lang selector
        const appLang = localStorage.getItem('agri_lang') || 'en';
        window.voiceInterface.setLanguage(appLang);
        // Clear previous results
        document.getElementById('vp-transcript').style.display = 'none';
        document.getElementById('vp-response').style.display = 'none';
        // Start listening
        const started = window.voiceInterface.startListening();
        if (started) {
            setVoiceState('listening');
        } else {
            setVoiceState('error');
        }
    }
}

function setVoiceState(state) {
    const stateIcon = document.getElementById('vp-state-icon');
    const stateText = document.getElementById('vp-state-text');
    const wave = document.getElementById('vp-wave');
    const micBtn = document.getElementById('vp-mic-btn');
    const micIcon = document.getElementById('vp-mic-icon');
    const fabBtn = document.getElementById('voice-btn');
    const fabIcon = document.getElementById('voice-btn-icon');

    // Remove all state classes
    micBtn.classList.remove('listening', 'processing', 'speaking', 'error');
    fabBtn.classList.remove('listening', 'speaking', 'error');
    wave.style.display = 'none';

    const lang = localStorage.getItem('agri_lang') || 'en';
    const texts = {
       idle:       { en: 'Tap the mic to speak', hi: 'माइक दबाएं और बोलें', kn: 'ಮೈಕ್ ಒತ್ತಿ ಮಾತನಾಡಿ', te: 'మైక్ నొక్కి మాట్లాడండి', ta: 'மைக் அழுத்தி பேசுங்கள்' },
       listening:  { en: '🎤 Listening... speak now', hi: '🎤 सुन रहे हैं... अभी बोलें', kn: '🎤 ಕೇಳುತ್ತಿದ್ದೇನೆ... ಈಗ ಮಾತನಾಡಿ', te: '🎤 వింటున్నాను... ఇప్పుడు మాట్లాడండి', ta: '🎤 கேட்கிறேன்... இப்போது பேசுங்கள்' },
       processing: { en: '🧠 Thinking...', hi: '🧠 सोच रहे हैं...', kn: '🧠 ಯೋಚಿಸುತ್ತಿದ್ದೇನೆ...', te: '🧠 ఆలోచిస్తున్నాను...', ta: '🧠 சிந்திக்கிறேன்...' },
       speaking:   { en: '🔊 Speaking...', hi: '🔊 बोल रहे हैं...', kn: '🔊 ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ...', te: '🔊 చెప్తున్నాను...', ta: '🔊 பேசுகிறேன்...' },
       error:      { en: '❌ Could not hear. Try again.', hi: '❌ सुनाई नहीं दिया। फिर बोलें।', kn: '❌ ಕೇಳಿಸಲಿಲ್ಲ. ಮತ್ತೆ ಹೇಳಿ.', te: '❌ వినబడలేదు. మళ్ళీ చెప్పండి.', ta: '❌ கேட்கவில்லை. மீண்டும் சொல்லுங்கள்.' }
    };
    stateText.textContent = texts[state]?.[lang] || texts[state]?.en || '';

    switch(state) {
        case 'listening':
            stateIcon.innerHTML = '<i class="fas fa-ear-listen" style="color:#ef4444"></i>';
            stateIcon.className = 'vp-state-icon listening';
            wave.style.display = 'flex';
            micBtn.classList.add('listening');
            micIcon.className = 'fas fa-stop';
            fabBtn.classList.add('listening');
            fabIcon.className = 'fas fa-stop';
            break;
        case 'processing':
            stateIcon.innerHTML = '<i class="fas fa-brain" style="color:#8b5cf6"></i>';
            stateIcon.className = 'vp-state-icon processing';
            micBtn.classList.add('processing');
            micIcon.className = 'fas fa-spinner fa-spin';
            fabIcon.className = 'fas fa-spinner fa-spin';
            break;
        case 'speaking':
            stateIcon.innerHTML = '<i class="fas fa-volume-up" style="color:#3b82f6"></i>';
            stateIcon.className = 'vp-state-icon speaking';
            micBtn.classList.add('speaking');
            micIcon.className = 'fas fa-volume-up';
            fabBtn.classList.add('speaking');
            fabIcon.className = 'fas fa-volume-up';
            break;
        case 'error':
            stateIcon.innerHTML = '<i class="fas fa-exclamation-circle" style="color:#ef4444"></i>';
            stateIcon.className = 'vp-state-icon error';
            micBtn.classList.add('error');
            micIcon.className = 'fas fa-microphone';
            fabIcon.className = 'fas fa-microphone';
            break;
        default: // idle
            stateIcon.innerHTML = '<i class="fas fa-microphone" style="color:#22c55e"></i>';
            stateIcon.className = 'vp-state-icon';
            micIcon.className = 'fas fa-microphone';
            fabIcon.className = 'fas fa-microphone';
    }
}

function showVoiceTranscript(text) {
    const el = document.getElementById('vp-transcript');
    const textEl = document.getElementById('vp-transcript-text');
    if (el && textEl) {
        textEl.textContent = text;
        el.style.display = 'block';
    }
}

function showVoiceResponse(text) {
    const el = document.getElementById('vp-response');
    const textEl = document.getElementById('vp-response-text');
    if (el && textEl) {
        lastVoiceResponse = text;
        textEl.textContent = text;
        el.style.display = 'block';
    }
}

function replayVoiceResponse() {
    if (lastVoiceResponse && window.voiceInterface) {
        setVoiceState('speaking');
        window.voiceInterface.speak(lastVoiceResponse);
        // Monitor when speech ends
        const checkEnd = setInterval(() => {
            if (!window.speechSynthesis.speaking) {
                clearInterval(checkEnd);
                setVoiceState('idle');
            }
        }, 300);
    }
}

async function handleVoiceQuery(text) {
    // Show what user said
    showVoiceTranscript(text);
    setVoiceState('processing');

    try {
        // Call the chatbot API
        const response = await fetch(`${API}/chatbot/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text, username: localStorage.getItem('agri_username') || 'farmer' })
        });
        const data = await response.json();
        const answer = data.response || 'Sorry, I could not get an answer.';

        // Clean markdown/HTML for display
        const cleanAnswer = answer.replace(/[#*_`]/g, '').replace(/<[^>]*>/g, '').trim();
        showVoiceResponse(cleanAnswer);

        // Speak the response
        setVoiceState('speaking');
        if (window.voiceInterface) {
            // Truncate for TTS
            const speakText = cleanAnswer.length > 500 ? cleanAnswer.substring(0, 500) + '...' : cleanAnswer;
            window.voiceInterface.speak(speakText);
        }

        // Monitor when speech ends
        const checkEnd = setInterval(() => {
            if (!window.speechSynthesis.speaking) {
                clearInterval(checkEnd);
                setVoiceState('idle');
            }
        }, 300);

    } catch (err) {
        console.error('Voice query error:', err);
        showVoiceResponse('Could not connect to server. Please try again.');
        setVoiceState('error');
        setTimeout(() => setVoiceState('idle'), 2000);
    }
}

function voiceQuickCommand(command) {
    if (!window.voiceInterface) return;
    showVoiceTranscript(command);
    // Let voice-interface process the command
    window.voiceInterface.processVoiceCommandEnhanced(command, []);
}

function updateVoiceCommandLabels() {
    // Could localize chip labels in future
}

// Legacy compatibility
function toggleVoiceInterface() {
    toggleVoicePanel();
}

// ═══════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════

async function fetchAPI(endpoint, body, method = 'POST') {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API}${endpoint}`, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
    return data;
}

function showLoading(msg) {
    const el = document.getElementById('loading-overlay');
    document.getElementById('loading-message').textContent = msg || 'Processing...';
    el.style.display = '';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const icons = { success: 'fa-check-circle', error: 'fa-times-circle', info: 'fa-info-circle' };
    const div = document.createElement('div');
    div.className = `toast ${type}`;
    div.innerHTML = `<i class="fas ${icons[type] || icons.info} toast-icon"></i><span>${message}</span>`;
    container.appendChild(div);
    setTimeout(() => { div.style.opacity = '0'; div.style.transform = 'translateX(80px)'; setTimeout(() => div.remove(), 300); }, 4000);
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ─── Service Worker Registration ───
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('service-worker.js').catch(() => {});
}
