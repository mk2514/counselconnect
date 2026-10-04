import sqlite3
db = sqlite3.connect('counselconnect.db')
with open('schema.txt', 'w') as f:
    for row in db.execute("SELECT name, sql FROM sqlite_master WHERE sql IS NOT NULL"):
        f.write(f"--- {row[0]} ---\n{row[1]}\n\n")
