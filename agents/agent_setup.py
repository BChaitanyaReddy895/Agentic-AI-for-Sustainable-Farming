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
            "FarmerAdvisor": self.farmer_advisor_response(messages),
            "MarketResearcher": self.market_researcher_response(messages),
            "WeatherAnalyst": "For the next 3 months, expect low rainfall and high temperatures, which may require irrigation.",
            "SustainabilityExpert": self.sustainability_expert_response(messages),
            "CentralCoordinator": self.central_coordinator_logic(messages, sender)
        }
        return responses.get(self.name, "No response available.")

    def farmer_advisor_response(self, messages):
        # Extract farm inputs from the initial message
        initial_message = next((msg["content"] for msg in messages if msg["name"] == "CentralCoordinator"), "")
        if "hectare farm with" in initial_message:
            # Parse the message to get land size, soil type, and crop preference
            parts = initial_message.split("suggest crops based on a ")[1].split(" farm with ")
            land_size = parts[0].split("-hectare")[0]
            soil_type_part = parts[1].split(" soil and a preference for ")[0]
            crop_preference = parts[1].split(" soil and a preference for ")[1].split(".")[0]
            # For now, suggest crops based on crop preference (simplified logic)
            if crop_preference.lower() == "grains":
                return f"Based on a {land_size}-hectare farm with {soil_type_part} soil and a preference for {crop_preference}, I suggest planting wheat and barley."
            elif crop_preference.lower() == "vegetables":
                return f"Based on a {land_size}-hectare farm with {soil_type_part} soil and a preference for {crop_preference}, I suggest planting carrots and potatoes."
            else:  # Default to fruits or other preferences
                return f"Based on a {land_size}-hectare farm with {soil_type_part} soil and a preference for {crop_preference}, I suggest planting apples and oranges."
        return "No farm inputs provided to suggest crops."

    def market_researcher_response(self, messages):
        # Extract crops from FarmerAdvisor's response
        farmer_response = next((msg["content"] for msg in messages if msg["name"] == "FarmerAdvisor"), "")
        if "suggest planting" in farmer_response:
            crops = farmer_response.split("suggest planting ")[1].split(" and ")
            # Simulate market insights for the crops
            market_insights = []
            for crop in crops:
                crop = crop.strip(".")
                if crop == "wheat":
                    market_insights.append("Wheat prices are expected to rise by 15% next season")
                elif crop == "barley":
                    market_insights.append("barley has steady demand")
                elif crop == "carrots":
                    market_insights.append("carrots have a growing demand in local markets")
                elif crop == "potatoes":
                    market_insights.append("potatoes are seeing stable prices")
                elif crop == "apples":
                    market_insights.append("apples are in high demand due to export opportunities")
                elif crop == "oranges":
                    market_insights.append("oranges have a moderate market with seasonal fluctuations")
            return ", and ".join(market_insights) + "."
        return "No crops suggested to provide market insights."

    def sustainability_expert_response(self, messages):
        # Extract crops from FarmerAdvisor's response
        farmer_response = next((msg["content"] for msg in messages if msg["name"] == "FarmerAdvisor"), "")
        if "suggest planting" in farmer_response:
            crops = farmer_response.split("suggest planting ")[1].split(" and ")
            # Simulate sustainability evaluation with carbon footprint, water usage, and soil erosion metrics
            sustainability_notes = []
            for crop in crops:
                crop = crop.strip(".")
                if crop == "wheat":
                    sustainability_notes.append(
                        "Wheat has a low carbon footprint due to minimal fertilizer use, requires moderate water with drip irrigation, "
                        "and its root system helps reduce soil erosion."
                    )
                elif crop == "barley":
                    sustainability_notes.append(
                        "Barley has a slightly higher carbon footprint due to more tillage, requires moderate water with efficient irrigation, "
                        "and also helps prevent soil erosion."
                    )
                elif crop == "carrots":
                    sustainability_notes.append(
                        "Carrots have a moderate carbon footprint, require low water with proper scheduling, "
                        "and their growth cycle helps reduce soil erosion."
                    )
                elif crop == "potatoes":
                    sustainability_notes.append(
                        "Potatoes have a higher carbon footprint due to intensive farming, require significant water, "
                        "but can reduce soil erosion with proper management."
                    )
                elif crop == "apples":
                    sustainability_notes.append(
                        "Apples have a moderate carbon footprint, require regular water for orchards, "
                        "and their deep roots help prevent soil erosion."
                    )
                elif crop == "oranges":
                    sustainability_notes.append(
                        "Oranges have a moderate carbon footprint, require substantial water for irrigation, "
                        "and their root systems offer moderate soil erosion prevention."
                    )
            return " ".join(sustainability_notes)
        return "No crops suggested to evaluate sustainability."

    def central_coordinator_logic(self, messages, sender):
        # Placeholder for Step 5: Will be implemented later to include scoring and database storage
        agent_responses = {}
        for message in messages:
            sender_name = message.get("name")
            content = message.get("content")
            if sender_name and content and sender_name != "CentralCoordinator":
                agent_responses[sender_name] = content
        return "Recommendation generation will be implemented in Step 5."

# Define the agents using the custom class
farmer_advisor = CustomAssistantAgent(
    name="FarmerAdvisor",
    system_message="I am the Farmer Advisor. I process farmer inputs like land size, soil type, and crop preferences to suggest suitable crops.",
    llm_config=False
)

market_researcher = CustomAssistantAgent(
    name="MarketResearcher",
    system_message="I am the Market Researcher. I analyze market trends, crop prices, and demand forecasts to suggest profitable crops.",
    llm_config=False
)

weather_analyst = CustomAssistantAgent(
    name="WeatherAnalyst",
    system_message="I am the Weather Analyst. I predict weather conditions based on historical data.",
    llm_config=False
)

sustainability_expert = CustomAssistantAgent(
    name="SustainabilityExpert",
    system_message="I am the Sustainability Expert. I evaluate crops based on carbon footprint, water usage, and soil erosion prevention.",
    llm_config=False
)

central_coordinator = CustomAssistantAgent(
    name="CentralCoordinator",
    system_message="I am the Central Coordinator. I integrate outputs from all agents to provide unified farming recommendations.",
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
        f"Let’s generate a farming recommendation."
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
    # Example usage with dynamic inputs
    run_agent_collaboration(land_size=5, soil_type="Sandy", crop_preference="Grains")
