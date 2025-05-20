import sys
import os
# Add the 'models' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models')))
# Importing necessary autogen classes and SQLite connector
from autogen import AssistantAgent, GroupChat, GroupChatManager
import sqlite3
import pandas as pd
from farmer_advisor import FarmerAdvisor
from market_Researcher import MarketResearcher
from weather_Analyst import WeatherAnalyst
from sustainability_Expert import SustainabilityExpert

# Custom AssistantAgent class to override generate_reply
class CustomAssistantAgent(AssistantAgent):
    def __init__(self, name, system_message, llm_config):
        super().__init__(name=name, system_message=system_message, llm_config=llm_config)
        # Instantiate the agent classes
        self.farmer_advisor = FarmerAdvisor()
        self.market_researcher = MarketResearcher()
        self.weather_analyst = WeatherAnalyst()
        self.sustainability_expert = SustainabilityExpert()
        # Simulated farm and market inputs (to be replaced with real data in a production system)
        self.simulated_inputs = {
            'soil_ph': 6.5,  # Neutral soil pH
            'soil_moisture': 30.0,  # Percentage
            'fertilizer': 50.0,  # kg/ha
            'pesticide': 2.0,  # kg/ha
            'crop_yield': 3.0,  # ton/ha
            'temperature': 25.0,  # Celsius (initial placeholder, updated by WeatherAnalyst)
            'rainfall': 50.0,  # mm (initial placeholder, updated by WeatherAnalyst)
            'market_features': {
                'Demand_Index': 75.0,
                'Supply_Index': 60.0,
                'Competitor_Price_per_ton': 1400.0,
                'Economic_Indicator': 0.8,
                'Weather_Impact_Score': 0.7,
                'Seasonal_Factor': 'Spring',
                'Consumer_Trend_Index': 65.0
            }
        }
        self.sustainability_metrics = {}  # To store sustainability sub-scores

    def generate_reply(self, messages=None, sender=None):
        if messages is None and sender is not None:
            messages = self.chat_messages.get(sender, [])

        # Responses for each agent
        if self.name == "FarmerAdvisor":
            return self.farmer_advisor_response(messages)
        elif self.name == "MarketResearcher":
            return self.market_researcher_response(messages)
        elif self.name == "WeatherAnalyst":
            return self.weather_analyst_response(messages)
        elif self.name == "SustainabilityExpert":
            return self.sustainability_expert_response(messages)
        elif self.name == "CentralCoordinator":
            return self.central_coordinator_logic(messages, sender)
        return "No response available."

    def farmer_advisor_response(self, messages):
        initial_message = next((msg["content"] for msg in messages if msg["name"] == "CentralCoordinator"), "")
        if "hectare farm with" in initial_message:
            parts = initial_message.split("suggest crops based on a ")[1].split(" farm with ")
            land_size = float(parts[0].split("-hectare")[0])
            soil_type = parts[1].split(" soil and a preference for ")[0].lower()
            crop_preference = parts[1].split(" soil and a preference for ")[1].split(".")[0].lower()

            # Map soil type to soil pH (simplified mapping)
            soil_ph_mapping = {"sandy": 6.0, "loamy": 6.5, "clay": 7.0}
            self.simulated_inputs['soil_ph'] = soil_ph_mapping.get(soil_type, 6.5)

            # Use WeatherAnalyst's forecast for temperature and rainfall
            weather_forecast = self.weather_analyst.forecast(
                self.simulated_inputs['soil_ph'],
                self.simulated_inputs['soil_moisture'],
                self.simulated_inputs['fertilizer'],
                self.simulated_inputs['pesticide']
            )
            self.simulated_inputs['temperature'] = weather_forecast['temperature'][0]
            self.simulated_inputs['rainfall'] = weather_forecast['rainfall'][0]

            # Recommend crops
            recommended_crop = self.farmer_advisor.recommend(
                soil_ph=self.simulated_inputs['soil_ph'],
                soil_moisture=self.simulated_inputs['soil_moisture'],
                temp=self.simulated_inputs['temperature'],
                rainfall=self.simulated_inputs['rainfall'],
                fertilizer=self.simulated_inputs['fertilizer'],
                pesticide=self.simulated_inputs['pesticide'],
                crop_yield=self.simulated_inputs['crop_yield']
            )
            # Suggest a second crop based on crop preference
            crop_preference_crops = {
                "grains": ["wheat", "barley"],
                "vegetables": ["carrots", "potatoes"],
                "fruits": ["apples", "oranges"]
            }
            suggested_crops = crop_preference_crops.get(crop_preference, ["wheat", "barley"])
            if recommended_crop.lower() not in suggested_crops:
                suggested_crops[0] = recommended_crop.lower()
            return f"Based on a {land_size}-hectare farm with {soil_type} soil and a preference for {crop_preference}, I suggest planting {suggested_crops[0]} and {suggested_crops[1]}."
        return "No farm inputs provided to suggest crops."

    def market_researcher_response(self, messages):
        farmer_response = next((msg["content"] for msg in messages if msg["name"] == "FarmerAdvisor"), "")
        if "suggest planting" in farmer_response:
            crops = farmer_response.split("suggest planting ")[1].split(" and ")
            crops = [crop.strip(".") for crop in crops]
            market_insights = []
            self.market_predictions = {}  # Store predictions for scoring
            for crop in crops:
                try:
                    predicted_price = self.market_researcher.forecast(crop, self.simulated_inputs['market_features'])[0]
                    self.market_predictions[crop] = predicted_price
                    market_insights.append(f"{crop} is expected to have a market price of ${predicted_price:.2f} per ton")
                except ValueError as e:
                    self.market_predictions[crop] = 0.0
                    market_insights.append(f"No market data available for {crop}")
            return ", and ".join(market_insights) + "."
        return "No crops suggested to provide market insights."

    def weather_analyst_response(self, messages):
        temp = self.simulated_inputs['temperature']
        rainfall = self.simulated_inputs['rainfall']
        return f"For the next 3 months, expect a temperature of {temp:.1f}°C and rainfall of {rainfall:.1f} mm."

    def sustainability_expert_response(self, messages):
        farmer_response = next((msg["content"] for msg in messages if msg["name"] == "FarmerAdvisor"), "")
        if "suggest planting" in farmer_response:
            crops = farmer_response.split("suggest planting ")[1].split(" and ")
            crops = [crop.strip(".") for crop in crops]

            sustainability_notes = []
            self.sustainability_metrics = {}

            # Connect to SQLite database to compute sub-scores
            with sqlite3.connect("Models/database/sustainable_farming.db") as conn:
                for crop in crops:
                    df = pd.read_sql("""
                        SELECT Crop_Type, Sustainability_Score, Fertilizer_Usage_kg, Soil_Moisture
                        FROM farmer_advisor
                        WHERE Crop_Type = ?
                    """, conn, params=(crop,))

                    if df.empty:
                        sustainability_notes.append(f"No sustainability data available for {crop}.")
                        self.sustainability_metrics[crop] = {'carbon_score': 0.5, 'water_score': 0.5, 'erosion_score': 0.5}
                        continue

                    # Compute sub-scores
                    avg_sustainability = df['Sustainability_Score'].mean()
                    avg_fertilizer = df['Fertilizer_Usage_kg'].mean()
                    avg_moisture = df['Soil_Moisture'].mean()

                    # Carbon footprint: Lower fertilizer usage = lower carbon footprint
                    carbon_score = 1.0 - (avg_fertilizer / 100.0)
                    carbon_score = max(0.0, min(1.0, carbon_score))

                    # Water usage: Lower soil moisture requirement = better water usage score
                    water_score = 1.0 - (avg_moisture / 100.0)
                    water_score = max(0.0, min(1.0, water_score))

                    # Soil erosion: Higher sustainability score = better erosion prevention
                    erosion_score = avg_sustainability / 100.0
                    erosion_score = max(0.0, min(1.0, erosion_score))

                    self.sustainability_metrics[crop] = {
                        'carbon_score': carbon_score,
                        'water_score': water_score,
                        'erosion_score': erosion_score
                    }

                    sustainability_notes.append(
                        f"{crop} has a carbon footprint score of {carbon_score:.2f} (lower fertilizer usage), "
                        f"a water usage score of {water_score:.2f} (based on soil moisture needs), "
                        f"and a soil erosion prevention score of {erosion_score:.2f} (based on sustainability score)."
                    )

            return " ".join(sustainability_notes)
        return "No crops suggested to evaluate sustainability."

    def central_coordinator_logic(self, messages, sender):
        # Collect responses from all agents
        agent_responses = {}
        for message in messages:
            sender_name = message.get("name")
            content = message.get("content")
            if sender_name and content and sender_name != "CentralCoordinator":
                agent_responses[sender_name] = content

        # Extract crops from FarmerAdvisor
        crops = agent_responses.get("FarmerAdvisor", "").split("suggest planting ")[1].split(" and ")
        crops = [crop.strip(".") for crop in crops]

        # Extract market, weather, and sustainability info
        market_info = agent_responses.get("MarketResearcher", "")
        weather_info = agent_responses.get("WeatherAnalyst", "")
        sustainability_info = agent_responses.get("SustainabilityExpert", "")

        # Weighted scoring system
        weights = {
            "sustainability": 0.5,  # 50%
            "weather": 0.25,        # 25%
            "market": 0.15,         # 15% (profitability)
            "farmer": 0.1           # 10% (preferences)
        }
        sustainability_sub_weights = {
            "carbon": 0.20,  # 20% of total score
            "water": 0.15,   # 15% of total score
            "erosion": 0.15  # 15% of total score
        }
        crop_scores = {}

        for crop in crops:
            # Farmer Score: Assume preferences are met
            farmer_score = 1.0

            # Market Score (Profitability): Based on predicted price
            market_score = 0.5  # Default
            predicted_price = self.market_predictions.get(crop, 0.0)
            market_score = min(predicted_price / 2000.0, 1.0)  # Normalize (assuming $2000/ton is max)

            # Weather Score (Suitability): Based on temperature and rainfall
            weather_score = 0.5  # Default
            temp = float(weather_info.split("temperature of ")[1].split("°C")[0])
            rainfall = float(weather_info.split("rainfall of ")[1].split(" mm")[0])
            # Simplified: Ideal temp 15-30°C, ideal rainfall 30-70 mm
            temp_suitability = 1.0 if 15 <= temp <= 30 else 0.6
            rainfall_suitability = 1.0 if 30 <= rainfall <= 70 else 0.6
            weather_score = (temp_suitability + rainfall_suitability) / 2.0

            # Sustainability Sub-Scores
            metrics = self.sustainability_metrics.get(crop, {'carbon_score': 0.5, 'water_score': 0.5, 'erosion_score': 0.5})
            sustainability_score = (
                sustainability_sub_weights["carbon"] * metrics['carbon_score'] +
                sustainability_sub_weights["water"] * metrics['water_score'] +
                sustainability_sub_weights["erosion"] * metrics['erosion_score']
            ) / (sustainability_sub_weights["carbon"] + sustainability_sub_weights["water"] + sustainability_sub_weights["erosion"])

            # Total score
            total_score = (
                weights["farmer"] * farmer_score +
                weights["market"] * market_score +
                weights["weather"] * weather_score +
                weights["sustainability"] * sustainability_score
            )
            crop_scores[crop] = {
                'total_score': total_score,
                'carbon_score': metrics['carbon_score'],
                'water_score': metrics['water_score'],
                'erosion_score': metrics['erosion_score'],
                'market_score': market_score,
                'weather_score': weather_score,
                'farmer_score': farmer_score
            }

        # Rank crops by total score
        ranked_crops = sorted(crop_scores.items(), key=lambda x: x[1]['total_score'], reverse=True)

        # Generate recommendation with rationale
        recommendations = []
        for crop, scores in ranked_crops:
            market_rationale = f"high demand (${self.market_predictions.get(crop, 0.0):.2f}/ton)" if scores['market_score'] > 0.7 else "moderate demand"
            weather_rationale = "suitable weather" if scores['weather_score'] > 0.7 else "challenging weather"
            sustainability_rationale = "sustainable" if scores['carbon_score'] > 0.7 and scores['water_score'] > 0.7 and scores['erosion_score'] > 0.7 else "moderately sustainable"
            rationale = f"Plant {crop}: {market_rationale}, {weather_rationale}, {sustainability_rationale} (Score: {scores['total_score']:.2f})"
            recommendations.append(rationale)

        # Combine into final recommendation
        final_recommendation = "Recommendations:\n" + "\n".join(recommendations) + f"\n\nDetails:\nMarket Insights: {market_info}\nWeather Forecast: {weather_info}\nSustainability Notes: {sustainability_info}"

        # Store in SQLite
        with sqlite3.connect("Models/database/sustainable_farming.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop TEXT,
                    score REAL,
                    rationale TEXT,
                    carbon_score REAL,
                    water_score REAL,
                    erosion_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            for crop, scores in ranked_crops:
                cursor.execute(
                    "INSERT INTO recommendations (crop, score, rationale, carbon_score, water_score, erosion_score) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        crop,
                        scores['total_score'],
                        f"Plant {crop}: high demand, suitable weather, sustainable",
                        scores['carbon_score'],
                        scores['water_score'],
                        scores['erosion_score']
                    )
                )
            conn.commit()

        return final_recommendation

