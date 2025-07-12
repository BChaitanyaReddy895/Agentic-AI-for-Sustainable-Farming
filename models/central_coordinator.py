import joblib
from Models.farmer_advisor import FarmerAdvisor
from Models.market_Researcher import MarketResearcher
from Models.weather_Analyst import WeatherAnalyst
from Models.sustainability_Expert import SustainabilityExpert
import matplotlib.pyplot as plt
from Models import weather_api
from Models.pest_disease_predictor import PestDiseasePredictor


class CentralCoordinator:
    def __init__(self):
        db_path = "database/sustainable_farming.db"
        self.farmer_advisor = FarmerAdvisor(db_path=db_path)
        self.market_researcher = MarketResearcher(db_path=db_path)
        self.weather_analyst = WeatherAnalyst(db_path=db_path)
        self.sustainability_expert = SustainabilityExpert(db_path=db_path)
        self.pest_predictor = PestDiseasePredictor()

    def generate_recommendation(self, soil_ph, soil_moisture, temperature, rainfall,
                                fertilizer, pesticide, crop_yield, city_name=None):
        warnings = []
        # If city_name is provided, fetch real-time weather
        if city_name:
            try:
                weather = weather_api.get_current_weather(city_name)
                temperature = weather['temperature']
                rainfall = weather['rainfall']
            except Exception as e:
                warnings.append(f"Weather API error: {e}")

        # 1. Recommend crop using FarmerAdvisor
        crop = self.farmer_advisor.recommend(
            soil_ph, soil_moisture, temperature, rainfall,
            fertilizer, pesticide, crop_yield
        )

        # Pest/Disease prediction
        pest_advice = self.pest_predictor.predict(
            crop_type=crop,
            soil_ph=soil_ph,
            soil_moisture=soil_moisture,
            temperature=temperature,
            rainfall=rainfall
        )

        # 2. Prepare dummy input for MarketResearcher
        market_features = {
            'Demand_Index': 0.5,
            'Supply_Index': 0.5,
            'Competitor_Price_per_ton': 1000.0,
            'Economic_Indicator': 0.8,
            'Weather_Impact_Score': 0.7,
            'Seasonal_Factor': 'Medium',
            'Consumer_Trend_Index': 0.6
        }

        # 3. Market forecast for recommended crop
        market_forecast = self.market_researcher.forecast(product=crop, input_features=market_features)
        market_score = market_forecast[0] / 1000  # Normalize

        # 4. Weather forecast
        weather_forecast = self.weather_analyst.forecast(
            soil_ph=soil_ph,
            soil_moisture=soil_moisture,
            fertilizer=fertilizer,
            pesticide=pesticide
        )
        predicted_temp = weather_forecast['temperature'][0]
        predicted_rain = weather_forecast['rainfall'][0]

        # 5. Weather suitability score
        weather_score = 1 - abs(predicted_temp - temperature) / 50 - abs(predicted_rain - rainfall) / 100
        weather_score = max(0, round(weather_score, 2))

        # 6. Get sustainability scores
        scores = self.sustainability_expert.evaluate(
            [crop],
            soil_ph=soil_ph,
            soil_moisture=soil_moisture,
            rainfall=rainfall,
            fertilizer=fertilizer,
            pesticide=pesticide,
            crop_yield=crop_yield
        )

        # Get the scores dictionary from the tuple returned by evaluate
        sustainability_scores = scores[1]  # Dictionary with all scores

        # 7. Final weighted score
        final_score = (
            0.25 * market_score +
            0.20 * weather_score +
            0.20 * sustainability_scores['sustainability'] +
            0.15 * sustainability_scores['carbon'] +
            0.10 * sustainability_scores['water'] +
            0.10 * sustainability_scores['erosion']
        )

        # 8. Enhanced Weather Warnings
        if city_name:
            # General weather hazards
            if temperature > 40:
                warnings.append("Warning: High temperature detected! Crop stress and yield loss possible.")
            if rainfall > 50:
                warnings.append("Warning: Heavy rainfall detected! Risk of flooding and waterlogging.")
            if temperature < 5:
                warnings.append("Warning: Low temperature detected! Frost risk and stunted growth possible.")
            if rainfall < 5:
                warnings.append("Warning: Very low rainfall detected! Drought risk and irrigation needed.")
            # Crop-specific suitability (example ranges, can be refined per crop)
            crop_temp_ranges = {
                'Wheat': (10, 25),
                'Rice': (20, 35),
                'Corn': (15, 35),
                'Soybeans': (15, 30),
                'Cotton': (20, 35)
            }
            crop_rain_ranges = {
                'Wheat': (30, 90),
                'Rice': (100, 200),
                'Corn': (50, 120),
                'Soybeans': (50, 100),
                'Cotton': (50, 100)
            }
            temp_range = crop_temp_ranges.get(crop)
            rain_range = crop_rain_ranges.get(crop)
            if temp_range:
                if not (temp_range[0] <= temperature <= temp_range[1]):
                    warnings.append(f"Warning: Real-time temperature ({temperature}°C) is outside the optimal range for {crop} ({temp_range[0]}–{temp_range[1]}°C).")
            if rain_range:
                if not (rain_range[0] <= rainfall <= rain_range[1]):
                    warnings.append(f"Warning: Real-time rainfall ({rainfall} mm) is outside the optimal range for {crop} ({rain_range[0]}–{rain_range[1]} mm).")
            # Severe weather
            if temperature > 45:
                warnings.append("Severe Alert: Extreme heat! Crop failure likely.")
            if temperature < 0:
                warnings.append("Severe Alert: Freezing conditions! Crop loss likely.")
            if rainfall > 100:
                warnings.append("Severe Alert: Torrential rain! Flooding and root rot risk.")

        result = {
            'Recommended Crop': crop,
            'Market Score': round(market_score, 2),
            'Weather Suitability Score': weather_score,
            'Sustainability Score': round(sustainability_scores['sustainability'], 2),
            'Carbon Footprint Score': round(sustainability_scores['carbon'], 2),
            'Water Score': round(sustainability_scores['water'], 2),
            'Erosion Score': round(sustainability_scores['erosion'], 2),
            'Final Score': round(final_score, 2),
            'Predicted Temperature': round(predicted_temp, 2),
            'Predicted Rainfall': round(predicted_rain, 2),
            'Real-Time Temperature': round(temperature, 2) if city_name else None,
            'Real-Time Rainfall': round(rainfall, 2) if city_name else None,
            'Warnings': warnings,
            'Pest/Disease Advice': pest_advice
        }
        return result

    @staticmethod
    def plot_scores(result):
        # Extract relevant numeric scores
        labels = []
        values = []
        for key in ['Market Score', 'Weather Suitability Score', 'Sustainability Score',
                    'Carbon Footprint Score', 'Water Score', 'Erosion Score', 'Final Score']:
            val = result.get(key)
            if val is not None:
                labels.append(key)
                values.append(val)

        # Plot
        plt.figure(figsize=(10, 8))
        colors = ['#4caf50', '#2196f3', '#ff9800', '#607d8b',
                 '#00bcd4', '#795548', '#e91e63']
        
        # Create pie chart
        plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, shadow=True)
        plt.title('Crop Recommendation Score Distribution')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.tight_layout()
        plt.show()


# Run it directly (for testing)
if __name__ == "__main__":
    coordinator = CentralCoordinator()
    result = coordinator.generate_recommendation(
        soil_ph=6.5,
        soil_moisture=35,
        temperature=27,
        rainfall=60,
        fertilizer=20,
        pesticide=5,
        crop_yield=3.5,
        city_name="New York"
    )

    print("\n --- Final Recommendation ---")
    for k, v in result.items():
        print(f"{k}: {v}")

    CentralCoordinator.plot_scores(result)