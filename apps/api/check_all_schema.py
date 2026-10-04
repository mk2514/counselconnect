import sqlite3
db = sqlite3.connect('counselconnect.db')
cursor = db.cursor()
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
for row in cursor.fetchall():
    if "now()" in (row[1] or ""):
        print(f"Table {row[0]} HAS now(): {row[1]}")
