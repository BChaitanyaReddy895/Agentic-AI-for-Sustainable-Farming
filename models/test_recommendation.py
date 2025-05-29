from Models.central_coordinator import CentralCoordinator

# Initialize the CentralCoordinator
coordinator = CentralCoordinator()

# Generate recommendation with sample input values
result = coordinator.generate_recommendation(
    soil_ph=4.0,
    soil_moisture=10,
    temperature=32,
    rainfall=35,
    fertilizer=0.5,
    pesticide=0.3,
    crop_yield=15
)

# Print recommendation results
print("\n--- Final Crop Recommendation ---")
for key, value in result.items():
    print(f"{key}: {value}")

# Automatically plot the result scores
CentralCoordinator.plot_scores(result)
