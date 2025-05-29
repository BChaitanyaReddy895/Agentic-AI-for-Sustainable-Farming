import sqlite3

conn = sqlite3.connect("Models/database/sustainable_farming.db")
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT Crop_Type FROM farmer_advisor;")
crops = cursor.fetchall()

print("Crops Available in Dataset:")
for crop in crops:
    print("-", crop[0])

conn.close()
