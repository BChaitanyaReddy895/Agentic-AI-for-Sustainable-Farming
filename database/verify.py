import sqlite3

conn = sqlite3.connect('sustainable_farming.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM market_researcher_normalized where Market_ID = 1")
print(cursor.fetchall())

conn.close()
