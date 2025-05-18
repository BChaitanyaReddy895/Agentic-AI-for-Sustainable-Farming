import sqlite3
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

class MarketResearcher:
    def __init__(self, db_path="Models/database/sustainable_farming.db"):
        self.db_path = db_path
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self._train_all_models()

    def _train_all_models(self):
        with sqlite3.connect(self.db_path) as conn:
            products = pd.read_sql(
                "SELECT DISTINCT Product FROM market_researcher", conn
            )['Product'].dropna().unique().tolist()

            for product in products:
                df = pd.read_sql("""
                    SELECT Product, Market_Price_per_ton, Demand_Index, Supply_Index,
                           Competitor_Price_per_ton, Economic_Indicator,
                           Weather_Impact_Score, Seasonal_Factor, Consumer_Trend_Index
                    FROM market_researcher
                    WHERE Product = ?
                """, conn, params=(product,))

                if len(df) < 10:
                    continue

                df['Seasonal_Factor'] = df['Seasonal_Factor'].fillna('None')

                le = LabelEncoder()
                df['Seasonal_Factor_Encoded'] = le.fit_transform(df['Seasonal_Factor'])
                self.encoders[product] = le

                features = ['Demand_Index', 'Supply_Index', 'Competitor_Price_per_ton',
                            'Economic_Indicator', 'Weather_Impact_Score',
                            'Seasonal_Factor_Encoded', 'Consumer_Trend_Index']

                X = df[features]
                y = df['Market_Price_per_ton']

                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                self.scalers[product] = scaler

                X_train, _, y_train, _ = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)

                model_name = product.strip().lower().replace(" ", "_")
                joblib.dump(model, f"models/market_model_{model_name}.pkl")
                joblib.dump(le, f"models/market_encoder_{model_name}.pkl")
                joblib.dump(scaler, f"models/market_scaler_{model_name}.pkl")

    def forecast(self, product, input_features):
        model_name = product.strip().lower().replace(" ", "_")
        model_path = f"models/market_model_{model_name}.pkl"
        encoder_path = f"models/market_encoder_{model_name}.pkl"
        scaler_path = f"models/market_scaler_{model_name}.pkl"

        if not os.path.exists(model_path) or not os.path.exists(encoder_path) or not os.path.exists(scaler_path):
            raise ValueError(f"No trained model found for product: {product}")

        model = joblib.load(model_path)
        le = joblib.load(encoder_path)
        scaler = joblib.load(scaler_path)

        sf = input_features.get('Seasonal_Factor', 'None')
        if sf not in le.classes_:
            sf = le.classes_[0]

        sf_encoded = le.transform([sf])[0]

        input_df = pd.DataFrame([[
            input_features.get('Demand_Index', 0),
            input_features.get('Supply_Index', 0),
            input_features.get('Competitor_Price_per_ton', 0),
            input_features.get('Economic_Indicator', 0),
            input_features.get('Weather_Impact_Score', 0),
            sf_encoded,
            input_features.get('Consumer_Trend_Index', 0)
        ]], columns=[
            'Demand_Index', 'Supply_Index', 'Competitor_Price_per_ton',
            'Economic_Indicator', 'Weather_Impact_Score',
            'Seasonal_Factor_Encoded', 'Consumer_Trend_Index'
        ])

        input_scaled = scaler.transform(input_df)
        prediction = model.predict(input_scaled)
        return prediction.tolist()
