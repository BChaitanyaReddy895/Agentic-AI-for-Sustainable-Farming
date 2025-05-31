def run_agent_collaboration(land_size, soil_type, crop_preference):
    # Simulated recommendation logic
    recommendation = {
        'recommendation': f"""Based on your {land_size} hectares of {soil_type} soil and preference for {crop_preference},
        we recommend focusing on sustainable farming practices.\n
        Key points:\n
        - Use crop rotation to maintain soil health\n
        - Implement water-efficient irrigation\n
        - Consider organic farming methods""",
        'chart_data': [{
            'crop': crop_preference.lower(),
            'labels': ['Market Score', 'Weather Score', 'Sustainability Score', 'Carbon Score', 
                      'Water Score', 'Erosion Score', 'Final Score'],
            'values': [85, 75, 90, 80, 85, 70, 82]
        }]
    }
    return recommendation