import sqlite3
import pandas as pd
import joblib
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import accuracy_score
import warnings
import os

class FarmerAdvisor:
    def __init__(self, db_path='Models/database/sustainable_farming.db'):
        self.db_path = db_path
        self.model = None
        self.encoders = {}
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

    def _preprocess(self):
        self.df.dropna(inplace=True)
        self.encoders['crop'] = LabelEncoder()
        self.df['Crop_encoded'] = self.encoders['crop'].fit_transform(self.df['Crop_Type'])

    def _train_model(self):
        feature_cols = [
            'Soil_pH', 'Soil_Moisture', 'Temperature_C', 'Rainfall_mm',
            'Fertilizer_Usage_kg', 'Pesticide_Usage_kg', 'Crop_Yield_ton'
        ]
        X = self.df[feature_cols]
        y = self.df['Crop_encoded']

        # Compute class-balanced sample weights
        sample_weights = compute_sample_weight(class_weight='balanced', y=y)

        # Stratified split to ensure crop distribution is preserved
        X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
            X, y, sample_weights, test_size=0.2, stratify=y, random_state=42
        )

        self.model = DecisionTreeClassifier(
            max_depth=8, min_samples_split=6, class_weight='balanced', random_state=42
        )
        self.model.fit(X_train, y_train, sample_weight=w_train)

        # Save model & encoders
        joblib.dump(self.model, 'models/farmer_advisor_model.pkl')
        joblib.dump(self.encoders, 'models/farmer_encoders.pkl')

        # Accuracy evaluation
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"\n FarmerAdvisor Model Accuracy: {acc:.2f}")

        # Print rules
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rules = export_text(self.model, feature_names=feature_cols)
            print("\n Decision Tree Rules for Crop Recommendation:\n")
            print(rules)

    def recommend(self, soil_ph, soil_moisture, temp, rainfall, fertilizer, pesticide, crop_yield):
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
