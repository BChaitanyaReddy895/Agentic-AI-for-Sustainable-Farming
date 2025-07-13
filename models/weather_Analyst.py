import sqlite3
import pandas as pd
import joblib
import os
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherAnalyst:

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'sustainable_farming.db'))
        self.db_path = db_path
        # Always use absolute path for models_dir
        self.models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))

        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            logger.info(f"Created models directory at: {self.models_dir}")

        self.scaler = StandardScaler()
        self.df = None
        temp_model_path = os.path.join(self.models_dir, 'temp_model.pkl')
        rain_model_path = os.path.join(self.models_dir, 'rain_model.pkl')
        scaler_path = os.path.join(self.models_dir, 'weather_scaler.pkl')
        if os.path.exists(temp_model_path) and os.path.exists(rain_model_path) and os.path.exists(scaler_path):
            # Models already exist, do not retrain
            pass
        else:
            self._prepare_data()
            self._train_models()

    def _prepare_data(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                self.df = pd.read_sql("""
                    SELECT Soil_pH, Soil_Moisture, Temperature_C, Rainfall_mm,
                           Fertilizer_Usage_kg, Pesticide_Usage_kg
                    FROM farmer_advisor
                """, conn)
            if self.df.empty:
                logger.warning("No data found in farmer_advisor table.")
                raise ValueError("The farmer_advisor table is empty. Please populate it with data.")
            logger.info(f"Loaded {len(self.df)} rows from farmer_advisor table.")
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
            raise sqlite3.Error(f"Failed to connect to database or query data: {str(e)}")
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            raise

    def _train_models(self):
        try:
            features = ['Soil_pH', 'Soil_Moisture', 'Fertilizer_Usage_kg', 'Pesticide_Usage_kg']
            X = self.df[features]
            X_scaled = self.scaler.fit_transform(X)

            y_temp = self.df['Temperature_C']
            y_rain = self.df['Rainfall_mm']

            temp_model = RandomForestRegressor(n_estimators=100, random_state=42)
            temp_model.fit(X_scaled, y_temp)

            rain_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rain_model.fit(X_scaled, y_rain)

            temp_model_path = os.path.join(self.models_dir, 'temp_model.pkl')
            rain_model_path = os.path.join(self.models_dir, 'rain_model.pkl')
            scaler_path = os.path.join(self.models_dir, 'weather_scaler.pkl')

            # Remove files if they exist to avoid OneDrive/Windows file lock issues
            for path in [temp_model_path, rain_model_path, scaler_path]:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    logger.warning(f"Could not remove existing model file {path}: {e}")

            joblib.dump(temp_model, temp_model_path)
            logger.info(f"Saved temperature model at {temp_model_path}")

            joblib.dump(rain_model, rain_model_path)
            logger.info(f"Saved rainfall model at {rain_model_path}")

            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Saved scaler at {scaler_path}")
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            raise

    def forecast(self, soil_ph, soil_moisture, fertilizer, pesticide):
        try:
            temp_model = joblib.load(os.path.join(self.models_dir, 'temp_model.pkl'))
            rain_model = joblib.load(os.path.join(self.models_dir, 'rain_model.pkl'))
            scaler = joblib.load(os.path.join(self.models_dir, 'weather_scaler.pkl'))

            input_df = pd.DataFrame([[soil_ph, soil_moisture, fertilizer, pesticide]],
                                    columns=['Soil_pH', 'Soil_Moisture', 'Fertilizer_Usage_kg', 'Pesticide_Usage_kg'])
            input_scaled = scaler.transform(input_df)

            predicted_temp = temp_model.predict(input_scaled)[0]
            predicted_rain = rain_model.predict(input_scaled)[0]
            return {'temperature': [predicted_temp], 'rainfall': [predicted_rain]}
        except Exception as e:
            logger.error(f"Error during forecasting: {str(e)}")
            raise