import streamlit as st
import sys
import os

# Add the 'agents' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'agents')))

# Import the run_agent_collaboration function from agent_setup
from agent_setup import run_agent_collaboration

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

# Soil Type
soil_type = st.selectbox(
    "Select your soil type:",
    options=["Loamy", "Sandy", "Clay"],
    index=0,  # Default to Loamy
    help="Select the type of soil on your farm."
)

# Crop Preference
crop_preference = st.selectbox(
    "Select your crop preference:",
    options=["Grains", "Vegetables", "Fruits"],
    index=0,  # Default to Grains
    help="Choose the type of crops you prefer to grow."
)

# Button to generate recommendation
if st.button("Get Recommendation", type="primary"):
    with st.spinner("Generating recommendation..."):
        try:
            # Call the backend function to get the recommendation
            recommendation = run_agent_collaboration(
                land_size=land_size,
                soil_type=soil_type,
                crop_preference=crop_preference
            )
            # Replace newlines with HTML line breaks outside the f-string
            formatted_recommendation = recommendation.replace('\n', '<br>')
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
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display past recommendations
st.subheader("Past Recommendations", divider="green")
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'sustainable_farming.db'))
try:
    with sqlite3.connect(db_path) as conn:
        past_recommendations = pd.read_sql("SELECT * FROM recommendations ORDER BY timestamp DESC LIMIT 5", conn)
    if not past_recommendations.empty:
        st.dataframe(
            past_recommendations[['crop', 'score', 'rationale', 'sustainability_score', 'timestamp']],
            use_container_width=True,
            column_config={
                "crop": "Crop",
                "score": "Total Score",
                "rationale": "Rationale",
                "sustainability_score": "Sustainability Score",
                "timestamp": "Timestamp"
            }
        )
    else:
        st.info("No past recommendations found.")
except Exception as e:
    st.warning(f"Could not load past recommendations: {str(e)}")

# Footer
st.markdown("""
---
  
Built with Streamlit for sustainable farming recommendations.
""", unsafe_allow_html=True)
