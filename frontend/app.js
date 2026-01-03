// app.js - Complete migration from Streamlit app.py to JS/FastAPI (fixed with event delegation & all functions defined first)
const API_URL = "http://localhost:8000";
let lastSection = localStorage.getItem('lastSection') || 'farm-details';
let lastRecommendation = localStorage.getItem('lastRecommendation') || '';
let lastResults = {};
try {
    lastResults = JSON.parse(localStorage.getItem('lastResults')) || {};
} catch (e) {}
let currentUser = null;
let i18nextInstance = null;
let currentMap = null;
let chatHistory = [];
let offlineMode = false;

// Initialize i18next for translations (expanded from Streamlit T dict)
async function initTranslations() {
    await i18next.init({
        lng: 'en',
        fallbackLng: 'en',
        debug: false,
        resources: {
            en: {
                translation: {
                    'welcome': 'Welcome',
                    'logout': 'Logout',
                    'farm_details': 'Farm Details',
                    'soil_analysis': 'Soil Analysis',
                    'generate_recommendation': 'Generate Smart Recommendation',
                    'crop_rotation_planner': 'Crop Rotation Planner',
                    'fertilizer_optimization': 'Fertilizer Optimization Calculator',
                    'previous_recommendations': 'Previous Recommendations',
                    'sustainability_score_tracker': 'Sustainability Score Tracker',
                    'interactive_farm_map': 'Interactive Farm Map',
                    'community_insights': 'Community Insights',
                    'market_dashboard': 'Market Dashboard',
                    'ai_chatbot': 'AI Chatbot',
                    'offline_mode': 'Offline Mode',
                    'profile': 'User Profile',
                    'title': 'Sustainable Farming Recommendation System',
                    'crop_preference': 'Crop Preference',
                    'upload_photo': 'Upload a photo',
                    'manual_selection': 'Manual selection',
                    'select_soil_type': 'Select soil type',
                    'personalized_recommendation': 'Your Personalized Recommendation',
                    'weather_forecast': 'Weather Forecast (AI Model)',
                    'pest_prediction': 'Pest/Disease Prediction (AI Model)',
                    'details': 'Details:',
                    'built_with': 'Built with love for sustainable farming',
                    'last_updated': 'Last updated: ',
                    'signup_title': 'Join the Farming Community',
                    'login_title': 'Welcome Back',
                    'username': 'Farmer Name',
                    'farm_name': 'Farm Name',
                    'profile_picture': 'Profile Picture (Optional)',
                    'signup_button': 'Join Now',
                    'login_button': 'Login',
                    'signup_instruction': 'Fill in your details to get started!',
                    'login_instruction': 'Select your farmer profile to continue.',
                    'no_account': 'No account yet? Sign up!',
                    'signup_success': 'Welcome! Your account is created.',
                    'login_success': 'Welcome back!',
                    'username_exists': 'Farmer name already taken. Try another.',
                    'no_users': 'No farmers registered yet. Sign up to start!',
                    'farm_details_instruction': 'Enter your farm size and crop preference.',
                    'soil_analysis_instruction': 'Analyze your soil by uploading a photo or selecting manually.',
                    'recommendation_instruction': 'Click the button below to get your personalized AI-powered recommendation!',
                    'detected_soil_type': 'Detected soil type',
                    'could_not_detect_soil': 'Could not determine soil type from photo. Please select manually.',
                    'soil_option_label': 'How would you like to determine your soil type?',
                    'farm_size_label': 'Farm size',
                    'crop_preference_label': 'Crop type',
                    'farm_size_help': 'Slide to select your farm size',
                    'crop_preference_help': 'Choose your preferred crop type',
                    'fill_all_fields': 'Please fill in all required fields.',
                    'select_farmer': 'Select your farmer profile'
                }
            }
            // Add other languages as needed
        }
    });
    i18nextInstance = i18next;
    return i18nextInstance;
}

// All Functions Defined FIRST (to avoid ReferenceErrors)

// Voice Input
function startVoiceInput() {
    console.log('Voice input started');
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = i18nextInstance.language || 'en-US';
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const farmSizeInput = document.getElementById('land-size');
            if (farmSizeInput && transcript.match(/\d+\.?\d*/)) {
                farmSizeInput.value = transcript.match(/\d+\.?\d*/)[0];
            }
            alert(`Voice input: ${transcript}`);
        };
        recognition.onerror = function(event) {
            console.error('Voice recognition error:', event.error);
        };
        recognition.start();
    } else {
        alert('Voice recognition not supported.');
    }
}

// Farm Details Save
async function saveFarmDetails(username) {
    console.log('Saving farm details for', username);
    const land_size = document.getElementById('land-size').value || 8;
    const soil_type = document.getElementById('soil-type').value || 'Loamy';
    const crop_preference = document.getElementById('crop-preference').value || 'Grains';
    try {
        const res = await fetch(`${API_URL}/farm_details`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, land_size: parseFloat(land_size), soil_type, crop_preference })
        });
        const data = await res.json();
        const farmMsg = data.message || 'Saved!';
        document.getElementById('farm-details-msg').innerText = farmMsg;
        lastResults.farm = farmMsg;
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
        // Update currentUser's farm details if successful
        if (res.ok && currentUser) {
            currentUser.land_size = parseFloat(land_size);
            currentUser.soil_type = soil_type;
            currentUser.crop_preference = crop_preference;
        }
    } catch (error) {
        console.error('Save error:', error);
        document.getElementById('farm-details-msg').innerText = 'Save failed - check backend';
        lastResults.farm = 'Save failed - check backend';
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    }
}

