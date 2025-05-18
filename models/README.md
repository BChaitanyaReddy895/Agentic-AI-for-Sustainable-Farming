 Smart Crop Recommendation System

This project uses machine learning to recommend the most suitable crop based on environmental, agricultural, and economic factors such as:

- Soil pH & moisture
- Temperature & rainfall
- Fertilizer & pesticide usage
- Crop yield
- Sustainability & market demand

---

 Modules

 1. Farmer Advisor
Recommends the most suitable crop using a Decision Tree classifier trained on soil, weather, and chemical parameters.

 2. Weather Analyst
Predicts future temperature and rainfall using Random Forest Regressor, based on soil and chemical usage.

 3. Market Researcher
Forecasts market price trends using historical market data for each crop.

 4. Sustainability Expert
Evaluates which crop has the lowest carbon footprint, water usage, and highest sustainability score.

---

 How It Works

Each module runs independently and feeds into a central coordinator, which:

1. Recommends a crop
2. Predicts market price
3. Predicts future weather
4. Scores sustainability
5. Calculates a final recommendation score based on all factors

---

 Requirements

- Python 3.8+
- pandas, scikit-learn, joblib, sqlite3

-> To run the model
python test_recommendation.py

->To train all models
python train_all_models.py 
