import streamlit as st
import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime
from agents.init_db import initialize_db  # Import initialize_db
import plotly.graph_objects as go  # Import Plotly for chart rendering
from PIL import Image
import numpy as np

# Add the 'agents' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'agents')))

# Import the run_agent_collaboration function from agent_setup
from agent_setup import run_agent_collaboration

# Function to analyze soil type from photo based on color
def analyze_soil_from_photo(uploaded_file):
    try:
        image = Image.open(uploaded_file).convert("RGB")
        image_array = np.array(image)
        # Calculate average color
        avg_color = np.mean(image_array, axis=(0, 1))
        r, g, b = avg_color

        # Simple color-based soil classification (rough approximations)
        if r > 150 and g < 100 and b < 100:  # Reddish soil
            return "Clay"
        elif r > 100 and g > 100 and b < 50:  # Yellowish soil
            return "Sandy"
        elif r < 100 and g < 100 and b < 100:  # Dark soil
            return "Loamy"
        else:
            return None  # Unable to determine
    except Exception:
        return None

# Streamlit app
st.set_page_config(page_title="Sustainable Farming Recommendation System", page_icon="🌾")
st.title("Sustainable Farming Recommendation System 🌾")

st.markdown("""
Welcome to the Sustainable Farming Recommendation System!  
Please select your farm's details below to get personalized crop recommendations based on market trends, weather forecasts, and sustainability scores.
""", unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Modern color scheme and gradients */
    :root {
        --primary-color: #2E7D32;
        --secondary-color: #1565C0;
        --accent-color: #FF6D00;
        --background-color: #F5F7F9;
    }
    
    .main {
        background-color: var(--background-color);
        padding: 2rem;
    }
    
    /* Enhanced button styling */
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: 600;
        transition: transform 0.2s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    
    /* Modern recommendation box */
    .recommendation-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-left: 6px solid #4CAF50;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .recommendation-box:hover {
        transform: translateY(-5px);
    }
    
    /* Enhanced headers */
    .score-header {
        text-align: center;
        color: #2C3E50;
        margin-bottom: 2rem;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Custom radio buttons */
    .stRadio>label {
        background-color: white;
        padding: 10px 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 5px;
    }
    
    /* Custom selectbox */
    .stSelectbox {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #4CAF50;
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    
    /* Warning message styling */
    .stWarning {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Custom divider */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #4CAF50 0%, #1565C0 100%);
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Update the header section with a more modern look
st.markdown("""
<div class='recommendation-box' style='background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%); color: white;'>
    <h2 style='color: white; font-size: 2.5em; margin-bottom: 20px;'>🌾 Smart Farming Assistant</h2>
    <p style='font-size: 1.2em; margin-bottom: 15px;'>Get AI-powered recommendations based on:</p>
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>
            📊 Market Analysis
        </div>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>
            🌤️ Weather Patterns
        </div>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>
            🌱 Sustainability Metrics
        </div>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>
            🌍 Environmental Impact
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Update the columns section
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
        <div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h3 style='color: #2E7D32;'>📏 Farm Details</h3>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("### 📏 Farm Details")
    land_size = st.select_slider(
        "Farm size (hectares)",
        options=[1, 2, 5, 8, 10, 15, 20],
        value=8,
        help="Slide to select your farm size"
    )

with col2:
    st.markdown("""
        <div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h3 style='color: #2E7D32;'>🌱 Crop Preference</h3>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🌱 Crop Preference")
    crop_preference = st.selectbox(
        "What would you like to grow?",
        options=["Grains", "Vegetables", "Fruits"],
        help="Choose your preferred crop type"
    )

# Soil type section with improved UI
st.markdown("### 🗺️ Soil Analysis")
soil_option = st.radio(
    "How would you like to determine your soil type?",
    ("📸 Upload a photo", "📝 Manual selection"),
    horizontal=True
)

soil_type = None
if soil_option == "📸 Upload a photo":
    soil_photo = st.file_uploader("Upload soil photo", type=["jpg", "jpeg", "png"])
    if soil_photo:
        soil_type = analyze_soil_from_photo(soil_photo)
        if soil_type:
            st.success(f"✅ Detected soil type: {soil_type}")
        else:
            st.warning("⚠️ Could not determine soil type from photo. Please select manually.")
            soil_type = st.selectbox(
                "Select soil type",
                options=["Loamy", "Sandy", "Clay"],
                help="Choose your soil type"
            )
else:
    soil_type = st.selectbox(
        "Select soil type",
        options=["Loamy", "Sandy", "Clay"],
        help="Choose your soil type"
    )

# Centered get recommendation button
st.markdown("<br>", unsafe_allow_html=True)
if st.button("💡 Generate Smart Recommendation", type="primary"):
    with st.spinner("🔄 Analyzing your farm conditions..."):
        try:
            # Call the backend function to get the recommendation and chart data
            result = run_agent_collaboration(
                land_size=land_size,
                soil_type=soil_type,
                crop_preference=crop_preference
            )
            
            # Display recommendation in a nice box
            st.markdown("### 🎯 Your Personalized Recommendation")
            st.markdown(f"""
                <div class='recommendation-box'>
                    {result['recommendation'].replace('\n', '<br>')}
                </div>
            """, unsafe_allow_html=True)

            # Display charts with improved styling
            st.markdown("<h3 class='score-header'>📊 Detailed Score Analysis</h3>", unsafe_allow_html=True)
            for chart in result['chart_data']:
                crop = chart['crop']
                labels = chart['labels']
                values = chart['values']
                st.markdown(f"#### {crop.capitalize()} Score Distribution")
                # Create a Plotly pie chart
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=labels,
                            values=values,
                            textinfo='label+percent',
                            hoverinfo='label+value',
                            marker=dict(colors=[
                                "#4caf50",  # Market Score (Green)
                                "#2196f3",  # Weather Score (Blue)
                                "#ff9800",  # Sustainability Score (Orange)
                                "#607d8b",  # Carbon Score (Gray)
                                "#00bcd4",  # Water Score (Cyan)
                                "#795548",  # Erosion Score (Brown)
                                "#e91e63"   # Final Score (Pink)
                            ])
                        )
                    ]
                )
                fig.update_layout(
                    title=f"{crop.capitalize()} Score Distribution",
                    title_x=0.5,  # Center the title
                    margin=dict(l=0, r=0, t=40, b=0),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")

# Past recommendations with improved styling
st.markdown("<h3 class='score-header'>📜 Previous Recommendations</h3>", unsafe_allow_html=True)
st.subheader("Past Recommendations", divider="green")
try:
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'farm_recommendations.db')
    with sqlite3.connect(db_path) as conn:
        past_recommendations = pd.read_sql("SELECT * FROM recommendations ORDER BY timestamp DESC LIMIT 5", conn)
    if not past_recommendations.empty:
        st.dataframe(
            past_recommendations[['crop', 'score', 'rationale', 'market_score', 'weather_score', 'sustainability_score', 'carbon_score', 'water_score', 'erosion_score', 'timestamp']],
            use_container_width=True,
            column_config={
                "crop": "Crop",
                "score": "Final Score",
                "rationale": "Rationale",
                "market_score": "Market Score",
                "weather_score": "Weather Score",
                "sustainability_score": "Sustainability Score",
                "carbon_score": "Carbon Footprint Score",
                "water_score": "Water Score",
                "erosion_score": "Erosion Score",
                "timestamp": "Timestamp"
            }
        )
    else:
        st.info("No past recommendations found.")
except Exception as e:
    st.warning(f"Could not load past recommendations: {str(e)}")

# Footer with improved styling
st.markdown("""
---
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ for sustainable farming</p>
    <p><small>Last updated: {}</small></p>
</div>
""".format(datetime.now().strftime("%B %d, %Y at %I:%M %p")), unsafe_allow_html=True)