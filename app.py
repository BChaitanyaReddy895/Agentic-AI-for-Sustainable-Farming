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
import re  # For parsing recommendation text

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

        # Define typical RGB ranges for soil types (more inclusive thresholds)
        # Clay: Reddish-brown (higher red, moderate green/blue)
        if r > 120 and g < 110 and b < 110 and r > g and r > b:
            return "Clay"
        # Sandy: Yellowish (higher red and green, lower blue)
        elif r > 90 and g > 90 and b < 80 and abs(r - g) < 30:
            return "Sandy"
        # Loamy: Dark brown to black (lower values for all, relatively balanced)
        elif r < 120 and g < 120 and b < 120 and abs(r - g) < 20 and abs(g - b) < 20:
            return "Loamy"

        # Fallback: Classify based on the closest match using a simple distance metric
        # Define typical RGB centers for each soil type
        clay_rgb = (150, 80, 80)    # Reddish-brown
        sandy_rgb = (140, 120, 60)  # Yellowish
        loamy_rgb = (80, 70, 60)    # Dark brown

        # Calculate Euclidean distance to each soil type's RGB center
        def rgb_distance(rgb1, rgb2):
            return np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

        distances = {
            "Clay": rgb_distance((r, g, b), clay_rgb),
            "Sandy": rgb_distance((r, g, b), sandy_rgb),
            "Loamy": rgb_distance((r, g, b), loamy_rgb)
        }

        # Return the soil type with the smallest distance
        closest_soil = min(distances, key=distances.get)
        return closest_soil

    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

# Function to parse recommendation text and extract scores for visualization
def parse_recommendation(recommendation_text):
    crops_data = []
    # Split recommendation into individual crop entries
    crop_entries = recommendation_text.split("Plant ")[1:]  # Skip the "Recommendations:" header
    for entry in crop_entries:
        # Extract crop name
        crop_match = re.match(r"(\w+):", entry)
        if not crop_match:
            continue
        crop = crop_match.group(1)
        
        # Extract scores using regex
        scores = {
            "Market Score": float(re.search(r"market score: ([\d.]+)", entry).group(1)),
            "Weather Suitability": float(re.search(r"weather suitability: ([\d.]+)", entry).group(1)),
            "Sustainability": float(re.search(r"sustainability: ([\d.]+)", entry).group(1)),
            "Carbon Footprint": float(re.search(r"carbon footprint: ([\d.]+)", entry).group(1)),
            "Water": float(re.search(r"water: ([\d.]+)", entry).group(1)),
            "Erosion": float(re.search(r"erosion: ([\d.]+)", entry).group(1)),
            "Final Score": float(re.search(r"Final Score: ([\d.]+)", entry).group(1))
        }
        # Extract market price
        price_match = re.search(r"\(\$([\d.]+)/ton\)", entry)
        market_price = float(price_match.group(1)) if price_match else 0.0
        
        crops_data.append({
            "crop": crop,
            "scores": scores,
            "market_price": market_price
        })
    return crops_data

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

# Initialize database if it doesn't exist
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db'))
if not os.path.exists(db_path):
    initialize_db()

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
            
            # Parse the recommendation text to extract scores for visualization
            crops_data = parse_recommendation(result['recommendation'])
            
            # Display recommendation as poll-type visuals
            st.markdown("### 🎯 Your Personalized Recommendation")
            
            # Display details (Market Insights, Weather Forecast, Sustainability Notes)
            details = result['recommendation'].split("Details:")[1].strip()
            st.markdown(f"""
                <div class='recommendation-box'>
                    <strong>Details:</strong><br>
                    {details.replace('\n', '<br>')}
                </div>
            """, unsafe_allow_html=True)

            # Create a horizontal bar chart for each crop
            for crop_data in crops_data:
                crop = crop_data['crop']
                scores = crop_data['scores']
                market_price = crop_data['market_price']
                
                # Prepare data for the bar chart
                labels = list(scores.keys())
                values = [score * 100 for score in scores.values()]  # Scale to 0-100 for better visualization
                
                # Create a Plotly horizontal bar chart
                fig = go.Figure(
                    data=[
                        go.Bar(
                            y=labels,
                            x=values,
                            orientation='h',
                            marker=dict(
                                color=[
                                    "#4caf50",  # Market Score (Green)
                                    "#2196f3",  # Weather Suitability (Blue)
                                    "#ff9800",  # Sustainability (Orange)
                                    "#607d8b",  # Carbon Footprint (Gray)
                                    "#00bcd4",  # Water (Cyan)
                                    "#795548",  # Erosion (Brown)
                                    "#e91e63"   # Final Score (Pink)
                                ]
                            ),
                            text=[f"{val:.1f}%" for val in values],
                            textposition='auto'
                        )
                    ]
                )
                fig.update_layout(
                    title=f"{crop.capitalize()} Scores (Market Price: ${market_price:.2f}/ton)",
                    title_x=0.5,  # Center the title
                    xaxis_title="Score (%)",
                    yaxis_title="Category",
                    xaxis=dict(range=[0, 100]),  # Scores range from 0 to 100%
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            # Display charts with improved styling (keep the existing pie charts)
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
current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
st.markdown(f"""
---
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ for sustainable farming</p>
    <p><small>Last updated: {current_time}</small></p>
</div>
""", unsafe_allow_html=True)
