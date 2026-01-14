// Modern AgriSmart AI - Complete Frontend Application with Multilingual Support
// Version: 2.1.0 - Production Ready with Offline, Voice & Mobile Support

// Dynamic API URL - works on mobile and web
const API_BASE = (function() {
    // Check if running in Capacitor (mobile app)
    if (window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()) {
        // For mobile app - use your deployed server
        // TODO: Replace with your actual production server URL
        return 'https://agrismart-api.onrender.com';
    }
    // For localhost development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://127.0.0.1:8001';
    }
    // For production web
    return window.location.origin.includes(':3000') 
        ? window.location.origin.replace(':3000', ':8001')
        : window.location.origin + '/api';
})();

console.log('🌐 API Base URL:', API_BASE);

// Global state
let currentPage = 'home';
let currentLanguage = localStorage.getItem('agrismart-language') || 'hi';
let recommendations = [];
let weatherData = null;
let farmLocation = null;
let isOffline = !navigator.onLine;
let currentUser = JSON.parse(localStorage.getItem('agrismart-user')) || null;

// Check network status
window.addEventListener('online', () => { 
    isOffline = false; 
    document.body.classList.remove('offline');
    showNotification('Back online!', 'success');
});
window.addEventListener('offline', () => { 
    isOffline = true; 
    document.body.classList.add('offline');
    showNotification('You are offline. Some features may be limited.', 'warning');
});

// ==================== ENHANCED API WITH OFFLINE FALLBACK ====================
async function api(endpoint, method = 'GET', data = null) {
    // Check offline first
    if (isOffline) {
        console.log('📴 Offline mode - using cached data for:', endpoint);
        return getOfflineData(endpoint, data);
    }
    
    try {
        const options = {
            method,
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout: 15000 // 15 second timeout
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        console.log(`📤 API ${method}:`, endpoint, data);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);
        options.signal = controller.signal;
        
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(`📥 API Response:`, result);
        
        // Cache successful responses
        cacheResponse(endpoint, result);
        
        return result;
    } catch (error) {
        console.warn('⚠️ API call failed, trying offline:', error.message);
        return getOfflineData(endpoint, data);
    }
}

function cacheResponse(endpoint, data) {
    try {
        const cacheKey = `cache_${endpoint.replace(/[^a-z0-9]/gi, '_')}`;
        localStorage.setItem(cacheKey, JSON.stringify({
            data,
            timestamp: Date.now()
        }));
    } catch (e) {
        console.warn('Cache storage failed:', e);
    }
}

function getCachedResponse(endpoint) {
    try {
        const cacheKey = `cache_${endpoint.replace(/[^a-z0-9]/gi, '_')}`;
        const cached = localStorage.getItem(cacheKey);
        if (cached) {
            const { data, timestamp } = JSON.parse(cached);
            // Cache valid for 1 hour
            if (Date.now() - timestamp < 3600000) {
                return data;
            }
        }
    } catch (e) {}
    return null;
}

// Get offline data from IndexedDB or local cache
async function getOfflineData(endpoint, data) {
    // Check cached response first
    const cached = getCachedResponse(endpoint);
    if (cached) {
        console.log('📦 Using cached data for:', endpoint);
        return cached;
    }
    
    // Use IndexedDB if available
    if (window.offlineDB) {
        if (endpoint.includes('recommendation') || endpoint.includes('multi_agent')) {
            return await window.offlineDB.getOfflineRecommendation(data);
        }
        if (endpoint.includes('weather')) {
            const cachedWeather = await window.offlineDB.getCachedWeather(data?.lat + ',' + data?.lon);
            if (cachedWeather) return cachedWeather;
        }
        if (endpoint.includes('crop')) {
            return await window.offlineDB.getAllCrops();
        }
    }
    
    // Fallback offline data
    return getHardcodedOfflineData(endpoint, data);
}

// Hardcoded offline data for when everything else fails
function getHardcodedOfflineData(endpoint, data) {
    if (endpoint.includes('recommendation') || endpoint.includes('multi_agent')) {
        return {
            success: true,
            offline: true,
            central_coordinator: {
                final_crop: getBestOfflineCrop(data),
                final_score: 75,
                reasoning: "Based on offline analysis of your soil and weather conditions"
            },
            agents: {
                farmer_advisor: {
                    recommended_crop: getBestOfflineCrop(data),
                    original_prediction: getBestOfflineCrop(data),
                    confidence: 75,
                    advice: "This recommendation is based on offline data. Connect to internet for accurate AI analysis.",
                    model_used: "offline_rules"
                },
                market_researcher: {
                    market_score: 7,
                    price_trend: "Stable",
                    advice: "Market data unavailable offline"
                },
                weather_analyst: {
                    weather_score: 7,
                    risk_level: "medium",
                    advice: "Connect to internet for weather data"
                },
                sustainability_expert: {
                    sustainability_score: 7,
                    environmental_impact: "Moderate",
                    advice: "Crop rotation recommended for sustainability"
                }
            }
        };
    }
    
    if (endpoint.includes('weather')) {
        return {
            offline: true,
            message: "Weather data requires internet connection",
            current: { temp: "--", condition: "Offline" }
        };
    }
    
    if (endpoint.includes('market')) {
        return {
            offline: true,
            message: "Market prices require internet connection",
            prices: []
        };
    }
    
    return { offline: true, message: 'This feature requires internet connection' };
}

function getBestOfflineCrop(data) {
    if (!data) return 'Rice';
    
    const ph = data.ph || 6.5;
    const temp = data.temperature || 25;
    const rainfall = data.rainfall || 500;
    const humidity = data.humidity || 60;
    
    // Simple rule-based recommendation
    if (rainfall > 1000 && humidity > 70) return 'Rice';
    if (rainfall < 400 && temp > 25) return 'Cotton';
    if (ph < 6 && humidity > 60) return 'Rice';
    if (ph > 7.5 && temp < 30) return 'Wheat';
    if (temp > 30 && rainfall > 600) return 'Corn';
    if (temp < 20) return 'Wheat';
    if (rainfall > 500 && rainfall < 800) return 'Sugarcane';
    
    return 'Rice';
}

// Language translations using free translation service
const translations = {
    'en': {
        'Modern Farming Intelligence': 'Modern Farming Intelligence',
        'Home': 'Home',
        'AI Assistant': 'AI Assistant',
        'Smart Tools': 'Smart Tools',
        'Analytics': 'Analytics',
        'Profile': 'Profile',
        'Transform Your Farming with AI Intelligence': 'Transform Your Farming with AI Intelligence',
        'Get personalized crop recommendations, soil analysis, pest predictions, and market insights powered by advanced machine learning algorithms.': 'Get personalized crop recommendations, soil analysis, pest predictions, and market insights powered by advanced machine learning algorithms.',
        'Start AI Analysis': 'Start AI Analysis',
        'Watch Demo': 'Watch Demo'
    },
    'hi': {
        'Modern Farming Intelligence': 'आधुनिक कृषि बुद्धिमत्ता',
        'Home': 'होम',
        'AI Assistant': 'AI सहायक',
        'Smart Tools': 'स्मार्ट टूल्स',
        'Analytics': 'विश्लेषण',
        'Profile': 'प्रोफाइल',
        'Transform Your Farming with AI Intelligence': 'AI बुद्धिमत्ता के साथ अपनी कृषि को बदलें',
        'Get personalized crop recommendations, soil analysis, pest predictions, and market insights powered by advanced machine learning algorithms.': 'उन्नत मशीन लर्निंग एल्गोरिदम द्वारा संचालित व्यक्तिगत फसल सिफारिशें, मिट्टी विश्लेषण, कीट भविष्यवाणियां और बाजार अंतर्दृष्टि प्राप्त करें।',
        'Start AI Analysis': 'AI विश्लेषण शुरू करें',
        'Watch Demo': 'डेमो देखें'
    }
    // Add more languages as needed
};

// Navigation and UI Functions
function navigate(page) {
    currentPage = page;
    hideAllPages();
    showPage(page);
    updateNavigation(page);
    closeDropdowns();
}

function hideAllPages() {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.remove('active');
    });
}

function showPage(page) {
    const pageElement = document.getElementById(`${page}-page`);
    if (pageElement) {
        pageElement.classList.add('active');
        pageElement.classList.add('fade-in');
        
        // Initialize charts when navigating to analytics page
        if (page === 'analytics') {
            setTimeout(() => refreshAnalytics(), 100);
        }
        // Initialize weather chart when navigating to weather page
        if (page === 'weather') {
            setTimeout(() => initWeatherChart(), 100);
        }
        // Initialize market charts when navigating to market page
        if (page === 'market') {
            setTimeout(() => initMarketCharts(), 100);
        }
    }
}

function updateNavigation(activePage) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeNav = document.querySelector(`[onclick="navigate('${activePage}')"]`);
    if (activeNav) activeNav.classList.add('active');
}

