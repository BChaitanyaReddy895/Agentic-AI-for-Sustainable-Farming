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
});

// ═══════════════════════════════════════
//  AUTH
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
    closeMobileMenu();
    // Lazy-load actions
    if (pageId === 'history') loadHistory();
    if (pageId === 'profile') loadProfileData();
    if (pageId === 'offline') updateOfflinePage();
    if (pageId === 'community') loadCommunityInsights();
    if (pageId === 'sustainability') loadSustainabilityChart();
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
            document.getElementById('dash-temp').textContent = `${Math.round(data.current_weather.temperature)}°C`;
            document.getElementById('dash-humidity').textContent = `${data.current_weather.humidity}%`;
            document.getElementById('dash-wind').textContent = `${data.current_weather.wind_speed} km/h`;
        }
    } catch { /* fallback defaults */ }
}

// ═══════════════════════════════════════
//  FARM SETUP
// ═══════════════════════════════════════

function updateLocationMethod() {
    const method = document.querySelector('input[name="loc-method"]:checked').value;
    document.getElementById('loc-coords').style.display = method === 'coords' ? '' : 'none';
    document.getElementById('loc-city').style.display = method === 'city' ? '' : 'none';
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

    const locMethod = document.querySelector('input[name="loc-method"]:checked').value;
    let lat = 12.9716, lon = 77.5946;
    if (locMethod === 'coords') {
        lat = parseFloat(document.getElementById('user-lat').value) || 12.9716;
        lon = parseFloat(document.getElementById('user-lon').value) || 77.5946;
    }

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
        locMethod,
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

    updateDashboard();
    toast('Farm details saved! 🚜', 'success');
}

// ═══════════════════════════════════════
//  AI RECOMMENDATION (Multi-Agent)
// ═══════════════════════════════════════

async function getRecommendation() {
    if (!state.farmSetup) { toast('Please set up farm details first', 'info'); navigate('farm-setup'); return; }
    showLoading('4 AI agents are analyzing your farm data...');
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

        Plotly.newPlot('fertilizer-chart', [{
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
            Plotly.newPlot('sustainability-trend-chart', [{
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
            }, { responsive: true, displayModeBar: false });
        }
    } catch { /* offline ok */ }
}

// ═══════════════════════════════════════
//  COMMUNITY
// ═══════════════════════════════════════

async function shareCommunityData() {
    showLoading('Sharing anonymously...');
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
        loadCommunityInsights();
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
    } catch { /* offline ok */ }
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
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Analysis failed');
        showSoilResult(data.soil_type);
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
        toast('Pest analysis complete 🐛', 'success');
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
//  VOICE
// ═══════════════════════════════════════

function toggleVoiceInterface() {
    // Delegate to voice-interface.js if available
    if (typeof VoiceInterface !== 'undefined' && VoiceInterface.toggle) {
        VoiceInterface.toggle();
    } else if (typeof toggleVoice === 'function') {
        toggleVoice();
    } else {
        toast('Voice interface loading...', 'info');
    }
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
