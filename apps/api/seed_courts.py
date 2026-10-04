import sqlite3
import uuid

courts_data = [
    ("Supreme Court of India", "SUPREME_COURT", "National", "New Delhi"),
    ("High Court of Delhi", "HIGH_COURT", "State", "New Delhi"),
    ("High Court of Bombay", "HIGH_COURT", "State", "Mumbai"),
    ("High Court of Madras", "HIGH_COURT", "State", "Chennai"),
    ("High Court of Karnataka", "HIGH_COURT", "State", "Bengaluru"),
    ("District Court, Tis Hazari", "DISTRICT_COURT", "District", "New Delhi"),
    ("District Court, Karkardooma", "DISTRICT_COURT", "District", "New Delhi"),
    ("City Civil Court", "CIVIL_COURT", "City", "Mumbai"),
    ("Sessions Court", "SESSIONS_COURT", "District", "Chennai"),
    ("Family Court", "FAMILY_COURT", "District", "Bengaluru"),
    ("Lok Adalat", "LOK_ADALAT", "District", "National"),
    ("Fast Track Court", "FAST_TRACK_COURT", "District", "National"),
    ("Consumer Disputes Redressal Commission", "CONSUMER_COURT", "State", "National"),
    ("National Green Tribunal", "TRIBUNAL", "National", "New Delhi")
]

conn = sqlite3.connect('counselconnect.db')
cursor = conn.cursor()

for court_name, court_type, jurisdiction, address in courts_data:
    # Check if already exists
    cursor.execute("SELECT id FROM courts WHERE court_name = ?", (court_name,))
    if not cursor.fetchone():
        court_id = uuid.uuid4().hex
        cursor.execute(
            "INSERT INTO courts (id, court_name, court_type, jurisdiction, address) VALUES (?, ?, ?, ?, ?)",
            (court_id, court_name, court_type, jurisdiction, address)
        )

conn.commit()
conn.close()
print("Courts successfully seeded!")