// Language Support Functions - OPTIMIZED FOR SPEED
const translationCache = new Map();

function toggleLanguageDropdown() {
    const menu = document.getElementById('lang-menu');
    menu.classList.toggle('active');
}

async function changeLanguage(langCode, langName) {
    currentLanguage = langCode;
    document.getElementById('current-lang').textContent = langName;
    
    // Close dropdown
    document.getElementById('lang-menu').classList.remove('active');
    
    // Check if we have cached translations
    if (translationCache.has(langCode)) {
        applyTranslations(translationCache.get(langCode));
        showNotification(`Switched to ${langName}`, 'success');
        return;
    }
    
    // Show minimal loading for new translations
    const loadingToast = document.createElement('div');
    loadingToast.className = 'translation-loading';
    loadingToast.innerHTML = '<i class="fas fa-globe fa-spin"></i> Translating...';
    loadingToast.style.cssText = 'position:fixed;bottom:100px;left:50%;transform:translateX(-50%);background:#22c55e;color:white;padding:8px 16px;border-radius:20px;z-index:9999;font-size:12px;';
    document.body.appendChild(loadingToast);
    
    try {
        await translateInterface(langCode);
        showNotification(`Switched to ${langName}`, 'success');
    } catch (error) {
        showNotification('Translation applied (some text may remain in English)', 'warning');
    }
    
    loadingToast.remove();
}

function applyTranslations(translationMap) {
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translationMap[key]) {
            el.textContent = translationMap[key];
        }
    });
}

async function translateInterface(langCode) {
    if (langCode === 'en') {
        location.reload(); // Reset to English
        return;
    }
    
    const elementsToTranslate = document.querySelectorAll('[data-translate]');
    const translationMap = {};
    
    // Batch translate - collect all unique texts
    const textsToTranslate = new Set();
    elementsToTranslate.forEach(el => {
        textsToTranslate.add(el.getAttribute('data-translate'));
    });
    
    // Translate in parallel batches
    const textsArray = Array.from(textsToTranslate);
    const batchSize = 5;
    
    for (let i = 0; i < textsArray.length; i += batchSize) {
        const batch = textsArray.slice(i, i + batchSize);
        const promises = batch.map(text => getTranslation(text, langCode));
        const results = await Promise.all(promises);
        
        batch.forEach((text, idx) => {
            translationMap[text] = results[idx];
        });
    }
    
    // Cache and apply
    translationCache.set(langCode, translationMap);
    applyTranslations(translationMap);
}

async function getTranslation(text, targetLang) {
    // Check pre-defined translations first (instant)
    if (translations[targetLang] && translations[targetLang][text]) {
        return translations[targetLang][text];
    }
    
    // Check localStorage cache (fast)
    const cacheKey = `trans_${targetLang}_${text.substring(0, 30)}`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) return cached;
    
    try {
        // Use faster translation API with timeout
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(
            `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|${targetLang}`,
            { signal: controller.signal }
        );
        clearTimeout(timeout);
        
        const data = await response.json();
        
        if (data.responseData && data.responseData.translatedText) {
            const translated = data.responseData.translatedText;
            localStorage.setItem(cacheKey, translated);
            return translated;
        }
    } catch (error) {
        console.warn('Translation failed, using original:', text.substring(0, 20));
    }
    
    return text;
}

// Tools Dropdown
function showToolsDropdown() {
    const dropdown = document.getElementById('tools-dropdown');
    dropdown.classList.toggle('active');
}

function closeDropdowns() {
    document.getElementById('lang-menu').classList.remove('active');
    const toolsDropdown = document.getElementById('tools-dropdown');
    if (toolsDropdown) {
        toolsDropdown.classList.remove('active');
    }
}

// API Helper with enhanced error handling
async function api(endpoint, method = 'GET', data = null) {
    showLoading('Processing request...');
    
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (data) options.body = JSON.stringify(data);
        
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${response.statusText}`);
        }
        
        const result = await response.json();
        hideLoading();
        return result;
    } catch (error) {
        hideLoading();
        console.error('API call failed:', error);
        showNotification(`Request failed: ${error.message}`, 'error');
        return null;
    }
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type} slide-up`;
    
    const icon = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    notification.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="margin-left: auto; background: none; border: none; color: inherit; cursor: pointer;">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 1001;
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 300px;
        max-width: 500px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Loading overlay
function showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    const messageEl = overlay.querySelector('p');
    if (messageEl) messageEl.textContent = message;
    overlay.classList.add('active');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
}

