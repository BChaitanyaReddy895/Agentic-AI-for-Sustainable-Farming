import sqlite3
import os

# Create Models/database directory if it doesn't exist
os.makedirs("Models/database", exist_ok=True)

# Connect to database
db_path = "Models/database/sustainable_farming.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create farmer_advisor table
cursor.execute('''
CREATE TABLE IF NOT EXISTS farmer_advisor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Soil_pH REAL,
    Soil_Moisture REAL,
    Temperature_C REAL,
    Rainfall_mm REAL,
    Fertilizer_Usage_kg REAL,
    Pesticide_Usage_kg REAL,
    Crop_Yield_ton REAL,
    Crop_Type TEXT,
    Sustainability_Score REAL,
    Carbon_Footprint_Score REAL,
    Erosion_Score REAL,
    Water_Score REAL
)
''')

# Create market_researcher table
cursor.execute('''
CREATE TABLE IF NOT EXISTS market_researcher (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Product TEXT,
    Market_Price_per_ton REAL,
    Demand_Index REAL,
    Supply_Index REAL,
    Competitor_Price_per_ton REAL,
    Economic_Indicator REAL,
    Weather_Impact_Score REAL,
    Seasonal_Factor TEXT,
    Consumer_Trend_Index REAL
)
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database setup completed successfully!") 