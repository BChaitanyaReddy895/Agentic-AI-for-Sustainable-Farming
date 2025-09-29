import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPestDiseasePredictor:
    """
    Enhanced pest and disease predictor using Llama 2 for intelligent analysis
    """
    
    def __init__(self):
        # Initialize Llama 2 model for pest/disease analysis
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "meta-llama/Llama-2-7b-chat-hf"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            logger.info(f"Loaded Llama 2 model for pest prediction on {self.device}")
        except Exception as e:
            logger.warning(f"Could not load Llama 2 model: {e}. Using rule-based fallback.")
            self.model = None
            self.tokenizer = None
        
        # Pest and disease database
        self.pest_database = self._load_pest_database()
        self.disease_database = self._load_disease_database()
    
    def _load_pest_database(self) -> Dict:
        """Load comprehensive pest database"""
        return {
            'wheat': {
                'aphids': {
                    'conditions': {'temp_range': (15, 25), 'humidity_range': (40, 80), 'rainfall_range': (20, 100)},
                    'symptoms': 'Yellowing leaves, sticky honeydew, stunted growth',
                    'treatment': 'Neem oil spray, beneficial insects, resistant varieties',
                    'risk_factors': ['high_nitrogen', 'dense_planting', 'poor_air_circulation']
                },
                'rust': {
                    'conditions': {'temp_range': (15, 25), 'humidity_range': (70, 95), 'rainfall_range': (50, 150)},
                    'symptoms': 'Orange or brown pustules on leaves and stems',
                    'treatment': 'Fungicide application, crop rotation, resistant varieties',
                    'risk_factors': ['high_humidity', 'warm_temperatures', 'previous_infestation']
                },
                'armyworm': {
                    'conditions': {'temp_range': (20, 30), 'humidity_range': (50, 90), 'rainfall_range': (30, 120)},
                    'symptoms': 'Chewed leaves, defoliation, larvae visible',
                    'treatment': 'Bacillus thuringiensis, pheromone traps, natural predators',
                    'risk_factors': ['warm_weather', 'high_humidity', 'dense_vegetation']
                }
            },
            'rice': {
                'brown_planthopper': {
                    'conditions': {'temp_range': (25, 35), 'humidity_range': (70, 95), 'rainfall_range': (100, 300)},
                    'symptoms': 'Yellowing and wilting, honeydew secretion, sooty mold',
                    'treatment': 'Systemic insecticides, resistant varieties, proper water management',
                    'risk_factors': ['high_nitrogen', 'excessive_irrigation', 'dense_planting']
                },
                'bacterial_leaf_blight': {
                    'conditions': {'temp_range': (25, 35), 'humidity_range': (80, 95), 'rainfall_range': (150, 400)},
                    'symptoms': 'Yellow stripes on leaves, wilting, plant death',
                    'treatment': 'Copper-based fungicides, resistant varieties, proper drainage',
                    'risk_factors': ['high_humidity', 'warm_temperatures', 'poor_drainage']
                },
                'rice_blast': {
                    'conditions': {'temp_range': (20, 30), 'humidity_range': (85, 95), 'rainfall_range': (100, 300)},
                    'symptoms': 'Diamond-shaped lesions on leaves, neck rot, yield loss',
                    'treatment': 'Fungicide application, resistant varieties, proper spacing',
                    'risk_factors': ['high_humidity', 'cool_temperatures', 'excessive_nitrogen']
                }
            },
            'corn': {
                'corn_borer': {
                    'conditions': {'temp_range': (20, 30), 'humidity_range': (50, 80), 'rainfall_range': (40, 120)},
                    'symptoms': 'Holes in stalks, ear damage, reduced yield',
                    'treatment': 'Bt corn varieties, beneficial insects, crop rotation',
                    'risk_factors': ['warm_weather', 'dense_planting', 'previous_infestation']
                },
                'corn_earworm': {
                    'conditions': {'temp_range': (25, 35), 'humidity_range': (60, 85), 'rainfall_range': (50, 150)},
                    'symptoms': 'Damage to ears, frass in silk, reduced quality',
                    'treatment': 'Insecticides, Bt varieties, pheromone traps',
                    'risk_factors': ['warm_weather', 'high_humidity', 'late_planting']
                },
                'gray_leaf_spot': {
                    'conditions': {'temp_range': (20, 30), 'humidity_range': (80, 95), 'rainfall_range': (80, 200)},
                    'symptoms': 'Gray lesions on leaves, premature death',
                    'treatment': 'Fungicide application, resistant varieties, crop rotation',
                    'risk_factors': ['high_humidity', 'warm_temperatures', 'continuous_corn']
                }
            },
            'tomato': {
                'aphids': {
                    'conditions': {'temp_range': (20, 30), 'humidity_range': (50, 80), 'rainfall_range': (30, 100)},
                    'symptoms': 'Curled leaves, honeydew, virus transmission',
                    'treatment': 'Neem oil, beneficial insects, reflective mulches',
                    'risk_factors': ['high_nitrogen', 'dense_planting', 'poor_air_circulation']
                },
                'late_blight': {
                    'conditions': {'temp_range': (15, 25), 'humidity_range': (85, 95), 'rainfall_range': (50, 150)},
                    'symptoms': 'Water-soaked lesions, white mold, rapid spread',
                    'treatment': 'Copper fungicides, resistant varieties, proper spacing',
                    'risk_factors': ['high_humidity', 'cool_temperatures', 'poor_air_circulation']
                },
                'whitefly': {
                    'conditions': {'temp_range': (25, 35), 'humidity_range': (40, 70), 'rainfall_range': (20, 80)},
                    'symptoms': 'Yellowing leaves, honeydew, sooty mold',
                    'treatment': 'Yellow sticky traps, beneficial insects, reflective mulches',
                    'risk_factors': ['warm_weather', 'low_humidity', 'dense_planting']
                }
            }
        }
    
    def _load_disease_database(self) -> Dict:
        """Load comprehensive disease database"""
        return {
            'fungal_diseases': {
                'powdery_mildew': {
                    'conditions': {'temp_range': (15, 25), 'humidity_range': (70, 90), 'rainfall_range': (20, 100)},
                    'symptoms': 'White powdery coating on leaves',
                    'treatment': 'Sulfur fungicides, resistant varieties, proper spacing',
                    'affected_crops': ['wheat', 'tomato', 'cucumber', 'grape']
                },
                'downy_mildew': {
                    'conditions': {'temp_range': (10, 20), 'humidity_range': (85, 95), 'rainfall_range': (50, 200)},
                    'symptoms': 'Yellow spots on upper leaves, white mold underneath',
                    'treatment': 'Copper fungicides, resistant varieties, proper drainage',
                    'affected_crops': ['lettuce', 'cucumber', 'grape', 'onion']
                }
            },
            'bacterial_diseases': {
                'bacterial_wilt': {
                    'conditions': {'temp_range': (25, 35), 'humidity_range': (70, 90), 'rainfall_range': (50, 200)},
                    'symptoms': 'Wilting, yellowing, plant death',
                    'treatment': 'Copper-based bactericides, resistant varieties, crop rotation',
                    'affected_crops': ['tomato', 'pepper', 'cucumber', 'eggplant']
                }
            },
            'viral_diseases': {
                'mosaic_viruses': {
                    'conditions': {'temp_range': (20, 30), 'humidity_range': (50, 80), 'rainfall_range': (30, 120)},
                    'symptoms': 'Mottled leaves, stunted growth, reduced yield',
                    'treatment': 'Virus-free seeds, vector control, resistant varieties',
                    'affected_crops': ['tomato', 'cucumber', 'tobacco', 'pepper']
                }
            }
        }
    
    def predict_with_llama(self, crop_type: str, weather_data: Dict, soil_data: Dict) -> str:
        """
        Use Llama 2 to predict pest and disease risks
        """
        if not self.model or not self.tokenizer:
            return self._rule_based_prediction(crop_type, weather_data, soil_data)
        
        try:
            # Prepare context for Llama 2
            context = f"""
            As an agricultural pest and disease expert, analyze the following conditions for {crop_type} farming:
            
            Weather Conditions:
            - Temperature: {weather_data.get('temperature', 'N/A')}°C
            - Humidity: {weather_data.get('humidity', 'N/A')}%
            - Rainfall: {weather_data.get('rainfall', 'N/A')} mm
            - Wind Speed: {weather_data.get('wind_speed', 'N/A')} m/s
            - Description: {weather_data.get('description', 'N/A')}
            
            Soil Conditions:
            - pH: {soil_data.get('ph', 'N/A')}
            - Moisture: {soil_data.get('moisture', 'N/A')}%
            - Type: {soil_data.get('type', 'N/A')}
            
            Provide a comprehensive pest and disease risk assessment for {crop_type} including:
            1. Most likely pests and diseases based on current conditions
            2. Risk level (Low/Medium/High) for each threat
            3. Specific symptoms to watch for
            4. Recommended preventive measures
            5. Treatment options if infestation occurs
            6. Timing for monitoring and intervention
            
            Focus on practical, actionable advice for farmers.
            """
            
            # Tokenize and generate response
            inputs = self.tokenizer.encode(context, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 300,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the generated part
            generated_text = response[len(context):].strip()
            
            return generated_text if generated_text else self._rule_based_prediction(crop_type, weather_data, soil_data)
            
        except Exception as e:
            logger.error(f"Error in Llama 2 pest prediction: {e}")
            return self._rule_based_prediction(crop_type, weather_data, soil_data)
    
    def predict(self, crop_type: str, soil_ph: float, soil_moisture: float, 
                temperature: float, rainfall: float, additional_data: Dict = None) -> str:
        """
        Main prediction method that combines Llama 2 analysis with rule-based fallback
        """
        try:
            # Prepare weather and soil data
            weather_data = {
                'temperature': temperature,
                'humidity': 65.0,  # Default if not provided
                'rainfall': rainfall,
                'wind_speed': 3.0,  # Default if not provided
                'description': 'partly cloudy'  # Default if not provided
            }
            
            soil_data = {
                'ph': soil_ph,
                'moisture': soil_moisture,
                'type': 'loamy'  # Default if not provided
            }
            
            # Update with additional data if provided
            if additional_data:
                weather_data.update(additional_data.get('weather', {}))
                soil_data.update(additional_data.get('soil', {}))
            
            # Get Llama 2 prediction
            llama_prediction = self.predict_with_llama(crop_type, weather_data, soil_data)
            
            # Get rule-based risk assessment
            risk_assessment = self._assess_risks(crop_type, weather_data, soil_data)
            
            # Combine predictions
            combined_prediction = self._combine_predictions(llama_prediction, risk_assessment, crop_type)
            
            return combined_prediction
            
        except Exception as e:
            logger.error(f"Error in pest prediction: {e}")
            return self._rule_based_prediction(crop_type, weather_data, soil_data)
    
    def _assess_risks(self, crop_type: str, weather_data: Dict, soil_data: Dict) -> Dict:
        """Assess pest and disease risks using rule-based approach"""
        risks = {
            'pests': [],
            'diseases': [],
            'overall_risk': 'low',
            'recommendations': []
        }
        
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 65)
        rainfall = weather_data.get('rainfall', 50)
        soil_ph = soil_data.get('ph', 6.5)
        soil_moisture = soil_data.get('moisture', 50)
        
        crop_lower = crop_type.lower()
        
        # Check for specific pests based on crop type
        if crop_lower in self.pest_database:
            for pest_name, pest_info in self.pest_database[crop_lower].items():
                conditions = pest_info['conditions']
                
                # Check temperature conditions
                temp_ok = conditions['temp_range'][0] <= temp <= conditions['temp_range'][1]
                humidity_ok = conditions['humidity_range'][0] <= humidity <= conditions['humidity_range'][1]
                rainfall_ok = conditions['rainfall_range'][0] <= rainfall <= conditions['rainfall_range'][1]
                
                if temp_ok and humidity_ok and rainfall_ok:
                    risks['pests'].append({
                        'name': pest_name,
                        'risk_level': 'high',
                        'symptoms': pest_info['symptoms'],
                        'treatment': pest_info['treatment']
                    })
                elif any([temp_ok, humidity_ok, rainfall_ok]):
                    risks['pests'].append({
                        'name': pest_name,
                        'risk_level': 'medium',
                        'symptoms': pest_info['symptoms'],
                        'treatment': pest_info['treatment']
                    })
        
        # Check for diseases
        for disease_category, diseases in self.disease_database.items():
            for disease_name, disease_info in diseases.items():
                if crop_lower in disease_info.get('affected_crops', []):
                    conditions = disease_info['conditions']
                    
                    temp_ok = conditions['temp_range'][0] <= temp <= conditions['temp_range'][1]
                    humidity_ok = conditions['humidity_range'][0] <= humidity <= conditions['humidity_range'][1]
                    rainfall_ok = conditions['rainfall_range'][0] <= rainfall <= conditions['rainfall_range'][1]
                    
                    if temp_ok and humidity_ok and rainfall_ok:
                        risks['diseases'].append({
                            'name': disease_name,
                            'category': disease_category,
                            'risk_level': 'high',
                            'symptoms': disease_info['symptoms'],
                            'treatment': disease_info['treatment']
                        })
        
        # Determine overall risk level
        high_risks = len([p for p in risks['pests'] if p['risk_level'] == 'high']) + \
                    len([d for d in risks['diseases'] if d['risk_level'] == 'high'])
        
        if high_risks > 0:
            risks['overall_risk'] = 'high'
        elif len(risks['pests']) + len(risks['diseases']) > 0:
            risks['overall_risk'] = 'medium'
        
        # Generate recommendations
        risks['recommendations'] = self._generate_recommendations(risks, crop_type)
        
        return risks
    
    def _generate_recommendations(self, risks: Dict, crop_type: str) -> List[str]:
        """Generate specific recommendations based on risk assessment"""
        recommendations = []
        
        if risks['overall_risk'] == 'high':
            recommendations.append("🚨 HIGH RISK: Immediate action required. Monitor crops daily.")
        elif risks['overall_risk'] == 'medium':
            recommendations.append("⚠️ MEDIUM RISK: Increased monitoring recommended.")
        else:
            recommendations.append("✅ LOW RISK: Continue regular monitoring.")
        
        # Add specific recommendations for pests
        for pest in risks['pests']:
            if pest['risk_level'] == 'high':
                recommendations.append(f"🐛 High risk of {pest['name']}: {pest['treatment']}")
        
        # Add specific recommendations for diseases
        for disease in risks['diseases']:
            if disease['risk_level'] == 'high':
                recommendations.append(f"🦠 High risk of {disease['name']}: {disease['treatment']}")
        
        # General recommendations
        recommendations.append("📅 Monitor crops every 2-3 days during high-risk periods.")
        recommendations.append("🔍 Look for early symptoms and take preventive action.")
        recommendations.append("🌱 Consider resistant varieties for future plantings.")
        
        return recommendations
    
    def _combine_predictions(self, llama_prediction: str, risk_assessment: Dict, crop_type: str) -> str:
        """Combine Llama 2 prediction with rule-based assessment"""
        combined = f"🤖 AI Analysis for {crop_type}:\n\n"
        combined += llama_prediction + "\n\n"
        
        combined += "📊 Risk Assessment:\n"
        combined += f"Overall Risk Level: {risk_assessment['overall_risk'].upper()}\n\n"
        
        if risk_assessment['pests']:
            combined += "🐛 Pest Risks:\n"
            for pest in risk_assessment['pests']:
                combined += f"- {pest['name']} ({pest['risk_level']} risk)\n"
            combined += "\n"
        
        if risk_assessment['diseases']:
            combined += "🦠 Disease Risks:\n"
            for disease in risk_assessment['diseases']:
                combined += f"- {disease['name']} ({disease['risk_level']} risk)\n"
            combined += "\n"
        
        combined += "💡 Recommendations:\n"
        for rec in risk_assessment['recommendations']:
            combined += f"- {rec}\n"
        
        return combined
    
    def _rule_based_prediction(self, crop_type: str, weather_data: Dict, soil_data: Dict) -> str:
        """Fallback rule-based prediction when Llama 2 is not available"""
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 65)
        rainfall = weather_data.get('rainfall', 50)
        
        prediction = f"Pest and Disease Risk Assessment for {crop_type}:\n\n"
        
        # Basic risk assessment
        if temp > 30 and humidity > 80:
            prediction += "⚠️ High risk of fungal diseases due to hot, humid conditions.\n"
        elif temp < 15 and humidity > 85:
            prediction += "⚠️ High risk of bacterial diseases due to cool, wet conditions.\n"
        elif temp > 25 and humidity < 40:
            prediction += "⚠️ High risk of pest infestation due to hot, dry conditions.\n"
        else:
            prediction += "✅ Conditions appear favorable with low disease risk.\n"
        
        # General recommendations
        prediction += "\nGeneral Recommendations:\n"
        prediction += "- Monitor crops regularly for early signs of problems\n"
        prediction += "- Maintain proper spacing for air circulation\n"
        prediction += "- Use disease-resistant varieties when possible\n"
        prediction += "- Practice crop rotation to break pest cycles\n"
        
        return prediction