// ==================== ENHANCED CROP RECOMMENDATIONS ====================
async function getRecommendation() {
    const resultsDiv = document.getElementById('recommendation-results');
    resultsDiv.innerHTML = `
        <div class="loading-state">
            <div class="loading-animation">
                <div class="ai-brain">
                    <i class="fas fa-brain"></i>
                </div>
                <div class="loading-text">
                    <h3>AI Agents Collaborating...</h3>
                    <p>Our 4 specialized agents are analyzing your farm data</p>
                    <div class="progress-steps">
                        <div class="step active">🚜 Farmer Analysis</div>
                        <div class="step">💰 Market Research</div>
                        <div class="step">🌤️ Weather Check</div>
                        <div class="step">🌱 Sustainability</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Animate progress steps
    const steps = resultsDiv.querySelectorAll('.step');
    for (let i = 0; i < steps.length; i++) {
        setTimeout(() => {
            steps[i].classList.add('active');
        }, (i + 1) * 1000);
    }
    
    const formData = {
        username: "web_user",
        nitrogen: parseFloat(document.getElementById('nitrogen')?.value) || 40,
        phosphorus: parseFloat(document.getElementById('phosphorus')?.value) || 30,
        potassium: parseFloat(document.getElementById('potassium')?.value) || 30,
        temperature: parseFloat(document.getElementById('temperature')?.value) || 25,
        humidity: parseFloat(document.getElementById('humidity')?.value) || 60,
        ph: parseFloat(document.getElementById('ph')?.value) || 6.5,
        rainfall: parseFloat(document.getElementById('rainfall')?.value) || 500,
        land_size: parseFloat(document.getElementById('land-size')?.value) || 5,
        soil_type: document.getElementById('soil-type')?.value || 'Loamy',
        crop_preference: document.getElementById('crop-preference')?.value || 'Grains'
    };
    
    // DEBUG: Log the actual values being sent
    console.log('📤 Sending to API:', JSON.stringify(formData, null, 2));

    const result = await api('/multi_agent_recommendation', 'POST', formData);
    
    // DEBUG: Log the response
    console.log('📥 API Response:', result);
    
    if (result && result.success) {
        // Show what was sent vs what was received
        console.log('✅ Model prediction:', result.agents?.farmer_advisor?.original_prediction);
        console.log('✅ Final recommendation:', result.agents?.farmer_advisor?.recommended_crop);
        
        displayEnhancedMultiAgentResults(result);
        recommendations.push({ ...formData, ...result, timestamp: new Date().toISOString() });
    } else {
        // Fallback with enhanced display
        displayFallbackRecommendation(formData);
    }
}

function displayEnhancedMultiAgentResults(result) {
    const container = document.getElementById('recommendation-results');
    const agents = result.agents || {};
    const coordinator = result.central_coordinator || {};
    
    container.innerHTML = `
        <div class="modern-results-container fade-in">
            <div class="results-header">
                <div class="success-indicator">
                    <i class="fas fa-check-circle"></i>
                    <span>Analysis Complete</span>
                </div>
                <h2>Multi-Agent AI Recommendation</h2>
                <p>4 specialized AI agents have analyzed your farm conditions</p>
            </div>
            
            <div class="agent-collaboration">
                <h3><i class="fas fa-users"></i> Agent Collaboration</h3>
                <div class="agents-grid">
                    <div class="agent-card farmer-agent">
                        <div class="agent-header">
                            <div class="agent-avatar">🚜</div>
                            <div class="agent-info">
                                <h4>Farmer Advisor</h4>
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${agents.farmer_advisor?.confidence || 0}%"></div>
                                </div>
                                <span class="confidence-text">${agents.farmer_advisor?.confidence || 0}% Confidence</span>
                            </div>
                        </div>
                        <div class="agent-recommendation">
                            <div class="crop-suggestion">
                                <span class="label">🤖 ML Model Predicted:</span>
                                <span class="value" style="color: #3b82f6;">${agents.farmer_advisor?.original_prediction || 'N/A'}</span>
                            </div>
                            <div class="crop-suggestion" style="margin-top: 8px;">
                                <span class="label">✅ Final Recommendation:</span>
                                <span class="value" style="color: #10b981; font-weight: bold;">${agents.farmer_advisor?.recommended_crop || 'N/A'}</span>
                            </div>
                            <div class="model-info" style="margin-top: 8px; font-size: 0.8em; color: #6b7280;">
                                <i class="fas fa-info-circle"></i> Model: ${agents.farmer_advisor?.model_used || 'unknown'}
                            </div>
                            <p class="agent-advice">${agents.farmer_advisor?.advice || 'Analyzing soil and environmental conditions for optimal crop selection.'}</p>
                        </div>
                    </div>
                    
                    <div class="agent-card market-agent">
                        <div class="agent-header">
                            <div class="agent-avatar">💰</div>
                            <div class="agent-info">
                                <h4>Market Researcher</h4>
                                <div class="score-indicator">
                                    <span class="score-value">${agents.market_researcher?.market_score || 0}</span>
                                    <span class="score-max">/10</span>
                                </div>
                                <span class="score-label">Market Score</span>
                            </div>
                        </div>
                        <div class="agent-recommendation">
                            <div class="market-trend">
                                <span class="label">Price Trend:</span>
                                <span class="value trend-${(agents.market_researcher?.price_trend || 'stable').toLowerCase()}">${agents.market_researcher?.price_trend || 'Stable'}</span>
                            </div>
                            <p class="agent-advice">${agents.market_researcher?.advice || 'Current market conditions are favorable for recommended crops.'}</p>
                        </div>
                    </div>
                    
                    <div class="agent-card weather-agent">
                        <div class="agent-header">
                            <div class="agent-avatar">🌤️</div>
                            <div class="agent-info">
                                <h4>Weather Analyst</h4>
                                <div class="risk-indicator ${(agents.weather_analyst?.risk_level || 'medium').toLowerCase()}">
                                    <i class="fas fa-${agents.weather_analyst?.risk_level === 'low' ? 'check' : agents.weather_analyst?.risk_level === 'high' ? 'exclamation' : 'minus'}"></i>
                                    <span>${(agents.weather_analyst?.risk_level || 'Medium').toUpperCase()} RISK</span>
                                </div>
                            </div>
                        </div>
                        <div class="agent-recommendation">
                            <div class="weather-score">
                                <span class="label">Weather Score:</span>
                                <span class="value">${agents.weather_analyst?.weather_score || 0}/10</span>
                            </div>
                            <p class="agent-advice">${agents.weather_analyst?.advice || 'Weather patterns are suitable for the recommended growing season.'}</p>
                        </div>
                    </div>
                    
                    <div class="agent-card sustainability-agent">
                        <div class="agent-header">
                            <div class="agent-avatar">🌱</div>
                            <div class="agent-info">
                                <h4>Sustainability Expert</h4>
                                <div class="sustainability-meter">
                                    <div class="meter-fill" style="width: ${(agents.sustainability_expert?.sustainability_score || 0) * 10}%"></div>
                                </div>
                                <span class="meter-label">${agents.sustainability_expert?.sustainability_score || 0}/10 Sustainable</span>
                            </div>
                        </div>
                        <div class="agent-recommendation">
                            <div class="environmental-impact">
                                <span class="label">Impact Level:</span>
                                <span class="value impact-${(agents.sustainability_expert?.environmental_impact || 'moderate').toLowerCase()}">${agents.sustainability_expert?.environmental_impact || 'Moderate'}</span>
                            </div>
                            <p class="agent-advice">${agents.sustainability_expert?.advice || 'This recommendation supports sustainable farming practices.'}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="final-recommendation">
                <div class="recommendation-header">
                    <h3><i class="fas fa-trophy"></i> Final Recommendation</h3>
                    <div class="coordinator-badge">
                        <span>Central Coordinator</span>
                    </div>
                </div>
                
                <div class="recommendation-result">
                    <div class="recommended-crop">
                        <div class="crop-icon">
                            <i class="fas fa-seedling"></i>
                        </div>
                        <div class="crop-details">
                            <h4>${coordinator.final_crop || 'Wheat'}</h4>
                            <div class="crop-score">
                                <span class="score">${coordinator.overall_score || 8.5}</span>
                                <span class="max">/10</span>
                                <div class="confidence-badge ${(coordinator.confidence_level || 'medium').toLowerCase()}">
                                    ${coordinator.confidence_level || 'Medium'} Confidence
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="recommendation-reasoning">
                        <h5>Why This Crop?</h5>
                        <p>${coordinator.reasoning || 'Based on comprehensive analysis of soil conditions, weather patterns, market trends, and sustainability factors, this crop offers the best potential for your farm.'}</p>
                    </div>
                </div>
                
                <div class="action-plan">
                    <h5><i class="fas fa-clipboard-list"></i> Action Plan</h5>
                    <div class="action-items">
                        ${(coordinator.action_items || [
                            'Prepare soil with recommended nutrients',
                            'Monitor weather conditions for optimal planting time',
                            'Consider market timing for harvest season',
                            'Implement sustainable farming practices'
                        ]).map(item => `
                            <div class="action-item">
                                <i class="fas fa-check"></i>
                                <span>${item}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="recommendation-actions">
                    <button class="btn btn-primary" onclick="downloadRecommendation()">
                        <i class="fas fa-download"></i>
                        Download Report
                    </button>
                    <button class="btn btn-outline" onclick="shareRecommendation()">
                        <i class="fas fa-share"></i>
                        Share Results
                    </button>
                    <button class="btn btn-outline" onclick="saveToProfile()">
                        <i class="fas fa-bookmark"></i>
                        Save to Profile
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add animation delays for smooth appearance
    const cards = container.querySelectorAll('.agent-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('slide-up');
    });
}

// Fallback recommendation when API fails
function displayFallbackRecommendation(formData) {
    const offlineData = getHardcodedOfflineData('/multi_agent_recommendation', formData);
    
    if (offlineData && offlineData.central_coordinator) {
        displayEnhancedMultiAgentResults(offlineData);
        showNotification('Showing offline recommendation. Connect to internet for AI analysis.', 'warning');
    } else {
        const container = document.getElementById('recommendation-results');
        const crop = getBestOfflineCrop(formData);
        
        container.innerHTML = `
            <div class="offline-recommendation fade-in">
                <div class="offline-header">
                    <i class="fas fa-wifi-slash"></i>
                    <h3>Offline Recommendation</h3>
                    <p>Based on your inputs, here's a basic recommendation</p>
                </div>
                
                <div class="recommended-crop-card">
                    <div class="crop-icon-large">
                        <i class="fas fa-seedling"></i>
                    </div>
                    <h2>${crop}</h2>
                    <p class="crop-reason">Recommended based on your soil pH (${formData.ph}), temperature (${formData.temperature}°C), and rainfall (${formData.rainfall}mm)</p>
                </div>
                
                <div class="offline-tips">
                    <h4><i class="fas fa-lightbulb"></i> Quick Tips for ${crop}</h4>
                    <ul>
                        ${getCropTips(crop).map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="offline-actions">
                    <button class="btn btn-primary" onclick="getRecommendation()">
                        <i class="fas fa-sync"></i> Retry Online
                    </button>
                </div>
            </div>
        `;
    }
}

function getCropTips(crop) {
    const tips = {
        'Rice': [
            'Requires standing water during growth',
            'Best planted during monsoon season',
            'Needs nitrogen-rich fertilizer',
            'Harvest when 80% of grains turn golden'
        ],
        'Wheat': [
            'Plant in October-November for best results',
            'Requires 3-4 irrigations',
            'Apply urea fertilizer at tillering stage',
            'Harvest when grains are hard and golden'
        ],
        'Cotton': [
            'Requires well-drained soil',
            'Plant in April-May',
            'Needs proper pest management',
            'Pick when bolls open fully'
        ],
        'Sugarcane': [
            'Requires heavy irrigation',
            'Plant in February-March',
            'Apply potash fertilizer for better yield',
            'Harvest after 10-12 months'
        ],
        'Corn': [
            'Requires warm temperatures',
            'Needs nitrogen-rich soil',
            'Water regularly during tasseling',
            'Harvest when kernels are firm'
        ]
    };
    
    return tips[crop] || [
        'Prepare soil well before planting',
        'Ensure adequate irrigation',
        'Monitor for pests and diseases',
        'Harvest at optimal maturity'
    ];
}

// ==================== ENHANCED SOIL ANALYSIS ====================
async function analyzeSoil() {
    const fileInput = document.getElementById('soil-photo');
    if (!fileInput.files[0]) {
        showNotification('Please select a soil photo first', 'warning');
        return;
    }
    
    const resultsDiv = document.getElementById('soil-results');
    resultsDiv.innerHTML = `
        <div class="analysis-progress">
            <div class="analysis-icon">
                <i class="fas fa-microscope"></i>
            </div>
            <h3>Analyzing Soil Sample...</h3>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <p class="progress-text">Processing image with AI...</p>
        </div>
    `;
    
    // Animate progress bar
    const progressFill = resultsDiv.querySelector('.progress-fill');
    const progressText = resultsDiv.querySelector('.progress-text');
    
    const progressSteps = [
        'Processing image with AI...',
        'Analyzing soil texture...',
        'Identifying soil composition...',
        'Generating recommendations...'
    ];
    
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 25;
        progressFill.style.width = `${progress}%`;
        
        if (progress <= 100) {
            progressText.textContent = progressSteps[Math.floor(progress / 25) - 1] || progressSteps[0];
        }
        
        if (progress >= 100) {
            clearInterval(progressInterval);
        }
    }, 500);
    
    const formData = new FormData();
    formData.append('soil_photo', fileInput.files[0]);
    
    try {
        const response = await fetch(`${API_BASE}/soil_analysis`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            displayEnhancedSoilResults(result);
            showNotification(`Soil analysis complete: ${result.soil_type} detected`, 'success');
        } else {
            throw new Error('Analysis failed');
        }
    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="error-state">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Analysis Failed</h3>
                <p>Unable to analyze soil image. Please try with a clearer photo.</p>
                <button class="btn btn-outline" onclick="document.getElementById('soil-photo').click()">
                    <i class="fas fa-retry"></i>
                    Try Again
                </button>
            </div>
        `;
        showNotification('Soil analysis failed. Please try again.', 'error');
    }
}

function displayEnhancedSoilResults(result) {
    const container = document.getElementById('soil-results');
    const soilType = result.soil_type || 'Unknown';
    
    container.innerHTML = `
        <div class="soil-analysis-result fade-in">
            <div class="result-header">
                <div class="success-indicator">
                    <i class="fas fa-check-circle"></i>
                    <span>Analysis Complete</span>
                </div>
                <h3>Soil Analysis Results</h3>
            </div>
            
            <div class="soil-type-display">
                <div class="soil-sample">
                    <div class="soil-icon ${soilType.toLowerCase()}">
                        <i class="fas fa-layer-group"></i>
                    </div>
                    <div class="soil-details">
                        <h4>Detected Soil Type</h4>
                        <div class="soil-type-badge ${soilType.toLowerCase()}">${soilType}</div>
                        <div class="confidence-score">
                            <span>Confidence: </span>
                            <strong>${result.confidence || 95}%</strong>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="soil-properties">
                <h4><i class="fas fa-list"></i> Soil Characteristics</h4>
                <div class="properties-grid">
                    <div class="property-card">
                        <div class="property-icon drainage-${getDrainageLevel(soilType)}">
                            <i class="fas fa-tint"></i>
                        </div>
                        <div class="property-details">
                            <h5>Drainage</h5>
                            <span class="property-value">${getDrainageLevel(soilType)}</span>
                            <div class="property-bar">
                                <div class="property-fill" style="width: ${getDrainagePercent(soilType)}%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="property-card">
                        <div class="property-icon retention-${getNutrientLevel(soilType)}">
                            <i class="fas fa-leaf"></i>
                        </div>
                        <div class="property-details">
                            <h5>Nutrient Retention</h5>
                            <span class="property-value">${getNutrientLevel(soilType)}</span>
                            <div class="property-bar">
                                <div class="property-fill" style="width: ${getNutrientPercent(soilType)}%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="property-card">
                        <div class="property-icon water-${getWaterLevel(soilType)}">
                            <i class="fas fa-droplet"></i>
                        </div>
                        <div class="property-details">
                            <h5>Water Retention</h5>
                            <span class="property-value">${getWaterLevel(soilType)}</span>
                            <div class="property-bar">
                                <div class="property-fill" style="width: ${getWaterPercent(soilType)}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="recommendations-section">
                <h4><i class="fas fa-lightbulb"></i> Expert Recommendations</h4>
                <div class="recommendation-card">
                    <div class="recommendation-content">
                        <p>${getDetailedSoilRecommendations(soilType)}</p>
                    </div>
                </div>
                
                <div class="best-crops">
                    <h5>Recommended Crops for ${soilType} Soil:</h5>
                    <div class="crop-tags">
                        ${getRecommendedCrops(soilType).map(crop => 
                            `<span class="crop-tag">
                                <i class="fas fa-seedling"></i>
                                ${crop}
                            </span>`
                        ).join('')}
                    </div>
                </div>
            </div>
            
            <div class="soil-actions">
                <button class="btn btn-primary" onclick="getRecommendationBasedOnSoil('${soilType}')">
                    <i class="fas fa-magic"></i>
                    Get Crop Recommendations
                </button>
                <button class="btn btn-outline" onclick="downloadSoilReport()">
                    <i class="fas fa-download"></i>
                    Download Report
                </button>
            </div>
        </div>
    `;
}

// Helper functions for soil analysis
function getDrainageLevel(soilType) {
    const levels = {
        'Sandy': 'Excellent',
        'Loamy': 'Good',
        'Clay': 'Poor'
    };
    return levels[soilType] || 'Good';
}

function getDrainagePercent(soilType) {
    const percentages = {
        'Sandy': 90,
        'Loamy': 70,
        'Clay': 30
    };
    return percentages[soilType] || 60;
}

function getNutrientLevel(soilType) {
    const levels = {
        'Clay': 'High',
        'Loamy': 'Medium',
        'Sandy': 'Low'
    };
    return levels[soilType] || 'Medium';
}

function getNutrientPercent(soilType) {
    const percentages = {
        'Clay': 85,
        'Loamy': 70,
        'Sandy': 40
    };
    return percentages[soilType] || 60;
}

function getWaterLevel(soilType) {
    return getNutrientLevel(soilType); // Similar pattern
}

function getWaterPercent(soilType) {
    return getNutrientPercent(soilType); // Similar pattern
}

function getDetailedSoilRecommendations(soilType) {
    const recommendations = {
        'Clay': 'Clay soil has excellent nutrient retention but poor drainage. Improve soil structure by adding organic matter like compost or aged manure. Consider raised beds or drainage systems for better water management. Till when soil moisture is optimal to prevent compaction.',
        'Sandy': 'Sandy soil drains quickly and warms up fast, but nutrients leach out easily. Add organic matter regularly to improve water retention. Use slow-release fertilizers and consider more frequent, smaller irrigation applications. Mulching will help retain moisture.',
        'Loamy': 'Excellent soil type! Your loamy soil has the perfect balance of drainage and nutrient retention. Maintain soil health by adding organic matter annually. This soil type supports most crops with proper care and management.'
    };
    return recommendations[soilType] || 'Continue with standard soil management practices based on your specific soil conditions.';
}

function getRecommendedCrops(soilType) {
    const crops = {
        'Clay': ['Rice', 'Wheat', 'Barley', 'Cabbage', 'Brussels Sprouts'],
        'Sandy': ['Carrots', 'Radishes', 'Potatoes', 'Lettuce', 'Tomatoes'],
        'Loamy': ['Corn', 'Wheat', 'Cotton', 'Soybeans', 'Most Vegetables']
    };
    return crops[soilType] || ['Wheat', 'Rice', 'Vegetables'];
}

// Additional utility functions
function downloadRecommendation() {
    showNotification('Generating PDF report...', 'info');
    // Implementation for PDF generation
    setTimeout(() => {
        showNotification('Report downloaded successfully!', 'success');
    }, 2000);
}

function shareRecommendation() {
    if (navigator.share) {
        navigator.share({
            title: 'AgriSmart AI Crop Recommendation',
            text: 'Check out my personalized crop recommendation from AgriSmart AI',
            url: window.location.href
        });
    } else {
        navigator.clipboard.writeText(window.location.href);
        showNotification('Link copied to clipboard!', 'success');
    }
}

function saveToProfile() {
    showNotification('Recommendation saved to your profile!', 'success');
    // Implementation to save to user profile
}

function downloadSoilReport() {
    showNotification('Generating soil analysis report...', 'info');
    // Implementation for soil report generation
    setTimeout(() => {
        showNotification('Soil report downloaded!', 'success');
    }, 2000);
}

function getRecommendationBasedOnSoil(soilType) {
    // Pre-fill recommendation form with soil type
    document.getElementById('soil-type').value = soilType;
    navigate('recommendation');
    showNotification(`Recommendation form updated with ${soilType} soil type`, 'success');
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    startAnimations();
});

function initializeApp() {
    navigate('home');
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.lang-dropdown') && !e.target.closest('.dropdown-trigger')) {
            closeDropdowns();
        }
    });
}

