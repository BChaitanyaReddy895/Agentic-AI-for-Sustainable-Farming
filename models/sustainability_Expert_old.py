import sqlite3
import pandas as pd
import numpy as np
import os

class SustainabilityExpert:
    def __init__(self, db_path="Models/database/sustainable_farming.db"):
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'sustainable_farming.db'))
        self.sustainability_db = self._load_sustainability_data()

    def _load_sustainability_data(self):
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql("""
                SELECT Crop_Type, 
                       AVG(Sustainability_Score) AS avg_score,
                       AVG(Fertilizer_Usage_kg) AS avg_fertilizer,
                       AVG(Soil_Moisture) AS avg_moisture,
                       AVG(Pesticide_Usage_kg) AS avg_pesticide,
                       AVG(Crop_Yield_ton) AS avg_yield
                FROM farmer_advisor
                GROUP BY Crop_Type
            """, conn)
            return df.set_index('Crop_Type').to_dict('index')

    def calculate_carbon_score(self, fertilizer, pesticide, crop_yield):
        # Carbon footprint score based on fertilizer and pesticide usage
        # Lower usage and higher yield means better score
        fertilizer_impact = 1 - (fertilizer / 100)  # Normalize to 0-1
        pesticide_impact = 1 - (pesticide / 20)    # Normalize to 0-1
        yield_impact = min(crop_yield / 5, 1)      # Normalize to 0-1
        
        return (0.4 * fertilizer_impact + 0.3 * pesticide_impact + 0.3 * yield_impact)

    def calculate_water_score(self, soil_moisture, rainfall):
        # Water score based on soil moisture and rainfall
        # Optimal moisture is between 30-40%
        moisture_score = 1 - abs(soil_moisture - 35) / 35
        rainfall_score = min(rainfall / 100, 1)
        
        return (0.6 * moisture_score + 0.4 * rainfall_score)

    def calculate_erosion_score(self, soil_ph, soil_moisture):
        # Erosion score based on soil pH and moisture
        # Optimal pH is between 6-7
        ph_score = 1 - abs(soil_ph - 6.5) / 3.5
        moisture_score = 1 - abs(soil_moisture - 35) / 35
        
        return (0.5 * ph_score + 0.5 * moisture_score)

    def evaluate(self, crops, soil_ph, soil_moisture, rainfall, fertilizer, pesticide, crop_yield):
        """Evaluate sustainability of crops based on environmental factors"""
        results = {}
        for crop in crops:
            # Calculate individual scores
            carbon_score = self.calculate_carbon_score(fertilizer, pesticide, crop_yield)
            water_score = self.calculate_water_score(soil_moisture, rainfall)
            erosion_score = self.calculate_erosion_score(soil_ph, soil_moisture)
            
            # Calculate overall sustainability score
            sustainability_score = (
                0.4 * carbon_score +
                0.3 * water_score +
                0.3 * erosion_score
            )
            
            results[crop] = {
                'sustainability': sustainability_score,
                'carbon': carbon_score,
                'water': water_score,
                'erosion': erosion_score
            }
        
        # Return the first crop's results since we're only evaluating one crop at a time
        return crops[0], results[crops[0]]