import sqlite3
from security import hash_password

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    service_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    photo_before TEXT,
    photo_after TEXT,
    employee_note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (employee_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    date TEXT NOT NULL,
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES users(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
)
""")

hashed_admin_password = hash_password("admin123")
cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role)
VALUES ('admin', ?, 'admin')
""", (hashed_admin_password,))

cursor.execute("""
INSERT OR IGNORE INTO services (name, price) VALUES
    ('Nettoyage intérieur complet', 5000),
    ('Nettoyage extérieur', 3000),
    ('Nettoyage complet (int + ext)', 7500),
    ('Lavage moteur', 4000),
    ('Polish et cire', 6000)
""")

conn.commit()
conn.close()

print("✅ Base de données initialisée avec succès")
print("📌 Compte admin créé : username='admin', password='admin123'")
print("📌 Services par défaut ajoutés")