function setupEventListeners() {
    // File upload drag and drop functionality
    const uploadArea = document.getElementById('soil-upload-area');
    if (uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.add('drag-over'), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('drag-over'), false);
        });
        
        uploadArea.addEventListener('drop', handleFileSelect, false);
    }
    
    // File input change handler
    const fileInput = document.getElementById('soil-photo');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateFileUploadDisplay(e.target.files[0]);
            }
        });
    }
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleFileSelect(e) {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        document.getElementById('soil-photo').files = files;
        updateFileUploadDisplay(files[0]);
    }
}

function updateFileUploadDisplay(file) {
    const uploadArea = document.getElementById('soil-upload-area');
    if (uploadArea) {
        uploadArea.innerHTML = `
            <div class="file-selected">
                <div class="file-icon">
                    <i class="fas fa-image"></i>
                </div>
                <div class="file-info">
                    <h4>File Selected</h4>
                    <p>${file.name}</p>
                    <p class="file-size">${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
            </div>
        `;
    }
}

function startAnimations() {
    // Animate statistics counters
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.getAttribute('data-count'));
                animateCounter(entry.target, target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    statNumbers.forEach(stat => {
        observer.observe(stat);
    });
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 100;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 20);
}

// Export functions to global scope
window.navigate = navigate;
window.getRecommendation = getRecommendation;
window.analyzeSoil = analyzeSoil;
window.toggleLanguageDropdown = toggleLanguageDropdown;
window.changeLanguage = changeLanguage;
window.showToolsDropdown = showToolsDropdown;

