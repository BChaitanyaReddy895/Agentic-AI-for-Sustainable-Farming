import joblib
from Models.farmer_advisor import FarmerAdvisor
from Models.market_Researcher import MarketResearcher
from Models.weather_Analyst import WeatherAnalyst
from Models.sustainability_Expert import SustainabilityExpert
import matplotlib.pyplot as plt


class CentralCoordinator:
    def __init__(self):
        db_path = "Models/database/sustainable_farming.db"
        self.farmer_advisor = FarmerAdvisor(db_path=db_path)
        self.market_researcher = MarketResearcher(db_path=db_path)
        self.weather_analyst = WeatherAnalyst(db_path=db_path)
        self.sustainability_expert = SustainabilityExpert(db_path=db_path)

    def generate_recommendation(self, soil_ph, soil_moisture, temperature, rainfall,
                                fertilizer, pesticide, crop_yield):

        # 1. Recommend crop using FarmerAdvisor
        crop = self.farmer_advisor.recommend(
            soil_ph, soil_moisture, temperature, rainfall,
            fertilizer, pesticide, crop_yield
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
            'Predicted Rainfall': round(predicted_rain, 2)
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
        crop_yield=3.5
    )

    print("\n --- Final Recommendation ---")
    for k, v in result.items():
        print(f"{k}: {v}")

    CentralCoordinator.plot_scores(result)
