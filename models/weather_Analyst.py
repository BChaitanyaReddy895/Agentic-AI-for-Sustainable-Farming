import sqlite3
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class WeatherAnalyst:
    def __init__(self, db_path="Models/database/sustainable_farming.db"):
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'sustainable_farming.db'))
        self.scaler = StandardScaler()
        self._prepare_data()
        self._train_models()

    def _prepare_data(self):
        with sqlite3.connect(self.db_path) as conn:
            self.df = pd.read_sql("""
                SELECT Soil_pH, Soil_Moisture, Temperature_C, Rainfall_mm,
                       Fertilizer_Usage_kg, Pesticide_Usage_kg
                FROM farmer_advisor
            """, conn)

    def _train_models(self):
        features = ['Soil_pH', 'Soil_Moisture', 'Fertilizer_Usage_kg', 'Pesticide_Usage_kg']
        X = self.df[features]
        X_scaled = self.scaler.fit_transform(X)

        y_temp = self.df['Temperature_C']
        y_rain = self.df['Rainfall_mm']

        temp_model = RandomForestRegressor(n_estimators=100, random_state=42)
        temp_model.fit(X_scaled, y_temp)

        rain_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rain_model.fit(X_scaled, y_rain)

        joblib.dump(temp_model, 'models/temp_model.pkl')
        joblib.dump(rain_model, 'models/rain_model.pkl')
        joblib.dump(self.scaler, 'models/weather_scaler.pkl')

    def forecast(self, soil_ph, soil_moisture, fertilizer, pesticide):
        temp_model = joblib.load('models/temp_model.pkl')
        rain_model = joblib.load('models/rain_model.pkl')
        scaler = joblib.load('models/weather_scaler.pkl')

        input_df = pd.DataFrame([[soil_ph, soil_moisture, fertilizer, pesticide]],
                                columns=['Soil_pH', 'Soil_Moisture', 'Fertilizer_Usage_kg', 'Pesticide_Usage_kg'])
        input_scaled = scaler.transform(input_df)

        predicted_temp = temp_model.predict(input_scaled)[0]
        predicted_rain = rain_model.predict(input_scaled)[0]
        return {'temperature': [predicted_temp], 'rainfall': [predicted_rain]}