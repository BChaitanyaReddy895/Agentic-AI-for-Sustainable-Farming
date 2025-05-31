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

# Dropdown menus for user inputs
st.subheader("Farm Details", divider="green")

# Land Size (in hectares)
land_size = st.selectbox(
    "Select your farm size (hectares):",
    options=[1, 2, 5, 8, 10, 15, 20],
    index=3,  # Default to 8 hectares
    help="Choose the size of your farm in hectares."
)

# Soil Type: Photo upload or dropdown
st.subheader("Soil Type")
soil_option = st.radio("How would you like to specify the soil type?", ("Upload a photo", "Select from dropdown"))

soil_type = None
if soil_option == "Upload a photo":
    soil_photo = st.file_uploader("Upload a photo of the soil", type=["jpg", "jpeg", "png"])
    if soil_photo:
        soil_type = analyze_soil_from_photo(soil_photo)
        if soil_type:
            st.success(f"Detected soil type: {soil_type}")
        else:
            st.warning("Could not determine soil type from the photo. Please select from the dropdown.")
            soil_type = st.selectbox(
                "Select your soil type:",
                options=["Loamy", "Sandy", "Clay"],
                index=0,  # Default to Loamy
                help="Select the type of soil on your farm."
            )
else:
    soil_type = st.selectbox(
        "Select your soil type:",
        options=["Loamy", "Sandy", "Clay"],
        index=0,  # Default to Loamy
        help="Select the type of soil on your farm."
    )

# Crop Preference: Dropdown only
crop_preference = st.selectbox(
    "Select your crop preference:",
    options=["Grains", "Vegetables", "Fruits"],
    index=0,  # Default to Grains
    help="Choose the type of crops you prefer to grow."
)

# Initialize database if it doesn't exist
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db'))
if not os.path.exists(db_path):
    initialize_db()

# Button to generate recommendation
if st.button("Get Recommendation", type="primary"):
    with st.spinner("Generating recommendation..."):
        try:
            # Call the backend function to get the recommendation and chart data
            result = run_agent_collaboration(
                land_size=land_size,
                soil_type=soil_type,
                crop_preference=crop_preference
            )
            # Replace newlines with HTML line breaks outside the f-string
            formatted_recommendation = result['recommendation'].replace('\n', '<br>')
            # Display the recommendation
            st.subheader("Your Farming Recommendation", divider="green")
            st.markdown(
                f"""
                <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; line-height: 1.6;'>
                    {formatted_recommendation}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Display pie charts for each crop using Plotly
            st.subheader("Score Distribution", divider="green")
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
            st.error(f"An error occurred: {str(e)}")

# Display past recommendations
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

# Footer with dynamic timestamp
current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p IST")
st.markdown(f"""
---

Built with Streamlit for sustainable farming recommendations.  
*Generated on {current_time}*
""", unsafe_allow_html=True)