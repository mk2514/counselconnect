import sqlite3

def clean_db():
    conn = sqlite3.connect('d:/counselconnect/apps/api/counselconnect.db')
    cursor = conn.cursor()
    
    # SQLite DATE columns are just TEXT. SQLAlchemy fails if it contains a time component when Date is expected.
    cursor.execute("DELETE FROM cases WHERE incident_date LIKE '% %'")
    print(f'Deleted {cursor.rowcount} corrupted cases.')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    clean_db()
