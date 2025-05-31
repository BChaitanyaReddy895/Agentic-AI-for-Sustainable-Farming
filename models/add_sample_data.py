import sqlite3
import random

def add_sample_data():
    db_path = "Models/database/sustainable_farming.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Sample crops
    crops = ['Wheat', 'Rice', 'Corn', 'Soybeans', 'Cotton']

    # Generate and insert sample data
    for _ in range(50):  # Add 50 sample records
        cursor.execute("""
            INSERT INTO farmer_advisor (
                Soil_pH, Soil_Moisture, Temperature_C, Rainfall_mm,
                Fertilizer_Usage_kg, Pesticide_Usage_kg, Crop_Yield_ton,
                Crop_Type, Sustainability_Score,
                Carbon_Footprint_Score, Water_Score, Erosion_Score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            round(random.uniform(5.5, 7.5), 2),  # Soil_pH
            round(random.uniform(20, 40), 2),    # Soil_Moisture
            round(random.uniform(15, 35), 2),    # Temperature_C
            round(random.uniform(30, 100), 2),   # Rainfall_mm
            round(random.uniform(10, 30), 2),    # Fertilizer_Usage_kg
            round(random.uniform(1, 10), 2),     # Pesticide_Usage_kg
            round(random.uniform(2, 5), 2),      # Crop_Yield_ton
            random.choice(crops),                # Crop_Type
            round(random.uniform(0.5, 1.0), 2),  # Sustainability_Score
            round(random.uniform(0.5, 1.0), 2),  # Carbon_Footprint_Score
            round(random.uniform(0.5, 1.0), 2),  # Water_Score
            round(random.uniform(0.5, 1.0), 2)   # Erosion_Score
        ))

    conn.commit()
    conn.close()
    print("Sample data added successfully!")

if __name__ == "__main__":
    add_sample_data() 
import sqlite3
import random

def add_sample_data():
    db_path = "Models/database/sustainable_farming.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Sample crops
    crops = ['Wheat', 'Rice', 'Corn', 'Soybeans', 'Cotton']

    # Generate and insert sample data
    for _ in range(50):  # Add 50 sample records
        cursor.execute("""
            INSERT INTO farmer_advisor (
                Soil_pH, Soil_Moisture, Temperature_C, Rainfall_mm,
                Fertilizer_Usage_kg, Pesticide_Usage_kg, Crop_Yield_ton,
                Crop_Type, Sustainability_Score,
                Carbon_Footprint_Score, Water_Score, Erosion_Score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            round(random.uniform(5.5, 7.5), 2),  # Soil_pH
            round(random.uniform(20, 40), 2),    # Soil_Moisture
            round(random.uniform(15, 35), 2),    # Temperature_C
            round(random.uniform(30, 100), 2),   # Rainfall_mm
            round(random.uniform(10, 30), 2),    # Fertilizer_Usage_kg
            round(random.uniform(1, 10), 2),     # Pesticide_Usage_kg
            round(random.uniform(2, 5), 2),      # Crop_Yield_ton
            random.choice(crops),                # Crop_Type
            round(random.uniform(0.5, 1.0), 2),  # Sustainability_Score
            round(random.uniform(0.5, 1.0), 2),  # Carbon_Footprint_Score
            round(random.uniform(0.5, 1.0), 2),  # Water_Score
            round(random.uniform(0.5, 1.0), 2)   # Erosion_Score
        ))

    conn.commit()
    conn.close()
    print("Sample data added successfully!")

if __name__ == "__main__":
    add_sample_data() 