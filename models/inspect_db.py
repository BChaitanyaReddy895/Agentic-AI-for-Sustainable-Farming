import sqlite3

db_path = "Models/database/sustainable_farming.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# List columns of each table
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print(f"\nColumns in table '{table_name}':")
    for col in columns:
        print(f"  {col[1]} (type: {col[2]})")

conn.close()
