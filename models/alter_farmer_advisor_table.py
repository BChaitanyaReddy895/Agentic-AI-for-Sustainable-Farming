import sqlite3

db_path = "Models/database/sustainable_farming.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column_if_not_exists(table, column, col_type):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"Added column {column} to {table}")
    else:
        print(f"Column {column} already exists in {table}")

add_column_if_not_exists('farmer_advisor', 'Carbon_Footprint_Score', 'REAL')
add_column_if_not_exists('farmer_advisor', 'Erosion_Score', 'REAL')
add_column_if_not_exists('farmer_advisor', 'Water_Score', 'REAL')

conn.commit()
conn.close()
print("Schema update completed.") 