"""End-to-end test: CentralCoordinator with Groq (Llama 3.3 70B)"""
import json, time
from models.central_coordinator import CentralCoordinator

coordinator = CentralCoordinator()

start = time.time()
result = coordinator.generate_recommendation(
    soil_ph=6.5, soil_moisture=75, temperature=28,
    rainfall=200, fertilizer=80, pesticide=2.0,
    crop_yield=3.5, land_size=1.0, city_name="Mumbai"
)
elapsed = time.time() - start

print(f"\n{'='*60}")
print(f"  FULL E2E TEST — Completed in {elapsed:.1f}s")
print(f"{'='*60}")
print(f"Recommended Crop : {result.get('Recommended Crop')}")
print(f"Farmer Confidence: {result.get('Farmer Confidence')}")
print(f"Farmer Reasoning : {str(result.get('Farmer Reasoning', ''))[:250]}")
print(f"\nMarket Analysis  : {str(result.get('Market Analysis', ''))[:250]}")
print(f"\nWeather Impact   : {str(result.get('Weather Impact', ''))[:250]}")
print(f"\nSustainability   : {str(result.get('Sustainability Score', ''))[:250]}")
print(f"\nPest Risk        : {str(result.get('Pest Risk', ''))[:250]}")
print(f"\nAI Synthesis     : {str(result.get('AI Synthesis', ''))[:400]}")
print(f"\nAI Confidence    : {result.get('AI Confidence')}")
print(f"\nAI Action Plan   : {str(result.get('AI Action Plan', ''))[:300]}")
print(f"\nAI Key Factors   : {str(result.get('AI Key Factors', ''))[:300]}")
print(f"\nAI Risk Summary  : {str(result.get('AI Risk Summary', ''))[:300]}")
print(f"{'='*60}")
