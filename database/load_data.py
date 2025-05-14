import pandas as pd
import sqlite3

# Load CSV files
farmer_df = pd.read_csv('data/farmer_advisor_dataset.csv')
market_df = pd.read_csv('data/market_researcher_dataset.csv')

# Connect to SQLite DB
conn = sqlite3.connect('database/sustainable_farming.db')

# Load into SQLite tables
farmer_df.to_sql('farmer_advisor', conn, if_exists='replace', index=False)
market_df.to_sql('market_researcher', conn, if_exists='replace', index=False)

conn.close()
print("CSV data loaded into database.")
