from Models.central_coordinator import CentralCoordinator

coordinator = CentralCoordinator()

result = coordinator.generate_recommendation(
soil_ph=6.0,
    soil_moisture=30,
    temperature=22,
    rainfall=50,
    fertilizer=15,
    pesticide=5,
    crop_yield=20

)


print("\n---Final Crop Recommendation---")
for key, value in result.items():
    print(f"{key}: {value}")
