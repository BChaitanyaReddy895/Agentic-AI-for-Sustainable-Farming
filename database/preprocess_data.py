import sqlite3
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Connect to database
conn = sqlite3.connect('sustainable_farming.db')

### === Farmer Data Cleaning === ###
farmer_df = pd.read_sql_query("SELECT * FROM farmer_advisor", conn)

farmer_scaler = MinMaxScaler()
farmer_columns_to_normalize = [
    'Soil_pH', 'Soil_Moisture', 'Temperature_C', 'Rainfall_mm',
    'Fertilizer_Usage_kg', 'Pesticide_Usage_kg', 'Crop_Yield_ton', 'Sustainability_Score'
]
farmer_df[farmer_columns_to_normalize] = farmer_scaler.fit_transform(farmer_df[farmer_columns_to_normalize])

farmer_df.to_sql('farmer_advisor_normalized', conn, if_exists='replace', index=False)
print("✅ Farmer data normalized and saved.")


### === Market Data Cleaning === ###
market_df = pd.read_sql_query("SELECT * FROM market_researcher", conn)

market_scaler = MinMaxScaler()
market_columns_to_normalize = [
    'Market_Price_per_ton',
    'Demand_Index',
    'Supply_Index',
    'Competitor_Price_per_ton',
    'Economic_Indicator',
    'Weather_Impact_Score',
    'Consumer_Trend_Index'
]

market_df[market_columns_to_normalize] = market_scaler.fit_transform(market_df[market_columns_to_normalize])

# Keep 'Product' and 'Seasonal_Factor' as-is
market_df.to_sql('market_researcher_normalized', conn, if_exists='replace', index=False)
print("✅ Market data normalized and saved.")

conn.close()
