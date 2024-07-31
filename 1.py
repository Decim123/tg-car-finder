import sqlite3

def create_log_db():
    conn = sqlite3.connect('database/log.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS log (
        passenger_id INTEGER,
        driver_id INTEGER,
        filepath TEXT,
        PRIMARY KEY (passenger_id, driver_id)
    )
    ''')
    conn.close()

create_log_db()
