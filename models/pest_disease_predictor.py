class PestDiseasePredictor:
    def predict(self, crop_type, soil_ph, soil_moisture, temperature, rainfall):
        # Example rules (customize as needed)
        crop = crop_type.lower()
        if crop == "tomato":
            if temperature > 28 and rainfall > 60:
                return "High risk of aphids in tomatoes; consider neem oil treatment."
            elif temperature < 15:
                return "Risk of late blight in tomatoes; monitor for leaf spots."
        elif crop == "wheat":
            if rainfall > 80:
                return "High risk of rust disease in wheat; consider fungicide spray."
        elif crop == "rice":
            if temperature > 30 and rainfall > 100:
                return "High risk of bacterial leaf blight in rice; ensure proper drainage."
        elif crop == "corn":
            if temperature > 32 and rainfall < 40:
                return "Risk of corn borer infestation; monitor for larvae."
        elif crop == "soybeans":
            if soil_moisture > 35:
                return "Risk of root rot in soybeans; avoid over-irrigation."
        # Add more rules for other crops as needed
        return "No significant pest or disease risk detected." 
class PestDiseasePredictor:
    def predict(self, crop_type, soil_ph, soil_moisture, temperature, rainfall):
        # Example rules (customize as needed)
        crop = crop_type.lower()
        if crop == "tomato":
            if temperature > 28 and rainfall > 60:
                return "High risk of aphids in tomatoes; consider neem oil treatment."
            elif temperature < 15:
                return "Risk of late blight in tomatoes; monitor for leaf spots."
        elif crop == "wheat":
            if rainfall > 80:
                return "High risk of rust disease in wheat; consider fungicide spray."
        elif crop == "rice":
            if temperature > 30 and rainfall > 100:
                return "High risk of bacterial leaf blight in rice; ensure proper drainage."
        elif crop == "corn":
            if temperature > 32 and rainfall < 40:
                return "Risk of corn borer infestation; monitor for larvae."
        elif crop == "soybeans":
            if soil_moisture > 35:
                return "Risk of root rot in soybeans; avoid over-irrigation."
        # Add more rules for other crops as needed
        return "No significant pest or disease risk detected." 