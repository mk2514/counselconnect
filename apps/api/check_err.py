import sqlite3
conn = sqlite3.connect('d:/counselconnect/apps/api/counselconnect.db')
cursor = conn.cursor()
cursor.execute("SELECT created_at, error_message FROM ai_jobs ORDER BY created_at DESC LIMIT 5;")
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]}")
conn.close()
