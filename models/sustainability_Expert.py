import sqlite3
import pandas as pd

class SustainabilityExpert:
    def __init__(self, db_path="Models/database/sustainable_farming.db"):
        self.db_path = db_path
        self.sustainability_db = self._load_sustainability_data()

    def _load_sustainability_data(self):
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql("""
                SELECT Crop_Type, 
                       AVG(Sustainability_Score) AS avg_score,
                       AVG(Fertilizer_Usage_kg) AS avg_fertilizer,
                       AVG(Soil_Moisture) AS avg_moisture

                FROM farmer_advisor
                GROUP BY Crop_Type
            """, conn)
            return df.set_index('Crop_Type').to_dict('index')

    def evaluate(self, crops):
        scores = {}
        for crop in crops:
            data = self.sustainability_db.get(crop, {})
            scores[crop] = (
                0.5 * data.get('avg_score', 0) +
                0.3 * (1 - data.get('avg_fertilizer', 0) / 100) +
                0.2 * data.get('avg_moisture', 0) / 100
            )
        return max(scores, key=scores.get)