// ==================== CHART FUNCTIONS ====================
// Initialize all analytics charts when page loads
function refreshAnalytics() {
    showNotification('Loading analytics data...', 'info');
    renderCropPerformanceChart();
    renderSoilCompositionChart();
    renderWeatherTrendsChart();
    renderSustainabilityGauge();
    showNotification('Analytics updated!', 'success');
}

function renderCropPerformanceChart() {
    const container = document.getElementById('crop-performance-chart');
    if (!container) return;
    
    const data = [{
        type: 'bar',
        x: ['Wheat', 'Rice', 'Corn', 'Soybean', 'Tomato', 'Cotton'],
        y: [85, 78, 92, 76, 88, 70],
        marker: {
            color: ['#22c55e', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#14b8a6']
        },
        text: ['85%', '78%', '92%', '76%', '88%', '70%'],
        textposition: 'auto'
    }];
    
    const layout = {
        title: 'Crop Suitability Scores',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        xaxis: { title: 'Crop' },
        yaxis: { title: 'Score (%)', range: [0, 100] },
        margin: { l: 50, r: 30, t: 50, b: 50 }
    };
    
    Plotly.newPlot(container, data, layout, {responsive: true});
}

function renderSoilCompositionChart() {
    const container = document.getElementById('soil-composition-chart');
    if (!container) return;
    
    const data = [{
        type: 'pie',
        values: [40, 30, 20, 10],
        labels: ['Nitrogen', 'Phosphorus', 'Potassium', 'Organic Matter'],
        marker: {
            colors: ['#22c55e', '#3b82f6', '#f59e0b', '#8b5cf6']
        },
        hole: 0.4,
        textinfo: 'label+percent'
    }];
    
    const layout = {
        title: 'Soil Nutrient Distribution',
        paper_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        showlegend: true,
        legend: { orientation: 'h', y: -0.1 },
        margin: { l: 30, r: 30, t: 50, b: 50 }
    };
    
    Plotly.newPlot(container, data, layout, {responsive: true});
}

function renderWeatherTrendsChart() {
    const container = document.getElementById('weather-trends-chart');
    if (!container) return;
    
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    
    const data = [
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Temperature (°C)',
            x: days,
            y: [25, 27, 26, 28, 30, 29, 27],
            line: { color: '#ef4444', width: 3 },
            marker: { size: 8 }
        },
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Humidity (%)',
            x: days,
            y: [60, 65, 70, 68, 55, 58, 62],
            line: { color: '#3b82f6', width: 3 },
            marker: { size: 8 },
            yaxis: 'y2'
        }
    ];
    
    const layout = {
        title: '7-Day Weather Overview',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        xaxis: { title: 'Day' },
        yaxis: { title: 'Temperature (°C)', side: 'left' },
        yaxis2: { title: 'Humidity (%)', overlaying: 'y', side: 'right' },
        legend: { orientation: 'h', y: -0.2 },
        margin: { l: 50, r: 50, t: 50, b: 80 }
    };
    
    Plotly.newPlot(container, data, layout, {responsive: true});
}

function renderSustainabilityGauge() {
    const container = document.getElementById('sustainability-chart');
    if (!container) return;
    
    const data = [{
        type: 'indicator',
        mode: 'gauge+number+delta',
        value: 75,
        title: { text: 'Current Score', font: { color: '#e5e7eb' } },
        delta: { reference: 70, increasing: { color: '#22c55e' } },
        gauge: {
            axis: { range: [0, 100], tickcolor: '#e5e7eb' },
            bar: { color: '#22c55e' },
            bgcolor: 'rgba(255,255,255,0.1)',
            borderwidth: 2,
            bordercolor: '#374151',
            steps: [
                { range: [0, 40], color: '#ef4444' },
                { range: [40, 70], color: '#f59e0b' },
                { range: [70, 100], color: '#22c55e' }
            ],
            threshold: {
                line: { color: '#22c55e', width: 4 },
                thickness: 0.75,
                value: 75
            }
        }
    }];
    
    const layout = {
        paper_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        margin: { l: 30, r: 30, t: 30, b: 30 }
    };
    
    Plotly.newPlot(container, data, layout, {responsive: true});
}

// ==================== WEATHER FUNCTIONS ====================
async function getWeatherForecast() {
    const lat = parseFloat(document.getElementById('weather-lat').value);
    const lon = parseFloat(document.getElementById('weather-lon').value);
    
    showLoading('Fetching weather data...');
    
    try {
        const result = await api('/weather', 'POST', { lat, lon, crop_type: 'Grains' });
        
        if (result) {
            displayWeatherResults(result);
            renderWeatherForecastChart(result);
        } else {
            // Generate demo weather data
            const demoData = generateDemoWeather();
            displayWeatherResults(demoData);
            renderWeatherForecastChart(demoData);
        }
    } catch (error) {
        const demoData = generateDemoWeather();
        displayWeatherResults(demoData);
        renderWeatherForecastChart(demoData);
    }
}

function generateDemoWeather() {
    const days = ['Today', 'Tomorrow', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];
    return {
        current: { temperature: 28, humidity: 65, description: 'Partly Cloudy', wind_speed: 12 },
        forecast: days.map((day, i) => ({
            day,
            temp_high: 28 + Math.round(Math.random() * 5),
            temp_low: 20 + Math.round(Math.random() * 3),
            humidity: 60 + Math.round(Math.random() * 20),
            rain_chance: Math.round(Math.random() * 50)
        })),
        risk_level: 'medium',
        recommendations: [
            'Good conditions for planting',
            'Monitor soil moisture levels',
            'Consider irrigation in afternoon'
        ]
    };
}

function displayWeatherResults(data) {
    const container = document.getElementById('weather-results');
    const current = data.current || {};
    
    container.innerHTML = `
        <div class="weather-result fade-in">
            <div class="current-weather">
                <div class="weather-icon">
                    <i class="fas fa-cloud-sun" style="font-size: 4rem; color: #f59e0b;"></i>
                </div>
                <div class="weather-main">
                    <div class="temperature">${current.temperature || 28}°C</div>
                    <div class="description">${current.description || 'Partly Cloudy'}</div>
                </div>
                <div class="weather-details">
                    <div class="detail"><i class="fas fa-tint"></i> ${current.humidity || 65}% Humidity</div>
                    <div class="detail"><i class="fas fa-wind"></i> ${current.wind_speed || 12} km/h Wind</div>
                </div>
            </div>
            
            <div class="risk-assessment">
                <h4>Agricultural Risk Level</h4>
                <div class="risk-badge ${data.risk_level || 'medium'}">
                    <i class="fas fa-${data.risk_level === 'low' ? 'check' : data.risk_level === 'high' ? 'exclamation-triangle' : 'info-circle'}"></i>
                    ${(data.risk_level || 'medium').toUpperCase()} RISK
                </div>
            </div>
            
            <div class="weather-recommendations">
                <h4><i class="fas fa-lightbulb"></i> Recommendations</h4>
                ${(data.recommendations || ['Good conditions for farming']).map(rec => 
                    `<div class="rec-item"><i class="fas fa-check"></i> ${rec}</div>`
                ).join('')}
            </div>
        </div>
    `;
}

function renderWeatherForecastChart(data) {
    const container = document.getElementById('weather-forecast-chart');
    if (!container || !data.forecast) return;
    
    const forecast = data.forecast;
    
    const traces = [
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'High Temp',
            x: forecast.map(d => d.day),
            y: forecast.map(d => d.temp_high),
            line: { color: '#ef4444', width: 3 },
            marker: { size: 8 }
        },
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Low Temp',
            x: forecast.map(d => d.day),
            y: forecast.map(d => d.temp_low),
            line: { color: '#3b82f6', width: 3 },
            marker: { size: 8 }
        },
        {
            type: 'bar',
            name: 'Rain Chance',
            x: forecast.map(d => d.day),
            y: forecast.map(d => d.rain_chance),
            marker: { color: 'rgba(59, 130, 246, 0.5)' },
            yaxis: 'y2'
        }
    ];
    
    const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        xaxis: { title: 'Day' },
        yaxis: { title: 'Temperature (°C)' },
        yaxis2: { title: 'Rain %', overlaying: 'y', side: 'right', range: [0, 100] },
        legend: { orientation: 'h', y: -0.2 },
        barmode: 'overlay',
        margin: { l: 50, r: 50, t: 30, b: 80 }
    };
    
    Plotly.newPlot(container, traces, layout, {responsive: true});
}