// Soil Analysis
async function analyzeSoilPhoto() {
    console.log('Analyzing soil photo');
    const fileInput = document.getElementById('soil-photo');
    if (!fileInput.files[0]) {
        alert('Select a photo');
        return;
    }
    const formData = new FormData();
    formData.append('soil_photo', fileInput.files[0]);
    try {
        const res = await fetch(`${API_URL}/soil_analysis`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        document.getElementById('soil-photo-msg').innerText = data.soil_type || 'Could not detect';
    } catch (error) {
        console.error('Soil analysis error:', error);
        document.getElementById('soil-photo-msg').innerText = 'Analysis failed';
    }
}

// Smart Recommendation
async function getRecommendation(username) {
    console.log('Getting recommendation');
    const land_size = document.getElementById('land-size').value || 8;
    const soil_type = document.getElementById('soil-type').value || 'Loamy';
    const crop_preference = document.getElementById('crop-preference').value || 'Grains';
    try {
        const res = await fetch(`${API_URL}/recommendation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, land_size: parseFloat(land_size), soil_type, crop_preference })
        });
        const data = await res.json();
        // Build a farmer-friendly summary
        let summary = '';
        if (data.recommendation) {
            summary += `<div style=\"font-size:1.2em;font-weight:600;margin-bottom:8px;\">Recommended Crop: <span style='color:#00bfff;'>${data.recommendation.crop || data.recommendation}</span></div>`;
            if (data.recommendation.reason) {
                summary += `<div style='margin-bottom:8px;'>Reason: ${data.recommendation.reason}</div>`;
            }
            if (data.recommendation.instructions) {
                summary += `<div style='margin-bottom:8px;'>Instructions: ${data.recommendation.instructions}</div>`;
            }
        } else if (typeof data.recommendation === 'string') {
            summary += `<div>${data.recommendation}</div>`;
        } else {
            summary += `<div>No recommendation available.</div>`;
        }
        document.getElementById('recommendation-msg').innerHTML = summary;
        lastRecommendation = summary;
        // Persist both summary and chart data
        lastResults.recommendation = {
            summary,
            chart_data: data.chart_data && Array.isArray(data.chart_data) ? data.chart_data : [{crop: 'Sample', labels: ['Market'], values: [80]}]
        };
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
        // Render charts if present
        renderRecommendationCharts(lastResults.recommendation.chart_data);
    } catch (error) {
        console.error('Recommendation error:', error);
        document.getElementById('recommendation-msg').innerText = 'Recommendation failed';
        lastResults.recommendation = { summary: 'Recommendation failed', chart_data: [] };
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    }
}

function renderRecommendationCharts(charts) {
    const container = document.getElementById('recommendation-charts');
    if (!container) return;
    container.innerHTML = '';
    // Define a color palette with enough unique colors
    const colorPalette = [
        '#00ff85', '#00bfff', '#ffcc00', '#ff6b6b', '#4ecdc4', '#45b7d1', '#ff9f1c',
        '#e91e63', '#8e44ad', '#f39c12', '#16a085', '#d35400', '#2ecc71', '#c0392b', '#2980b9'
    ];
    charts.forEach((chart, index) => {
        const canvas = document.createElement('canvas');
        canvas.id = `rec-chart-${index}`;
        container.appendChild(canvas);
        // Pick as many colors as needed for the number of labels
        const colors = colorPalette.slice(0, (chart.labels || []).length);
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: chart.labels || [],
                datasets: [{ data: chart.values || [], backgroundColor: colors }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: chart.crop || 'Chart' } } }
        });
    });
}

// Crop Rotation
async function getCropRotationPlan() {
    console.log('Getting crop rotation');
    const current_crop = document.getElementById('current-crop').value || 'wheat';
    const years = document.getElementById('rotation-years').value || 3;
    try {
        const res = await fetch(`${API_URL}/crop_rotation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ current_crop, years: parseInt(years) })
        });
        const data = await res.json();
        const rotMsg = data.plan || 'Sample plan';
        document.getElementById('rotation-plan-msg').innerText = rotMsg;
        lastResults.rotation = rotMsg;
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
        renderRotationChart(data.timeline || {months: ['Jan'], scores: [80]});
    } catch (error) {
        console.error('Rotation error:', error);
        document.getElementById('rotation-plan-msg').innerText = 'Plan failed';
        lastResults.rotation = 'Plan failed';
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    }
}

function renderRotationChart(timeline) {
    const ctx = document.getElementById('rotation-chart');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeline.months || [],
            datasets: [{ label: 'Score', data: timeline.scores || [], borderColor: '#00ff85' }]
        },
        options: { responsive: true }
    });
}

// Fertilizer
async function optimizeFertilizer() {
    console.log('Optimizing fertilizer');
    const land_size = document.getElementById('fertilizer-land-size').value || 8;
    const soil_type = document.getElementById('fertilizer-soil-type').value || 'Loamy';
    const crop_type = document.getElementById('fertilizer-crop-type').value || 'wheat';
    try {
        const res = await fetch(`${API_URL}/fertilizer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ land_size: parseFloat(land_size), soil_type, crop_type })
        });
        const data = await res.json();
        const fertMsg = `
            <p>Nitrogen: ${data.nitrogen_kg || 100} kg</p>
            <p>Phosphorus: ${data.phosphorus_kg || 50} kg</p>
            <p>Potassium: ${data.potassium_kg || 75} kg</p>
        `;
        document.getElementById('fertilizer-msg').innerHTML = fertMsg;
        lastResults.fertilizer = fertMsg;
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    } catch (error) {
        console.error('Fertilizer error:', error);
        document.getElementById('fertilizer-msg').innerText = 'Optimization failed';
        lastResults.fertilizer = 'Optimization failed';
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    }
}

