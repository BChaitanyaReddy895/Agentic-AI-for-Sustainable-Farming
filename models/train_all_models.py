from concurrent.futures import ProcessPoolExecutor
import os
from Models.farmer_advisor import FarmerAdvisor
from Models.market_Researcher import MarketResearcher
from Models.weather_Analyst import WeatherAnalyst
from Models.sustainability_Expert import SustainabilityExpert

# Set path to your SQLite database
DB_PATH = "Models/database/sustainable_farming.db"

# Ensure models directory exists
os.makedirs("models", exist_ok=True)

# --- Training Functions for Each Model ---

def train_farmer_advisor():
    print(" Training FarmerAdvisor...")
    try:
        FarmerAdvisor(db_path=DB_PATH)
        print(" FarmerAdvisor trained.")
    except Exception as e:
        print(f" FarmerAdvisor failed: {e}")

def train_market_researcher():
    print(" Training MarketResearcher...")
    try:
        MarketResearcher(db_path=DB_PATH)
        print(" MarketResearcher trained.")
    except Exception as e:
        print(f" MarketResearcher failed: {e}")

def train_weather_analyst():
    print(" Training WeatherAnalyst...")
    try:
        WeatherAnalyst(db_path=DB_PATH)
        print(" WeatherAnalyst trained.")
    except Exception as e:
        print(f"WeatherAnalyst failed: {e}")

def train_sustainability_expert():
    print(" Loading SustainabilityExpert (no model training needed)...")
    try:
        SustainabilityExpert(db_path=DB_PATH)
        print(" SustainabilityExpert loaded.")
    except Exception as e:
        print(f" SustainabilityExpert failed: {e}")

# --- Main parallel trainer ---
if __name__ == "__main__":
    print("\n Starting parallel training for all models...\n")
    
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(train_farmer_advisor),
            executor.submit(train_market_researcher),
            executor.submit(train_weather_analyst),
            executor.submit(train_sustainability_expert),
        ]

        for future in futures:
            future.result()

    print("\n All models trained and initialized successfully.")