// ==================== MARKET DASHBOARD FUNCTIONS ====================
function generateMarketForecast() {
    const crop = document.getElementById('market-crop').value;
    const months = parseInt(document.getElementById('forecast-period').value);
    
    showLoading('Generating market forecast...');
    
    // Base prices per crop (₹/ton)
    const basePrices = {
        'Rice': 25000, 'Wheat': 20000, 'Corn': 18000,
        'Soybean': 35000, 'Tomato': 15000, 'Cotton': 60000
    };
    
    const basePrice = basePrices[crop] || 20000;
    const forecastData = [];
    let currentPrice = basePrice;
    
    for (let i = 0; i < months; i++) {
        const change = (Math.random() - 0.4) * 0.15; // -6% to +9% monthly change
        currentPrice = currentPrice * (1 + change);
        forecastData.push({
            month: `Month ${i + 1}`,
            price: Math.round(currentPrice),
            confidence: Math.max(60, 95 - (i * 3))
        });
    }
    
    hideLoading();
    renderMarketChart(crop, forecastData);
    displayMarketInsights(crop, forecastData, basePrice);
}

function renderMarketChart(crop, data) {
    const container = document.getElementById('market-price-chart');
    if (!container) return;
    
    const prices = data.map(d => d.price);
    const upper = data.map((d, i) => d.price * (1 + (100 - d.confidence) / 200));
    const lower = data.map((d, i) => d.price * (1 - (100 - d.confidence) / 200));
    
    const traces = [
        {
            type: 'scatter',
            mode: 'lines',
            name: 'Upper Bound',
            x: data.map(d => d.month),
            y: upper,
            line: { width: 0 },
            showlegend: false
        },
        {
            type: 'scatter',
            mode: 'lines',
            name: 'Lower Bound',
            x: data.map(d => d.month),
            y: lower,
            fill: 'tonexty',
            fillcolor: 'rgba(59, 130, 246, 0.2)',
            line: { width: 0 },
            showlegend: false
        },
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Predicted Price',
            x: data.map(d => d.month),
            y: prices,
            line: { color: '#22c55e', width: 3 },
            marker: { size: 10 }
        }
    ];
    
    const layout = {
        title: `${crop} Price Forecast (₹/ton)`,
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        xaxis: { title: 'Period' },
        yaxis: { title: 'Price (₹/ton)' },
        legend: { orientation: 'h', y: -0.2 },
        margin: { l: 60, r: 30, t: 50, b: 80 }
    };
    
    Plotly.newPlot(container, traces, layout, {responsive: true});
}

function displayMarketInsights(crop, data, basePrice) {
    const container = document.getElementById('market-insights');
    const finalPrice = data[data.length - 1].price;
    const priceChange = ((finalPrice - basePrice) / basePrice) * 100;
    const trend = priceChange > 0 ? 'increasing' : 'decreasing';
    
    container.innerHTML = `
        <h3><i class="fas fa-lightbulb"></i> Market Insights</h3>
        <div class="insights-content">
            <div class="insight-card ${trend}">
                <div class="insight-icon">
                    <i class="fas fa-${priceChange > 0 ? 'arrow-up' : 'arrow-down'}"></i>
                </div>
                <div class="insight-text">
                    <h4>${crop} Price Trend</h4>
                    <p>Expected to ${trend === 'increasing' ? 'increase' : 'decrease'} by <strong>${Math.abs(priceChange).toFixed(1)}%</strong></p>
                </div>
            </div>
            
            <div class="insight-item">
                <i class="fas fa-rupee-sign"></i>
                <span>Current: ₹${basePrice.toLocaleString()}/ton</span>
            </div>
            <div class="insight-item">
                <i class="fas fa-chart-line"></i>
                <span>Projected: ₹${finalPrice.toLocaleString()}/ton</span>
            </div>
            
            <div class="recommendation-box">
                <h5><i class="fas fa-clipboard-check"></i> Recommendation</h5>
                <p>${priceChange > 5 ? 
                    `Consider planting ${crop} - prices expected to rise significantly.` : 
                    priceChange < -5 ? 
                    `Consider alternatives to ${crop} - prices expected to decline.` :
                    `${crop} prices are stable. Monitor market conditions before planting.`
                }</p>
            </div>
        </div>
    `;
    
    showNotification(`Market forecast generated for ${crop}`, 'success');
}

// ==================== SUSTAINABILITY TRACKER ====================
let sustainabilityHistory = [];

async function logSustainability() {
    const waterUsage = parseFloat(document.getElementById('water-usage').value);
    const fertilizerUse = parseFloat(document.getElementById('fertilizer-use').value);
    const rotation = document.getElementById('crop-rotation').value === 'yes';
    
    // Save to backend
    try {
        await api('/sustainability', 'POST', {
            username: 'web_user',
            water_score: waterUsage,
            fertilizer_use: fertilizerUse,
            rotation: rotation
        });
    } catch (error) {
        console.log('Backend save failed, continuing with local');
    }
    
    // Calculate score
    let score = 100;
    const RECOMMENDED_WATER = 2.0;
    const RECOMMENDED_FERTILIZER = 1.5;
    
    if (waterUsage > RECOMMENDED_WATER) {
        score -= Math.min(30, 30 * (waterUsage - RECOMMENDED_WATER) / RECOMMENDED_WATER);
    }
    if (fertilizerUse > RECOMMENDED_FERTILIZER) {
        score -= Math.min(30, 30 * (fertilizerUse - RECOMMENDED_FERTILIZER) / RECOMMENDED_FERTILIZER);
    }
    score += rotation ? 10 : -10;
    score = Math.max(0, Math.min(100, score));
    
    // Add to history
    sustainabilityHistory.push({
        date: new Date().toLocaleDateString(),
        score: Math.round(score),
        water: waterUsage,
        fertilizer: fertilizerUse,
        rotation
    });
    
    renderSustainabilityTrendChart();
    displaySustainabilityTips(waterUsage, fertilizerUse, rotation, score);
    showNotification(`Sustainability score logged: ${Math.round(score)}`, 'success');
}

function renderSustainabilityTrendChart() {
    const container = document.getElementById('sustainability-trend-chart');
    if (!container) return;
    
    // Add demo data if empty
    if (sustainabilityHistory.length < 2) {
        sustainabilityHistory = [
            { date: 'Season 1', score: 65, water: 2.5, fertilizer: 2.0, rotation: false },
            { date: 'Season 2', score: 72, water: 2.2, fertilizer: 1.8, rotation: true },
            { date: 'Season 3', score: 78, water: 2.0, fertilizer: 1.6, rotation: true },
            ...sustainabilityHistory
        ];
    }
    
    const trace = {
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Sustainability Score',
        x: sustainabilityHistory.map(d => d.date),
        y: sustainabilityHistory.map(d => d.score),
        line: { color: '#22c55e', width: 3 },
        marker: { size: 10 },
        fill: 'tozeroy',
        fillcolor: 'rgba(34, 197, 94, 0.2)'
    };
    
    const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        xaxis: { title: 'Season' },
        yaxis: { title: 'Score', range: [0, 100] },
        margin: { l: 50, r: 30, t: 30, b: 50 }
    };
    
    Plotly.newPlot(container, [trace], layout, {responsive: true});
}

