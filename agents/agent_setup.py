# Importing necessary autogen classes and MySQL connector
from autogen import AssistantAgent, GroupChat, GroupChatManager
import mysql.connector

# Custom AssistantAgent class to override generate_reply
class CustomAssistantAgent(AssistantAgent):
    def generate_reply(self, messages=None, sender=None):
        # If messages are not provided, fetch them from chat history
        if messages is None and sender is not None:
            messages = self.chat_messages.get(sender, [])

        # Responses for each agent
        responses = {
            "FarmerAdvisor": "Based on a 5-hectare farm with sandy soil and a preference for grains, I suggest planting wheat and barley.",
            "MarketResearcher": "Wheat prices are expected to rise by 15% next season, and barley has steady demand.",
            "WeatherAnalyst": "For the next 3 months, expect low rainfall and high temperatures, which may require irrigation.",
            "SustainabilityExpert": "Wheat and barley are sustainable for sandy soil, but use drip irrigation to minimize water usage.",
            "CentralCoordinator": self.central_coordinator_logic(messages, sender)
        }
        return responses.get(self.name, "No response available.")

    def central_coordinator_logic(self, messages, sender):
        # Collect responses from the chat messages
        agent_responses = {}
        for message in messages:
            sender_name = message.get("name")
            content = message.get("content")
            if sender_name and content and sender_name != "CentralCoordinator":
                agent_responses[sender_name] = content

        # Extract relevant information
        crops = agent_responses.get("FarmerAdvisor", "").split("planting ")[-1].split(" and ")  # e.g., ["wheat", "barley"]
        market_info = agent_responses.get("MarketResearcher", "")
        weather_info = agent_responses.get("WeatherAnalyst", "")
        sustainability_info = agent_responses.get("SustainabilityExpert", "")

        # Weighted scoring system
        weights = {"sustainability": 0.4, "weather": 0.3, "market": 0.2, "farmer": 0.1}
        crop_scores = {}

        for crop in crops:
            # Farmer Advisor (preferences already met, so score is 1)
            farmer_score = 1.0

            # Market Researcher: Score based on market trends
            market_score = 0.8 if "rise" in market_info.lower() and crop in market_info.lower() else 0.5

            # Weather Analyst: Score based on weather suitability
            weather_score = 0.6 if "low rainfall" in weather_info.lower() else 0.8  # Wheat and barley are somewhat drought-tolerant

            # Sustainability Expert: Score based on sustainability
            sustainability_score = 0.9 if "sustainable" in sustainability_info.lower() and crop in sustainability_info.lower() else 0.4

            # Calculate total score
            total_score = (
                weights["farmer"] * farmer_score +
                weights["market"] * market_score +
                weights["weather"] * weather_score +
                weights["sustainability"] * sustainability_score
            )
            crop_scores[crop] = total_score

        # Select the top crop
        recommended_crop = max(crop_scores, key=crop_scores.get)
        recommendation = (
            f"Recommendation: Plant {recommended_crop}. "
            f"Market Insights: {market_info}. "
            f"Weather Forecast: {weather_info}. "
            f"Sustainability Notes: {sustainability_info}. "
            f"Score: {crop_scores[recommended_crop]:.2f}"
        )

        # Store the recommendation in MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="Chaitu895@",  # Replace with your MySQL password
            database="farming_db"
        )
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                crop VARCHAR(50),
                score FLOAT,
                rationale TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert the recommendation
        cursor.execute(
            "INSERT INTO recommendations (crop, score, rationale) VALUES (%s, %s, %s)",
            (recommended_crop, crop_scores[recommended_crop], recommendation)
        )
        conn.commit()
        conn.close()

        return recommendation

# Define the agents using the custom class
farmer_advisor = CustomAssistantAgent(
    name="FarmerAdvisor",
    system_message="I am the Farmer Advisor. I process farmer inputs like land size, soil type, and crop preferences to suggest suitable crops.",
    llm_config=False  # Disable LLM for this agent
)

market_researcher = CustomAssistantAgent(
    name="MarketResearcher",
    system_message="I am the Market Researcher. I analyze market trends, crop prices, and demand forecasts to suggest profitable crops.",
    llm_config=False  # Disable LLM for this agent
)

weather_analyst = CustomAssistantAgent(
    name="WeatherAnalyst",
    system_message="I am the Weather Analyst. I predict weather conditions based on historical data.",
    llm_config=False  # Disable LLM for this agent
)

sustainability_expert = CustomAssistantAgent(
    name="SustainabilityExpert",
    system_message="I am the Sustainability Expert. I ensure farming practices minimize environmental impact.",
    llm_config=False  # Disable LLM for this agent
)

central_coordinator = CustomAssistantAgent(
    name="CentralCoordinator",
    system_message="I am the Central Coordinator. I integrate outputs from all agents to provide unified farming recommendations.",
    llm_config=False  # Disable LLM for this agent
)

# Define a custom speaker selection function
def custom_select_speaker(last_speaker, groupchat):
    # List of agents in the desired order
    agents = [farmer_advisor, market_researcher, weather_analyst, sustainability_expert, central_coordinator]
    # If there's no last speaker (first round), start with the first agent
    if last_speaker is None:
        return agents[0]
    # Find the index of the last speaker and select the next agent
    last_index = agents.index(last_speaker)
    next_index = (last_index + 1) % len(agents)
    return agents[next_index]

# Set up the group chat for agent interactions
group_chat = GroupChat(
    agents=[farmer_advisor, market_researcher, weather_analyst, sustainability_expert, central_coordinator],
    messages=[],
    max_round=5  # Limit the number of rounds to avoid infinite loops
)

# Set the custom speaker selection function
group_chat.select_speaker = custom_select_speaker

# Create a group chat manager to handle interactions
group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=False  # Disable LLM for the group chat manager
)

# Function to initiate the group chat and simulate interactions
def run_agent_collaboration():
    # Central Coordinator initiates the conversation
    initial_message = (
        "Let’s generate a farming recommendation. "
        "FarmerAdvisor, please suggest crops based on a 5-hectare farm with sandy soil and a preference for grains. "
        "MarketResearcher, provide market insights for those crops. "
        "WeatherAnalyst, predict weather for the next 3 months. "
        "SustainabilityExpert, evaluate the sustainability of the suggested crops."
    )
    # Start the group chat
    central_coordinator.initiate_chat(
        group_chat_manager,
        message=initial_message
    )

# Run the collaboration
if __name__ == "__main__":
    run_agent_collaboration()