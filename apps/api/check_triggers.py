import sqlite3
db = sqlite3.connect('counselconnect.db')
cursor = db.cursor()
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
for row in cursor.fetchall():
    print(f"TRIGGER {row[0]}: {row[1]}")