# Define the agents using the custom class
farmer_advisor = CustomAssistantAgent(
    name="FarmerAdvisor",
    system_message="I am the Farmer Advisor. I process farmer inputs to suggest suitable crops.",
    llm_config=False
)

market_researcher = CustomAssistantAgent(
    name="MarketResearcher",
    system_message="I am the Market Researcher. I analyze market trends to suggest profitable crops.",
    llm_config=False
)

weather_analyst = CustomAssistantAgent(
    name="WeatherAnalyst",
    system_message="I am the Weather Analyst. I predict weather conditions based on farm inputs.",
    llm_config=False
)

sustainability_expert = CustomAssistantAgent(
    name="SustainabilityExpert",
    system_message="I am the Sustainability Expert. I evaluate crops for sustainability.",
    llm_config=False
)

central_coordinator = CustomAssistantAgent(
    name="CentralCoordinator",
    system_message="I am the Central Coordinator. I integrate agent outputs to provide recommendations.",
    llm_config=False
)

# Define a custom speaker selection function
def custom_select_speaker(last_speaker, groupchat):
    agents = [farmer_advisor, market_researcher, weather_analyst, sustainability_expert, central_coordinator]
    if last_speaker is None:
        return agents[0]
    last_index = agents.index(last_speaker)
    next_index = (last_index + 1) % len(agents)
    return agents[next_index]

# Set up the group chat for agent interactions
group_chat = GroupChat(
    agents=[farmer_advisor, market_researcher, weather_analyst, sustainability_expert, central_coordinator],
    messages=[],
    max_round=5
)

group_chat.select_speaker = custom_select_speaker

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=False
)

# Function to initiate the group chat with dynamic farmer inputs
def run_agent_collaboration(land_size, soil_type, crop_preference):
    initial_message = (
        f"Let’s generate a farming recommendation. "
        f"FarmerAdvisor, please suggest crops based on a {land_size}-hectare farm with {soil_type.lower()} soil "
        f"and a preference for {crop_preference.lower()}. "
        f"MarketResearcher, provide market insights for those crops. "
        f"WeatherAnalyst, predict weather for the next 3 months. "
        f"SustainabilityExpert, evaluate the sustainability of the suggested crops."
    )
    central_coordinator.initiate_chat(
        group_chat_manager,
        message=initial_message
    )

if __name__ == "__main__":
    run_agent_collaboration(land_size=5, soil_type="Sandy", crop_preference="Grains")