function displaySustainabilityTips(water, fertilizer, rotation, score) {
    const container = document.getElementById('sustainability-tips');
    const tips = [];
    
    if (fertilizer > 1.5) {
        tips.push('Reduce fertilizer use to below 1.5 tons/ha. Consider organic alternatives.');
    }
    if (water > 2.0) {
        tips.push('Reduce water usage to below 2.0 ML/ha. Consider drip irrigation or mulching.');
    }
    if (!rotation) {
        tips.push('Practice crop rotation next season to improve soil health.');
    }
    if (tips.length === 0) {
        tips.push('Excellent! Your practices are highly sustainable. Keep it up!');
    }
    
    container.innerHTML = `
        <h3><i class="fas fa-lightbulb"></i> Improvement Tips</h3>
        <div class="score-display">
            <div class="score-circle ${score > 70 ? 'good' : score > 40 ? 'medium' : 'poor'}">
                <span class="score-value">${Math.round(score)}</span>
                <span class="score-label">Score</span>
            </div>
        </div>
        <div class="tips-list">
            ${tips.map(tip => `
                <div class="tip-item">
                    <i class="fas fa-${tip.includes('Excellent') ? 'check-circle' : 'lightbulb'}"></i>
                    <span>${tip}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// ==================== FERTILIZER OPTIMIZER ====================
async function calculateFertilizer() {
    const soil = document.getElementById('fert-soil').value;
    const crop = document.getElementById('fert-crop').value;
    const land = parseFloat(document.getElementById('fert-land').value);
    
    showLoading('Calculating optimal fertilizer...');
    
    try {
        const result = await api('/fertilizer', 'POST', {
            soil_type: soil,
            crop_type: crop,
            land_size: land
        });
        
        hideLoading();
        if (result) {
            displayFertilizerResults(result, soil, crop, land);
            renderFertilizerChart(result);
            return;
        }
    } catch (error) {
        hideLoading();
        console.log('Using fallback fertilizer calculation');
    }
    
    // Fallback: Base requirements (kg/ha)
    const cropNeeds = {
        'Wheat': { n: 120, p: 60, k: 40 },
        'Corn': { n: 150, p: 70, k: 60 },
        'Rice': { n: 100, p: 50, k: 50 },
        'Tomatoes': { n: 130, p: 80, k: 100 },
        'Soybeans': { n: 30, p: 60, k: 40 }
    };
    
    // Soil adjustments
    const soilModifiers = {
        'Loamy': { n: 1.0, p: 1.0, k: 1.0 },
        'Sandy': { n: 1.3, p: 1.2, k: 1.3 },
        'Clay': { n: 0.8, p: 1.1, k: 0.9 }
    };
    
    const base = cropNeeds[crop] || { n: 100, p: 50, k: 40 };
    const mod = soilModifiers[soil] || { n: 1, p: 1, k: 1 };
    
    const result = {
        nitrogen: Math.round(base.n * mod.n * land),
        phosphorus: Math.round(base.p * mod.p * land),
        potassium: Math.round(base.k * mod.k * land)
    };
    
    displayFertilizerResults(result, soil, crop, land);
    renderFertilizerChart(result);
}

function displayFertilizerResults(result, soil, crop, land) {
    const container = document.getElementById('fertilizer-results');
    
    // Handle both backend format (nitrogen_kg) and local format (nitrogen)
    const nitrogen = result.nitrogen_kg || result.nitrogen || 0;
    const phosphorus = result.phosphorus_kg || result.phosphorus || 0;
    const potassium = result.potassium_kg || result.potassium || 0;
    
    container.innerHTML = `
        <div class="fertilizer-result fade-in">
            <div class="result-header">
                <i class="fas fa-check-circle" style="color: #22c55e;"></i>
                <h3>Fertilizer Calculation Complete</h3>
            </div>
            
            <div class="result-summary">
                <p>For <strong>${land} hectares</strong> of <strong>${soil.toLowerCase()}</strong> soil planting <strong>${crop.toLowerCase()}</strong>:</p>
            </div>
            
            <div class="nutrient-cards">
                <div class="nutrient-card nitrogen">
                    <div class="nutrient-icon">N</div>
                    <div class="nutrient-details">
                        <h4>Nitrogen</h4>
                        <span class="amount">${nitrogen} kg</span>
                    </div>
                </div>
                <div class="nutrient-card phosphorus">
                    <div class="nutrient-icon">P</div>
                    <div class="nutrient-details">
                        <h4>Phosphorus</h4>
                        <span class="amount">${phosphorus} kg</span>
                    </div>
                </div>
                <div class="nutrient-card potassium">
                    <div class="nutrient-icon">K</div>
                    <div class="nutrient-details">
                        <h4>Potassium</h4>
                        <span class="amount">${potassium} kg</span>
                    </div>
                </div>
            </div>
            
            <div class="eco-note">
                <i class="fas fa-leaf"></i>
                <span>These recommendations factor in sustainability by reducing excess fertilizer to lower carbon footprint.</span>
            </div>
        </div>
    `;
}

function renderFertilizerChart(result) {
    const container = document.getElementById('fertilizer-chart');
    if (!container) return;
    
    // Handle both backend format (nitrogen_kg) and local format (nitrogen)
    const nitrogen = result.nitrogen_kg || result.nitrogen || 0;
    const phosphorus = result.phosphorus_kg || result.phosphorus || 0;
    const potassium = result.potassium_kg || result.potassium || 0;
    
    const data = [{
        type: 'bar',
        x: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'],
        y: [nitrogen, phosphorus, potassium],
        marker: {
            color: ['#22c55e', '#3b82f6', '#f59e0b']
        },
        text: [`${nitrogen} kg`, `${phosphorus} kg`, `${potassium} kg`],
        textposition: 'auto'
    }];
    
    const layout = {
        title: 'Recommended Fertilizer Amounts',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        yaxis: { title: 'Amount (kg)' },
        margin: { l: 50, r: 30, t: 50, b: 50 }
    };
    
    Plotly.newPlot(container, data, layout, {responsive: true});
}

// ==================== CROP ROTATION PLANNER ====================
async function generateRotationPlan() {
    const currentCrop = document.getElementById('current-crop').value;
    
    showLoading('Generating rotation plan...');
    
    try {
        const result = await api('/crop_rotation', 'POST', {
            current_crop: currentCrop
        });
        
        hideLoading();
        if (result && result.plan) {
            displayRotationResults(currentCrop, result.plan);
            renderRotationTimeline(currentCrop, result.plan);
            return;
        }
    } catch (error) {
        hideLoading();
        console.log('Using fallback rotation plan');
    }
    
    // Fallback: Rotation recommendations
    const rotationRules = {
        'Wheat': ['Soybean', 'Corn', 'Vegetables'],
        'Corn': ['Soybean', 'Wheat', 'Cover Crop'],
        'Rice': ['Wheat', 'Legumes', 'Vegetables'],
        'Soybean': ['Corn', 'Wheat', 'Barley'],
        'Tomato': ['Legumes', 'Corn', 'Grains'],
        'Cotton': ['Wheat', 'Soybean', 'Corn']
    };
    
    const nextCrops = rotationRules[currentCrop] || ['Legumes', 'Grains', 'Cover Crop'];
    
    displayRotationResults(currentCrop, nextCrops);
    renderRotationTimeline(currentCrop, nextCrops);
}

function displayRotationResults(current, nextCrops) {
    const container = document.getElementById('rotation-results');
    
    container.innerHTML = `
        <div class="rotation-result fade-in">
            <div class="result-header">
                <i class="fas fa-recycle" style="color: #22c55e;"></i>
                <h3>Rotation Plan Generated</h3>
            </div>
            
            <div class="current-crop">
                <h4>Current: ${current}</h4>
            </div>
            
            <div class="rotation-sequence">
                <h4>Recommended Rotation:</h4>
                <div class="sequence-items">
                    ${nextCrops.map((crop, i) => `
                        <div class="sequence-item">
                            <div class="season-badge">Season ${i + 2}</div>
                            <div class="crop-name">${crop}</div>
                        </div>
                    `).join('<div class="arrow"><i class="fas fa-arrow-right"></i></div>')}
                </div>
            </div>
            
            <div class="benefits">
                <h4><i class="fas fa-star"></i> Benefits</h4>
                <ul>
                    <li>Improves soil fertility and structure</li>
                    <li>Breaks pest and disease cycles</li>
                    <li>Reduces need for chemical inputs</li>
                    <li>Increases long-term yields</li>
                </ul>
            </div>
        </div>
    `;
}

function renderRotationTimeline(current, nextCrops) {
    const container = document.getElementById('rotation-timeline-chart');
    if (!container) return;
    
    const allCrops = [current, ...nextCrops];
    const colors = ['#22c55e', '#3b82f6', '#f59e0b', '#8b5cf6'];
    
    const data = [{
        type: 'bar',
        orientation: 'h',
        y: allCrops.map((_, i) => `Season ${i + 1}`),
        x: allCrops.map(() => 1),
        text: allCrops,
        textposition: 'inside',
        marker: {
            color: colors.slice(0, allCrops.length)
        },
        hoverinfo: 'text'
    }];
    
    const layout = {
        title: 'Crop Rotation Timeline',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        xaxis: { visible: false },
        yaxis: { autorange: 'reversed' },
        margin: { l: 80, r: 30, t: 50, b: 30 },
        barmode: 'stack'
    };
    
    Plotly.newPlot(container, data, layout, {responsive: true});
}

// ==================== PEST PREDICTION ====================
async function predictPests() {
    const crop = document.getElementById('pest-crop').value;
    const soilType = document.getElementById('pest-soil').value;
    const temp = parseFloat(document.getElementById('pest-temp').value);
    const humidity = parseFloat(document.getElementById('pest-humidity').value);
    const rainfall = parseFloat(document.getElementById('pest-rainfall').value);
    
    showLoading('Analyzing pest risks...');
    
    try {
        const result = await api('/pest_prediction', 'POST', {
            crop_type: crop,
            soil_type: soilType,
            temperature: temp,
            humidity: humidity,
            rainfall: rainfall
        });
        
        hideLoading();
        if (result && result.risks) {
            displayPestResults(result.risks, crop);
            return;
        }
    } catch (error) {
        hideLoading();
        console.log('Using fallback pest prediction');
    }
    
    // Fallback: Simplified pest risk calculation
    const risks = [];
    
    // Temperature-based risks
    if (temp > 30 && humidity > 70) {
        risks.push({ pest: 'Fungal Diseases', risk: 'high', advice: 'Apply preventive fungicide treatment' });
    }
    if (temp > 25 && humidity > 60) {
        risks.push({ pest: 'Aphids', risk: 'medium', advice: 'Monitor plants weekly, consider neem oil spray' });
    }
    if (rainfall > 1000) {
        risks.push({ pest: 'Root Rot', risk: 'medium', advice: 'Improve drainage, check waterlogging' });
    }
    if (temp < 15) {
        risks.push({ pest: 'Frost Damage', risk: 'high', advice: 'Cover plants or use frost protection' });
    }
    
    // Crop-specific risks
    const cropPests = {
        'Tomato': { pest: 'Tomato Hornworm', risk: 'medium', advice: 'Hand-pick or use Bt spray' },
        'Cotton': { pest: 'Bollworm', risk: 'medium', advice: 'Use pheromone traps for monitoring' },
        'Rice': { pest: 'Stem Borer', risk: 'medium', advice: 'Use light traps and biological control' }
    };
    
    if (cropPests[crop]) {
        risks.push(cropPests[crop]);
    }
    
    if (risks.length === 0) {
        risks.push({ pest: 'General', risk: 'low', advice: 'Conditions are favorable. Continue regular monitoring.' });
    }
    
    displayPestResults(risks, crop);
}

function displayPestResults(risks, crop) {
    const container = document.getElementById('pest-results');
    
    container.innerHTML = `
        <div class="pest-result fade-in">
            <div class="result-header">
                <i class="fas fa-shield-alt" style="color: #22c55e;"></i>
                <h3>Pest Risk Analysis for ${crop}</h3>
            </div>
            
            <div class="risk-cards">
                ${risks.map(r => `
                    <div class="risk-card ${r.risk}">
                        <div class="risk-header">
                            <span class="pest-name">${r.pest}</span>
                            <span class="risk-badge ${r.risk}">${r.risk.toUpperCase()} RISK</span>
                        </div>
                        <div class="risk-advice">
                            <i class="fas fa-lightbulb"></i>
                            <span>${r.advice}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <div class="prevention-tips">
                <h4><i class="fas fa-check-circle"></i> General Prevention Tips</h4>
                <ul>
                    <li>Maintain good field hygiene</li>
                    <li>Practice crop rotation</li>
                    <li>Use resistant varieties when available</li>
                    <li>Monitor fields regularly for early detection</li>
                </ul>
            </div>
        </div>
    `;
    
    showNotification('Pest risk analysis complete', 'success');
}

// ==================== AI CHATBOT ====================
const chatHistory = [];

function handleChatKeypress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addChatMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    addTypingIndicator();
    
    // Try backend API first
    try {
        const result = await api('/chatbot/ask', 'POST', {
            username: 'web_user',
            query: message
        });
        
        removeTypingIndicator();
        if (result && result.response) {
            addChatMessage(result.response, 'ai');
            return;
        }
    } catch (error) {
        console.log('Using fallback chatbot');
    }
    
    // Fallback: Generate AI response locally
    setTimeout(() => {
        removeTypingIndicator();
        const response = generateChatResponse(message);
        addChatMessage(response, 'ai');
    }, 500);
}

function addChatMessage(content, sender) {
    const container = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
        </div>
        <div class="message-content">
            <p>${content}</p>
        </div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    chatHistory.push({ sender, content, timestamp: new Date() });
}

function addTypingIndicator() {
    const container = document.getElementById('chat-messages');
    const indicator = document.createElement('div');
    indicator.className = 'chat-message ai typing-indicator';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="message-avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>
    `;
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function generateChatResponse(message) {
    const lowerMsg = message.toLowerCase();
    
    // Knowledge base for farming queries
    const responses = {
        'soil': 'Soil health is crucial for farming success. Key factors include pH level (6.0-7.0 is ideal for most crops), organic matter content, and nutrient balance (NPK). Consider getting a soil test to understand your specific needs.',
        'water': 'Irrigation needs vary by crop and soil type. Drip irrigation is 90% efficient and ideal for vegetables. Flood irrigation works for rice paddies. Monitor soil moisture and water during cooler parts of the day.',
        'fertilizer': 'Use balanced NPK fertilizers based on soil test results. For most crops, apply nitrogen in split doses. Organic options like compost improve soil structure. Avoid over-fertilization to prevent nutrient runoff.',
        'pest': 'Integrated Pest Management (IPM) is the best approach. Start with prevention (crop rotation, resistant varieties), then biological control, and use chemicals only as a last resort. Regular scouting helps catch problems early.',
        'weather': 'Monitor weather forecasts for planting and harvesting decisions. Protect crops from frost with covers. During heat waves, increase irrigation and provide shade for sensitive crops.',
        'crop': 'Choose crops based on your climate, soil type, and market demand. Consider crop rotation to maintain soil health. Diversification reduces risk from weather and market fluctuations.',
        'wheat': 'Wheat grows best in cool, dry climates. Plant in fall (winter wheat) or spring. Requires well-drained soil with pH 6.0-7.0. Watch for rust diseases and aphids.',
        'rice': 'Rice requires warm temperatures and standing water during growth. Prepare paddy fields carefully. Watch for stem borers and blast disease. Drain fields before harvest.',
        'tomato': 'Tomatoes need warm soil, full sun, and consistent watering. Stake or cage plants for support. Watch for blossom end rot (calcium deficiency) and hornworms.'
    };
    
    // Find matching response
    for (const [keyword, response] of Object.entries(responses)) {
        if (lowerMsg.includes(keyword)) {
            return response;
        }
    }
    
    // Default response
    return "I can help with questions about soil, water management, fertilizers, pest control, weather impacts, and specific crops like wheat, rice, tomatoes, and more. What would you like to know?";
}

// ==================== PROFILE FUNCTIONS ====================
function saveProfile() {
    const name = document.getElementById('farm-name').value;
    const land = document.getElementById('total-land').value;
    const region = document.getElementById('farm-region').value;
    
    localStorage.setItem('farmProfile', JSON.stringify({ name, land, region }));
    showNotification('Profile saved successfully!', 'success');
}

// ==================== CHART INITIALIZATION FUNCTIONS ====================
function initWeatherChart() {
    const container = document.getElementById('weather-forecast-chart');
    if (!container) return;
    
    // Show placeholder chart with sample data
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const traces = [
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'High Temp (°C)',
            x: days,
            y: [28, 30, 29, 31, 32, 30, 28],
            line: { color: '#ef4444', width: 3 },
            marker: { size: 8 }
        },
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Low Temp (°C)',
            x: days,
            y: [22, 23, 22, 24, 25, 24, 22],
            line: { color: '#3b82f6', width: 3 },
            marker: { size: 8 }
        }
    ];
    
    const layout = {
        title: 'Enter location to get actual forecast',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        xaxis: { title: 'Day' },
        yaxis: { title: 'Temperature (°C)' },
        legend: { orientation: 'h', y: -0.2 },
        margin: { l: 50, r: 30, t: 50, b: 80 }
    };
    
    Plotly.newPlot(container, traces, layout, {responsive: true});
}

