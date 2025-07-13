import sqlite3
import pandas as pd
import joblib
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
import os

class FarmerAdvisor:
    def __init__(self, db_path='Models/database/sustainable_farming.db'):
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'sustainable_farming.db'))
        self.model = None
        self.encoders = {}
        model_path = 'models/farmer_advisor_model.pkl'
        encoder_path = 'models/farmer_encoders.pkl'
        if os.path.exists(model_path) and os.path.exists(encoder_path):
            self.model = joblib.load(model_path)
            self.encoders = joblib.load(encoder_path)
        else:
            self._load_data()
            self._preprocess()
            self._train_model()

    def _load_data(self):
        with sqlite3.connect(self.db_path) as conn:
            self.df = pd.read_sql("""
                SELECT Soil_pH, Soil_Moisture, Temperature_C, Rainfall_mm,
                       Fertilizer_Usage_kg, Pesticide_Usage_kg, Crop_Yield_ton,
                       Crop_Type, Sustainability_Score
                FROM farmer_advisor
            """, conn)

        # Calculate Carbon Footprint, Water, and Erosion Scores
        self.df["Carbon_Footprint_Score"] = 100 - self.df["Fertilizer_Usage_kg"].fillna(0) * 0.6
        self.df["Water_Score"] = 100 - self.df["Soil_Moisture"].fillna(0) * 0.7
        self.df["Erosion_Score"] = 100 - self.df["Rainfall_mm"].fillna(0) * 0.5

        # Clip the scores to be within 0 to 100
        self.df["Carbon_Footprint_Score"] = self.df["Carbon_Footprint_Score"].clip(0, 100)
        self.df["Water_Score"] = self.df["Water_Score"].clip(0, 100)
        self.df["Erosion_Score"] = self.df["Erosion_Score"].clip(0, 100)

    def _preprocess(self):
        # Drop rows where Crop_Type is missing
        self.df.dropna(subset=['Crop_Type'], inplace=True)
        # Initialize and fit the label encoder
        self.encoders['crop'] = LabelEncoder()
        self.df['Crop_encoded'] = self.encoders['crop'].fit_transform(self.df['Crop_Type'].astype(str))

    def _train_model(self):
        # Define feature columns
        feature_cols = [
            'Soil_pH', 'Soil_Moisture', 'Temperature_C', 'Rainfall_mm',
            'Fertilizer_Usage_kg', 'Pesticide_Usage_kg', 'Crop_Yield_ton'
        ]
        # Prepare features and target
        X = self.df[feature_cols].fillna(0)
        y = self.df['Crop_encoded']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        self.model = DecisionTreeClassifier(
            max_depth=8,
            min_samples_split=6,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/farmer_advisor_model.pkl')
        joblib.dump(self.encoders, 'models/farmer_encoders.pkl')
        # Only print accuracy and rules if running as a script (not imported)
        if __name__ == "__main__":
            y_pred = self.model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            print(f"\nFarmerAdvisor Model Accuracy: {acc:.2f}")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                rules = export_text(self.model, feature_names=feature_cols)
                print("\nDecision Tree Rules for Crop Recommendation:\n")
                print(rules)

    def recommend(self, soil_ph, soil_moisture, temp, rainfall, fertilizer, pesticide, crop_yield,
                  carbon_score=None, water_score=None, erosion_score=None):
        if self.model is None:
            self.model = joblib.load('models/farmer_advisor_model.pkl')
        if not self.encoders:
            self.encoders = joblib.load('models/farmer_encoders.pkl')

        input_df = pd.DataFrame([[
            soil_ph, soil_moisture, temp, rainfall,
            fertilizer, pesticide, crop_yield
        ]], columns=[
            'Soil_pH', 'Soil_Moisture', 'Temperature_C', 'Rainfall_mm',
            'Fertilizer_Usage_kg', 'Pesticide_Usage_kg', 'Crop_Yield_ton'
        ])

        crop_code = self.model.predict(input_df)[0]
        return self.encoders['crop'].inverse_transform([crop_code])[0]