from database.db import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL,
        role TEXT NOT NULL,
        district TEXT,
        asha_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        district TEXT,
        phone TEXT,
        ambulance TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        woman_id INTEGER,
        title TEXT,
        message TEXT,
        level TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(woman_id) REFERENCES users(id)
    )
    """)

#visitlog
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asha_id INTEGER,
        woman_id INTEGER,
        visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT,
        FOREIGN KEY(asha_id) REFERENCES users(id),
        FOREIGN KEY(woman_id) REFERENCES users(id)
    )
    """)    

    # PREGNANCY RECORD
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pregnancies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        woman_id INTEGER,
        month INTEGER,
        week INTEGER,
        weight REAL,
        hb REAL,
        bp TEXT,
        sugar REAL,
        risk_score INTEGER,
        risk_level TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(woman_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mental_health (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        woman_id INTEGER,
        mood INTEGER,
        stress INTEGER,
        sleep INTEGER,
        probability REAL,
        risk_level TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(woman_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        woman_id INTEGER,
        question TEXT,
        response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(woman_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()