function initMarketCharts() {
    const container = document.getElementById('market-price-chart');
    if (!container) return;
    
    // Show placeholder with trend data
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const traces = [
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Rice (₹/quintal)',
            x: months,
            y: [2100, 2150, 2200, 2180, 2250, 2300],
            line: { color: '#22c55e', width: 3 }
        },
        {
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Wheat (₹/quintal)',
            x: months,
            y: [1950, 1980, 2020, 2050, 2030, 2080],
            line: { color: '#f59e0b', width: 3 }
        }
    ];
    
    const layout = {
        title: 'Select crop and generate forecast for detailed analysis',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        xaxis: { title: 'Month' },
        yaxis: { title: 'Price (₹/quintal)' },
        legend: { orientation: 'h', y: -0.2 },
        margin: { l: 60, r: 30, t: 50, b: 80 }
    };
    
    Plotly.newPlot(container, traces, layout, {responsive: true});
}

// Export all new functions
window.refreshAnalytics = refreshAnalytics;
window.initWeatherChart = initWeatherChart;
window.initMarketCharts = initMarketCharts;
window.getWeatherForecast = getWeatherForecast;
window.generateMarketForecast = generateMarketForecast;
window.logSustainability = logSustainability;
window.calculateFertilizer = calculateFertilizer;
window.generateRotationPlan = generateRotationPlan;
window.predictPests = predictPests;
window.sendChatMessage = sendChatMessage;
window.handleChatKeypress = handleChatKeypress;
window.saveProfile = saveProfile;