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
    full_name TEXT,
    phone TEXT,
    email TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    duration INTEGER,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    vehicle_brand TEXT,
    vehicle_model TEXT,
    vehicle_plate TEXT,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    client_name TEXT,
    service_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    photo_before TEXT,
    photo_after TEXT,
    employee_note TEXT,
    payment_status TEXT DEFAULT 'En attente',
    payment_method TEXT,
    amount_paid INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id),
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

cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

hashed_admin_password = hash_password("admin123")
cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role, full_name)
VALUES ('admin', ?, 'admin', 'Administrateur Principal')
""", (hashed_admin_password,))

cursor.execute("""
INSERT OR IGNORE INTO services (name, description, price, duration) VALUES
    ('Nettoyage intérieur complet', 'Nettoyage complet de l''intérieur du véhicule', 5000, 60),
    ('Nettoyage extérieur', 'Lavage extérieur + lustrage', 3000, 30),
    ('Nettoyage complet (int + ext)', 'Nettoyage intérieur + extérieur', 7500, 90),
    ('Lavage moteur', 'Nettoyage du compartiment moteur', 4000, 45),
    ('Polish et cire', 'Polissage et cirage de la carrosserie', 6000, 60),
    ('Detailing Premium', 'Service complet haut de gamme', 15000, 180)
""")

conn.commit()
conn.close()

print("✅ Base de données améliorée avec succès")
print("📌 Compte admin : username='admin', password='admin123'")
print("📌 Services premium ajoutés")
print("📌 Gestion clients activée")
print("📌 Système de paiements intégré")
