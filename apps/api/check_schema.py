import sqlite3
db = sqlite3.connect('counselconnect.db')
cursor = db.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='audit_logs'")
print(cursor.fetchone()[0])