// Previous Recommendations
async function loadPreviousRecommendations(username) {
    console.log('Loading previous recs');
    try {
        const res = await fetch(`${API_URL}/previous_recommendations?username=${username}`);
        const data = await res.json();
        const content = document.getElementById('previous-recs-content');
        if (content) {
            if (Array.isArray(data) && data.length > 0) {
                let table = `<table style='width:100%;border-collapse:collapse;'>`;
                table += `<tr style='background:#f0f8ff;'><th style='padding:8px;border:1px solid #b0e0e6;'>Date</th><th style='padding:8px;border:1px solid #b0e0e6;'>Recommendation</th></tr>`;
                data.forEach(rec => {
                    table += `<tr>`;
                    table += `<td style='padding:8px;border:1px solid #b0e0e6;'>${rec.timestamp ? new Date(rec.timestamp).toLocaleString() : 'Now'}</td>`;
                    table += `<td style='padding:8px;border:1px solid #b0e0e6;'>${rec.recommendation || 'Sample'}</td>`;
                    table += `</tr>`;
                });
                table += `</table>`;
                content.innerHTML = table;
            } else {
                content.innerHTML = 'No recommendations yet.';
            }
        }
    } catch (error) {
        console.error('Previous recs error:', error);
    }
}

// Sustainability
async function logSustainabilityScore() {
    console.log('Logging sustainability');
    const water = parseFloat(document.getElementById('sustainability-water').value) || 2.0;
    const fertilizer = parseFloat(document.getElementById('sustainability-fertilizer').value) || 1.5;
    const rotation = document.getElementById('sustainability-rotation').checked;
    try {
        const res = await fetch(`${API_URL}/sustainability`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ water_score: water, fertilizer_use: fertilizer, rotation })
        });
        const data = await res.json();
        const susMsg = `Score: ${data.score || 80}`;
        document.getElementById('sustainability-msg').innerText = susMsg;
        lastResults.sustainability = susMsg;
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
        fetchSustainabilityScores();
    } catch (error) {
        console.error('Sustainability error:', error);
        document.getElementById('sustainability-msg').innerText = 'Log failed';
        lastResults.sustainability = 'Log failed';
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    }
}

async function fetchSustainabilityScores() {
    try {
        const res = await fetch(`${API_URL}/sustainability/scores`);
        const data = await res.json();
        renderSustainabilityChart(data);
    } catch (error) {
        console.error('Sustainability scores error:', error);
    }
}

function renderSustainabilityChart(data) {
    const ctx = document.getElementById('sustainability-chart');
    if (!ctx || !data.timestamps) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.timestamps || [],
            datasets: [{ label: 'Score', data: data.scores || [], borderColor: '#00ff85' }]
        },
        options: { responsive: true }
    });
}

// Farm Map
function initMap() {
    const mapEl = document.getElementById('map');
    if (!mapEl) return;
    currentMap = L.map('map').setView([12.9716, 77.5946], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(currentMap);
    L.marker([12.9716, 77.5946]).addTo(currentMap).bindPopup('Your Farm');
    console.log('Map initialized');
}

async function saveFarmMap() {
    console.log('Saving map');
    if (!currentMap) {
        alert('Map not initialized');
        return;
    }
    const mapData = JSON.stringify(currentMap.toGeoJSON());
    try {
        await fetch(`${API_URL}/farm_map`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser.username, farm_name: currentUser.farm_name, map_data: mapData })
        });
        alert('Map saved!');
    } catch (error) {
        console.error('Map save error:', error);
    }
}

// Community
async function logCommunityInsight() {
    console.log('Logging community insight');
    const crop = document.getElementById('community-crop').value || 'Rice';
    const yield_data = parseFloat(document.getElementById('community-yield').value) || 5;
    const price = parseFloat(document.getElementById('community-price').value) || 2500;
    const practice = document.getElementById('community-practice').value || 'Organic';
    const region = document.getElementById('community-region').value || 'North';
    const season = document.getElementById('community-season').value || 'Kharif';
    try {
        await fetch(`${API_URL}/community`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser.username, crop_type: crop, yield_data, market_price: price, sustainability_practice: practice, region, season })
        });
        document.getElementById('community-msg').innerText = 'Insight shared!';
        lastResults.community = 'Insight shared!';
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
        fetchCommunityInsights();
    } catch (error) {
        console.error('Community error:', error);
        document.getElementById('community-msg').innerText = 'Share failed';
        lastResults.community = 'Share failed';
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    }
}

async function fetchCommunityInsights() {
    try {
        const res = await fetch(`${API_URL}/community/insights`);
        const data = await res.json();
        document.getElementById('community-insights').innerHTML = data.map(insight => `<div>${insight.crop_type}: ${insight.avg_yield} tons/ha</div>`).join('') || 'No insights yet';
        renderCommunityChart(data);
    } catch (error) {
        console.error('Community insights error:', error);
    }
}

