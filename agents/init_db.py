import sqlite3
import os

def initialize_db():
    # Create database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    # Database path
    db_path = os.path.join(db_dir, 'farm_recommendations.db')
    
    # Create tables
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop TEXT NOT NULL,
                score REAL NOT NULL,
                rationale TEXT,
                market_score REAL,
                weather_score REAL,
                sustainability_score REAL,
                carbon_score REAL,
                water_score REAL,
                erosion_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    return db_path