function renderCommunityChart(data) {
    const ctx = document.getElementById('community-chart');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.crop_type) || [],
            datasets: [{ label: 'Avg Yield', data: data.map(d => d.avg_yield) || [], backgroundColor: '#00ff85' }]
        },
        options: { responsive: true }
    });
}

// Market Dashboard
async function fetchMarketDashboard() {
    console.log('Fetching market dashboard');
    const crop = document.getElementById('market-crop').value || 'Rice';
    const period = document.getElementById('market-period').value || '3 months';
    try {
        const res = await fetch(`${API_URL}/market/dashboard?crop=${crop}&period=${period}`);
        const data = await res.json();
        const marketMsg = `<div>Forecast for ${data.crop}: ${JSON.stringify(data.forecast)}</div>`;
        document.getElementById('market-content').innerHTML = marketMsg;
        lastResults.market = marketMsg;
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
        renderMarketChart(data.forecast);
    } catch (error) {
        console.error('Market error:', error);
        document.getElementById('market-content').innerText = 'Forecast failed';
        lastResults.market = 'Forecast failed';
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    }
}

function renderMarketChart(forecast) {
    const ctx = document.getElementById('market-chart');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: forecast.map(f => f.month) || [],
            datasets: [{ label: 'Price', data: forecast.map(f => f.price) || [], borderColor: '#00bfff' }]
        },
        options: { responsive: true }
    });
}

// AI Chatbot
async function askChatbot() {
    console.log('Asking chatbot');
    const query = document.getElementById('chatbot-query').value;
    if (!query) return;
    try {
        const res = await fetch(`${API_URL}/chatbot/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await res.json();
        chatHistory.push({ role: 'user', content: query });
        chatHistory.push({ role: 'assistant', content: data.response });
        document.getElementById('chat-history').innerHTML = chatHistory.map(msg => `<div><b>${msg.role}:</b> ${msg.content}</div>`).join('');
        document.getElementById('chatbot-response').innerText = data.response;
        lastResults.chatbot = {
            chatHistory: chatHistory.slice(),
            response: data.response
        };
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    } catch (error) {
        console.error('Chatbot error:', error);
        document.getElementById('chatbot-response').innerText = 'Chat failed';
        lastResults.chatbot = { chatHistory: chatHistory.slice(), response: 'Chat failed' };
        localStorage.setItem('lastResults', JSON.stringify(lastResults));
    }
}

// Offline Mode
function setupOfflineMode() {
    const toggle = document.getElementById('offline-toggle');
    if (toggle) {
        toggle.addEventListener('change', (e) => {
            offlineMode = e.target.checked;
            localStorage.setItem('offlineMode', offlineMode);
            document.getElementById('offline-status').innerText = offlineMode ? 'Offline enabled - Data saved locally' : 'Online - Syncing...';
        });
        toggle.checked = localStorage.getItem('offlineMode') === 'true';
        document.getElementById('offline-status').innerText = toggle.checked ? 'Offline enabled' : 'Online';
    }
}

// User Profile
async function loadProfile() {
    console.log('Loading profile');
    document.getElementById('profile-info-tab').innerHTML = `<div>Username: ${currentUser.username}<br>Farm: ${currentUser.farm_name}</div>`;
    // Expand with history/settings fetches as needed
}

// Section Navigation
function showSection(section) {
                        // Restore recommendation result if on smart-recommendation section
                        if (section === 'smart-recommendation') {
                            let lastResults = {};
                            try {
                                lastResults = JSON.parse(localStorage.getItem('lastResults')) || {};
                            } catch (e) {}
                            if (lastResults.recommendation) {
                                document.getElementById('recommendation-msg').innerHTML = lastResults.recommendation.summary || '';
                                renderRecommendationCharts(lastResults.recommendation.chart_data || []);
                            } else {
                                document.getElementById('recommendation-msg').innerText = '';
                                renderRecommendationCharts([]);
                            }
                        }
                    // Restore chatbot result if on chatbot section
                    if (section === 'chatbot') {
                        let lastResults = {};
                        try {
                            lastResults = JSON.parse(localStorage.getItem('lastResults')) || {};
                        } catch (e) {}
                        if (lastResults.chatbot) {
                            if (Array.isArray(lastResults.chatbot.chatHistory)) {
                                document.getElementById('chat-history').innerHTML = lastResults.chatbot.chatHistory.map(msg => `<div><b>${msg.role}:</b> ${msg.content}</div>`).join('');
                            }
                            document.getElementById('chatbot-response').innerText = lastResults.chatbot.response || '';
                        } else {
                            document.getElementById('chatbot-response').innerText = '';
                            document.getElementById('chat-history').innerHTML = '';
                        }
                    }
                // Restore farm details result if on farm-details section
                if (section === 'farm-details') {
                    let lastResults = {};
                    try {
                        lastResults = JSON.parse(localStorage.getItem('lastResults')) || {};
                    } catch (e) {}
                    if (lastResults.farm) {
                        document.getElementById('farm-details-msg').innerText = lastResults.farm;
                    } else {
                        document.getElementById('farm-details-msg').innerText = '';
                    }
                }
            // Restore market dashboard result if on market-dashboard section
            if (section === 'market-dashboard') {
                let lastResults = {};
                try {
                    lastResults = JSON.parse(localStorage.getItem('lastResults')) || {};
                } catch (e) {}
                if (lastResults.market) {
                    document.getElementById('market-content').innerHTML = lastResults.market;
                } else {
                    document.getElementById('market-content').innerText = '';
                }
            }
        // Restore community result if on community section
        if (section === 'community') {
            let lastResults = {};
            try {
                lastResults = JSON.parse(localStorage.getItem('lastResults')) || {};
            } catch (e) {}
            if (lastResults.community) {
                document.getElementById('community-msg').innerText = lastResults.community;
            } else {
                document.getElementById('community-msg').innerText = '';
            }
        }
    console.log('Showing section:', section);
    lastSection = section;
    localStorage.setItem('lastSection', section);
    document.querySelectorAll('#main-sections > div').forEach(div => div.style.display = 'none');
    const target = document.getElementById(section);
    if (target) target.style.display = 'block';
    if (section === 'profile') {
        document.getElementById('main-sections').style.display = 'none';
        document.getElementById('profile-sections').style.display = 'block';
        loadProfile();
    } else {
        document.getElementById('main-sections').style.display = 'block';
        document.getElementById('profile-sections').style.display = 'none';
    }
    // Restore last recommendation if on smart-recommendation
    if (section === 'smart-recommendation' && lastRecommendation) {
        document.getElementById('recommendation-msg').innerHTML = lastRecommendation;
    }
    // Restore sustainability result if on sustainability section
    if (section === 'sustainability') {
        let lastResults = {};
        try {
            lastResults = JSON.parse(localStorage.getItem('lastResults')) || {};
        } catch (e) {}
        if (lastResults.sustainability) {
            document.getElementById('sustainability-msg').innerText = lastResults.sustainability;
        } else {
            document.getElementById('sustainability-msg').innerText = '';
        }
    }
}

// showMain (with delegation)
async function showMain(user) {
        // Restore saved values for farm details if available
        setTimeout(() => {
            if (user) {
                if (user.land_size) document.getElementById('land-size').value = user.land_size;
                if (user.soil_type) document.getElementById('soil-type').value = user.soil_type;
                if (user.crop_preference) document.getElementById('crop-preference').value = user.crop_preference;
            }
            // Fertilizer section
            if (user && user.land_size) {
                const fertLand = document.getElementById('fertilizer-land-size');
                if (fertLand) fertLand.value = user.land_size;
            }
            if (user && user.soil_type) {
                const fertSoil = document.getElementById('fertilizer-soil-type');
                if (fertSoil) fertSoil.value = user.soil_type;
            }

            // --- Persist farm details on every change ---
            const persistFarmDetails = () => {
                if (!currentUser) return;
                currentUser.land_size = document.getElementById('land-size').value;
                currentUser.soil_type = document.getElementById('soil-type').value;
                currentUser.crop_preference = document.getElementById('crop-preference').value;
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
            };
            document.getElementById('land-size').addEventListener('input', persistFarmDetails);
            document.getElementById('soil-type').addEventListener('change', persistFarmDetails);
            document.getElementById('crop-preference').addEventListener('change', persistFarmDetails);
            // Also persist fertilizer section if needed
            const fertLand = document.getElementById('fertilizer-land-size');
            if (fertLand) fertLand.addEventListener('input', persistFarmDetails);
            const fertSoil = document.getElementById('fertilizer-soil-type');
            if (fertSoil) fertSoil.addEventListener('change', persistFarmDetails);
        }, 0);
    console.log('Showing main for user:', user);
    currentUser = user;
    // Persist user in localStorage
    localStorage.setItem('currentUser', JSON.stringify(user));
    const t = i18nextInstance.t;
    document.getElementById('app').innerHTML = `
        <!-- Hero and Usage as in previous full version -->
        <div class="card-section" style="background: linear-gradient(120deg, #00ff85 0%, #00bfff 100%); color: white; text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size:3em; margin-bottom: 0.5em;">🌾 Sustainable Farming AI Platform</h1>
            <p style="font-size:1.4em; margin-bottom: 1.5em;">Empowering farmers with <b>real-time, AI-powered recommendations</b> for a greener, more profitable future.</p>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5em;">
                <div style="background: rgba(255,255,255,0.2); border-radius: 15px; padding: 1.2em 1.8em; font-size: 1.2em; display: flex; align-items: center; gap: 0.6em;"><span style="font-size:1.8em;">🌱</span> Crop Planning</div>
                <div style="background: rgba(255,255,255,0.2); border-radius: 15px; padding: 1.2em 1.8em; font-size: 1.2em; display: flex; align-items: center; gap: 0.6em;"><span style="font-size:1.8em;">🧪</span> Fertilizer Optimization</div>
                <div style="background: rgba(255,255,255,0.2); border-radius: 15px; padding: 1.2em 1.8em; font-size: 1.2em; display: flex; align-items: center; gap: 0.6em;"><span style="font-size:1.8em;">📊</span> Sustainability Tracking</div>
                <div style="background: rgba(255,255,255,0.2); border-radius: 15px; padding: 1.2em 1.8em; font-size: 1.2em; display: flex; align-items: center; gap: 0.6em;"><span style="font-size:1.8em;">🤖</span> AI Insights</div>
            </div>
        </div>
        <div class="card-section">
            <span class="section-step">📋</span>
            <span class="section-icon">📋</span>
            <b style="font-size:1.3em">How to Use This Platform</b>
            <div class="section-instructions">Follow these simple steps to get the most out of your farming AI assistant:</div>
        </div>
        <div style="display: flex; gap: 2rem; margin-bottom: 2rem;">
            <div style="flex: 1;">
                <h3>🌾 Basic Farming Features</h3>
                <ul>
                    <li><b>Farm Details & Soil Analysis</b>: Enter farm size, upload soil photos.</li>
                    <li><b>Smart Recommendations</b>: Get AI crop suggestions with charts.</li>
                    <li><b>Crop Rotation Planning</b>: Timeline-based schedules.</li>
                </ul>
            </div>
            <div style="flex: 1;">
                <h3>🚀 Advanced Features</h3>
                <ul>
                    <li><b>Interactive Farm Map</b>: Mark zones and risks.</li>
                    <li><b>Community Insights</b>: Share/learn yields and prices.</li>
                    <li><b>AI Chatbot</b>: Ask farming questions.</li>
                </ul>
            </div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:24px;margin-bottom:24px;">
            <div class="card" style="flex:1;min-width:320px;max-width:340px;">
                <div class="title">${t('welcome')}, ${user.username}!</div>
                <div>Farm: ${user.farm_name || ''}</div>
                ${user.profile_picture ? `<img src="data:image/png;base64,${user.profile_picture}" style="width:64px;height:64px;border-radius:50%;margin:12px 0;" />` : ''}
                <button class="logout-btn">${t('logout')}</button>
                <div style="margin-top:18px;">
                    <label for="language-select" style="font-weight:600;">🌐 Language:</label>
                    <select id="language-select" style="font-size:1.08em;padding:8px 12px;border-radius:8px;margin-left:8px;">
                        <option value="en">English</option>
                        <option value="hi">Hindi</option>
                        <option value="ta">Tamil</option>
                        <option value="te">Telugu</option>
                        <option value="mr">Marathi</option>
                        <option value="bn">Bengali</option>
                        <option value="kn">Kannada</option>
                        <option value="gu">Gujarati</option>
                    </select>
                </div>
            </div>
            <div class="card" style="flex:2;min-width:340px;max-width:600px;">
                <div class="title">${t('farm_details')}</div>
                <input id="land-size" type="number" min="0.1" step="0.1" placeholder="Land Size (hectares)" style="margin-bottom:12px;" />
                <select id="soil-type" style="margin-bottom:12px;">
                    <option value="Loamy">Loamy</option>
                    <option value="Sandy">Sandy</option>
                    <option value="Clay">Clay</option>
                </select>
                <select id="crop-preference" style="margin-bottom:12px;">
                    <option value="Grains">Grains</option>
                    <option value="Vegetables">Vegetables</option>
                    <option value="Fruits">Fruits</option>
                </select>
                <!-- End farm details inputs -->
                <button class="save-farm-btn">Save Farm Details</button>
                <div id="farm-details-msg"></div>
                <div style="margin-top:18px;">
                    <label style="font-weight:600;">🎤 Voice Input:</label>
                    <button class="voice-btn">Start Voice</button>
                    <span style="margin-left:12px;color:#888;">(Voice features enabled)</span>
                </div>
            </div>
        </div>
        <nav id="nav-buttons" style="margin-bottom:20px;display:flex;flex-wrap:wrap;gap:10px;justify-content:center;">
            <button class="nav-btn" data-section="farm-details">${t('farm_details')}</button>
            <button class="nav-btn" data-section="soil-analysis">${t('soil_analysis')}</button>
            <button class="nav-btn" data-section="smart-recommendation">${t('generate_recommendation')}</button>
            <button class="nav-btn" data-section="crop-rotation">${t('crop_rotation_planner')}</button>
            <button class="nav-btn" data-section="fertilizer">${t('fertilizer_optimization')}</button>
            <button class="nav-btn" data-section="previous-recs">${t('previous_recommendations')}</button>
            <button class="nav-btn" data-section="sustainability">${t('sustainability_score_tracker')}</button>
            <button class="nav-btn" data-section="farm-map">${t('interactive_farm_map')}</button>
            <button class="nav-btn" data-section="community">${t('community_insights')}</button>
            <button class="nav-btn" data-section="market-dashboard">${t('market_dashboard')}</button>
            <button class="nav-btn" data-section="chatbot">${t('ai_chatbot')}</button>
            <button class="nav-btn" data-section="offline">${t('offline_mode')}</button>
            <button class="nav-btn" data-section="profile">${t('profile')}</button>
        </nav>
        <div id="main-sections">
            <div id="farm-details" class="card" style="display: block;">
                <div class="title">${t('farm_details')}</div>
                <p>${t('farm_details_instruction')}</p>
            </div>
            <div id="soil-analysis" class="card" style="display:none;">
                <div class="title">${t('soil_analysis')} by Photo</div>
                <p>${t('soil_analysis_instruction')}</p>
                <input type="file" id="soil-photo" accept="image/*" style="margin-bottom:12px;" />
                <button class="analyze-soil-btn">${t('upload_photo')}</button>
                <div id="soil-photo-msg"></div>
            </div>
            <div id="smart-recommendation" class="card" style="display:none;">
                <div class="title">${t('generate_recommendation')}</div>
                <p>${t('recommendation_instruction')}</p>
                <button class="get-rec-btn">${t('generate_recommendation')}</button>
                <div id="recommendation-msg"></div>
                <div id="recommendation-charts"></div>
                <div id="weather-tab">Weather Forecast: Simulated data</div>
                <div id="pest-tab">Pest Prediction: IPM advice</div>
            </div>
            <div id="crop-rotation" class="card" style="display:none;">
                <div class="title">${t('crop_rotation_planner')}</div>
                <input id="current-crop" placeholder="Current Crop (e.g. wheat)" style="margin-bottom:12px;" />
                <input id="rotation-years" type="number" min="1" max="5" value="3" style="margin-bottom:12px;" />
                <button class="get-rotation-btn">${t('generate_recommendation')}</button>
                <div id="rotation-plan-msg"></div>
                <canvas id="rotation-chart" width="400" height="200"></canvas>
            </div>
            <div id="fertilizer" class="card" style="display:none;">
                <div class="title">${t('fertilizer_optimization')}</div>
                <input id="fertilizer-land-size" type="number" min="0.1" step="0.1" placeholder="Land Size (hectares)" style="margin-bottom:12px;" />
                <select id="fertilizer-soil-type" style="margin-bottom:12px;">
                    <option value="Loamy">Loamy</option>
                    <option value="Sandy">Sandy</option>
                    <option value="Clay">Clay</option>
                </select>
                <input id="fertilizer-crop-type" placeholder="Crop Type (e.g. wheat)" style="margin-bottom:12px;" />
                <button class="optimize-fertilizer-btn">Optimize Fertilizer</button>
                <div id="fertilizer-msg"></div>
            </div>
            <div id="previous-recs" class="card" style="display:none;">
                <div class="title">${t('previous_recommendations')}</div>
                <div id="previous-recs-content"></div>
            </div>
            <div id="sustainability" class="card" style="display:none;">
                <div class="title">${t('sustainability_score_tracker')}</div>
                <input id="sustainability-water" type="number" placeholder="Water usage (ML/ha)" />
                <input id="sustainability-fertilizer" type="number" placeholder="Fertilizer use (tons/ha)" />
                <label><input type="checkbox" id="sustainability-rotation"> Crop Rotation</label>
                <button class="log-sustainability-btn">Log Score</button>
                <div id="sustainability-msg"></div>
                <canvas id="sustainability-chart" width="400" height="200"></canvas>
            </div>
            <div id="farm-map" class="card" style="display:none;">
                <div class="title">${t('interactive_farm_map')}</div>
                <div id="map"></div>
                <button class="save-map-btn">Save Map</button>
            </div>
            <div id="community" class="card" style="display:none;">
                <div class="title">${t('community_insights')}</div>
                <select id="community-crop"><option>Rice</option><option>Wheat</option></select>
                <input id="community-yield" type="number" placeholder="Yield" />
                <input id="community-price" type="number" placeholder="Price" />
                <select id="community-practice"><option>Organic</option></select>
                <select id="community-region"><option>North</option></select>
                <select id="community-season"><option>Kharif</option></select>
                <button class="share-insight-btn">Share Insight</button>
                <div id="community-msg"></div>
                <div id="community-insights"></div>
                <canvas id="community-chart" width="400" height="200"></canvas>
            </div>
            <div id="market-dashboard" class="card" style="display:none;">
                <div class="title">${t('market_dashboard')}</div>
                <select id="market-crop"><option>Rice</option></select>
                <select id="market-period"><option>3 months</option></select>
                <button class="generate-forecast-btn">Generate Forecast</button>
                <div id="market-content"></div>
                <canvas id="market-chart" width="400" height="200"></canvas>
            </div>
            <div id="chatbot" class="card" style="display:none;">
                <div class="title">${t('ai_chatbot')}</div>
                <div id="chat-history" class="chat-history"></div>
                <input id="chatbot-query" placeholder="Ask about farming..." />
                <button class="send-chat-btn">Send</button>
                <div id="chatbot-response"></div>
            </div>
            <div id="offline" class="card" style="display:none;">
                <div class="title">${t('offline_mode')}</div>
                <label><input type="checkbox" id="offline-toggle"> Enable Offline</label>
                <div id="offline-status"></div>
            </div>
        </div>
        <div id="profile-sections" style="display:none;">
            <div class="card">
                <div class="title">${t('profile')}</div>
                <div id="profile-info-tab">Profile info here</div>
                <div id="profile-history-tab">History here</div>
                <div id="profile-settings-tab">Settings here</div>
                <button class="logout-btn">${t('logout')}</button>
            </div>
        </div>
        <footer style="text-align:center;color:#888;font-size:1em;margin-top:40px;padding:16px 0;background:#f9fff9;border-top:1px solid #e0ffe0;">
            ${t('built_with')} | <span id="footer-year"></span>
        </footer>
    `;
    document.getElementById('footer-year').innerText = new Date().getFullYear();

    // Event Delegation - Attach all listeners after injection
    document.querySelectorAll('.nav-btn').forEach(btn => btn.addEventListener('click', (e) => showSection(e.target.dataset.section)));
    document.querySelector('.save-farm-btn').addEventListener('click', () => saveFarmDetails(currentUser.username));
    document.querySelector('.voice-btn').addEventListener('click', startVoiceInput);
    document.querySelector('.analyze-soil-btn').addEventListener('click', analyzeSoilPhoto);
    document.querySelector('.get-rec-btn').addEventListener('click', () => getRecommendation(currentUser.username));
    document.querySelector('.get-rotation-btn').addEventListener('click', getCropRotationPlan);
    document.querySelector('.optimize-fertilizer-btn').addEventListener('click', optimizeFertilizer);
    document.querySelector('.log-sustainability-btn').addEventListener('click', logSustainabilityScore);
    document.querySelector('.save-map-btn').addEventListener('click', saveFarmMap);
    document.querySelector('.share-insight-btn').addEventListener('click', logCommunityInsight);
    document.querySelector('.generate-forecast-btn').addEventListener('click', fetchMarketDashboard);
    document.querySelector('.send-chat-btn').addEventListener('click', askChatbot);
    document.querySelectorAll('.logout-btn').forEach(btn => btn.addEventListener('click', logout));

    // Language
    document.getElementById('language-select').onchange = (e) => i18next.changeLanguage(e.target.value, () => showMain(user));

    // Offline
    setupOfflineMode();

    // Restore last section or default
    showSection(lastSection);
    loadPreviousRecommendations(user.username);
    fetchCommunityInsights();
    fetchSustainabilityScores();
    initMap();
    loadProfile();
}

// showSignup (with delegation)
async function showSignup() {
    console.log('Showing signup');
    document.getElementById('app').innerHTML = `
        <div class="card" style="max-width:540px;margin:40px auto;padding:36px 32px 28px 32px;">
            <div style="display:flex;justify-content:center;gap:24px;margin-bottom:28px;">
                <button id="tab-signup" class="tab-btn" style="flex:1;font-size:1.35em;padding:18px 0;border-radius:14px;">👋 Sign Up</button>
                <button id="tab-login" class="tab-btn" style="flex:1;font-size:1.35em;padding:18px 0;border-radius:14px;">🔑 Login</button>
            </div>
            <div id="tab-content"></div>
        </div>
    `;
    function renderSignupTab() {
        const t = i18nextInstance.t;
        document.getElementById('tab-content').innerHTML = `
            <div style="text-align:center;margin-bottom:18px;font-size:1.35em;">🌾 <b>${t('welcome')} Farmer!</b></div>
            <div style="margin-bottom:18px;color:#388e3c;font-size:1.08em;">${t('signup_instruction')}</div>
            <input id="signup-username" placeholder="👤 ${t('username')}" style="margin-bottom:16px;font-size:1.18em;padding:16px 12px;border-radius:12px;" />
            <input id="signup-farm" placeholder="🏡 ${t('farm_name')}" style="margin-bottom:16px;font-size:1.18em;padding:16px 12px;border-radius:12px;" />
            <input type="file" id="signup-picture" accept="image/*" style="margin-bottom:16px;font-size:1.08em;padding:10px 0;" />
            <button class="signup-btn" style="width:100%;font-size:1.22em;padding:16px 0;border-radius:12px;margin-top:8px;">✅ ${t('signup_button')}</button>
            <div id="signup-msg" style="margin-top:14px;font-size:1.08em;"></div>
        `;
        document.querySelector('.signup-btn').addEventListener('click', signup);
    }
    function renderLoginTab() {
        const t = i18nextInstance.t;
        document.getElementById('tab-content').innerHTML = `
            <div style="text-align:center;margin-bottom:18px;font-size:1.35em;">🔑 <b>${t('login_title')}</b></div>
            <div style="margin-bottom:18px;color:#388e3c;font-size:1.08em;">${t('login_instruction')}</div>
            <input id="login-username" placeholder="👤 ${t('username')}" style="margin-bottom:16px;font-size:1.18em;padding:16px 12px;border-radius:12px;" />
            <button class="login-btn" style="width:100%;font-size:1.22em;padding:16px 0;border-radius:12px;margin-top:8px;">🔓 ${t('login_button')}</button>
            <div id="login-msg" style="margin-top:14px;font-size:1.08em;"></div>
        `;
        document.querySelector('.login-btn').addEventListener('click', login);
    }
    document.getElementById('tab-signup').addEventListener('click', function() {
        renderSignupTab();
        this.classList.add('active');
        document.getElementById('tab-login').classList.remove('active');
    });
    document.getElementById('tab-login').addEventListener('click', function() {
        renderLoginTab();
        this.classList.add('active');
        document.getElementById('tab-signup').classList.remove('active');
    });
    renderSignupTab();
    document.getElementById('tab-signup').classList.add('active');
}


// Signup
async function signup() {
    const username = document.getElementById('signup-username').value;
    const farm_name = document.getElementById('signup-farm').value;
    let profile_picture = null;
    const picInput = document.getElementById('signup-picture');
    if (picInput && picInput.files && picInput.files[0]) {
        const reader = new FileReader();
        reader.onload = async function(e) {
            profile_picture = e.target.result.split(',')[1];
            await sendSignup(username, farm_name, profile_picture);
        };
        reader.readAsDataURL(picInput.files[0]);
    } else {
        await sendSignup(username, farm_name, profile_picture);
    }
}

async function sendSignup(username, farm_name, profile_picture) {
    try {
        const res = await fetch(`${API_URL}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, farm_name, profile_picture })
        });
        const data = await res.json();
        document.getElementById('signup-msg').innerText = data.message || data.detail;
        if (res.ok) showMain({ username, farm_name, profile_picture });
    } catch (err) {
        document.getElementById('signup-msg').innerText = 'Signup failed.';
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const data = await res.json();
        document.getElementById('login-msg').innerText = data.message || data.detail;
        if (res.ok) showMain(data);
    } catch (err) {
        document.getElementById('login-msg').innerText = 'Login failed.';
    }
}

function logout() {
    // Clear user from localStorage and memory
    localStorage.removeItem('currentUser');
    currentUser = null;
    showSignup();
}

// Init app
initTranslations().then(() => {
    // Restore user from localStorage if present
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        try {
            const user = JSON.parse(savedUser);
            if (user && user.username) {
                showMain(user);
                return;
            }
        } catch (e) {}
    }
    showSignup();
});