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
    gps_latitude REAL,
    gps_longitude REAL,
    vehicle_brand TEXT,
    vehicle_model TEXT,
    vehicle_plate TEXT,
    notes TEXT,
    loyalty_points INTEGER DEFAULT 0,
    referral_code TEXT UNIQUE,
    referred_by INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referred_by) REFERENCES clients(id)
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
    travel_fee INTEGER DEFAULT 0,
    total_amount INTEGER DEFAULT 0,
    distance_km REAL DEFAULT 0,
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

cursor.execute("""
CREATE TABLE IF NOT EXISTS payment_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    total_amount INTEGER NOT NULL,
    amount_paid INTEGER DEFAULT 0,
    deposit_amount INTEGER DEFAULT 0,
    installments INTEGER DEFAULT 1,
    status TEXT DEFAULT 'En cours',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payment_installments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_plan_id INTEGER NOT NULL,
    due_date TEXT NOT NULL,
    amount INTEGER NOT NULL,
    paid_amount INTEGER DEFAULT 0,
    status TEXT DEFAULT 'En attente',
    paid_at TEXT,
    payment_method TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_plan_id) REFERENCES payment_plans(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS loyalty_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    points INTEGER NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    job_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    unit TEXT,
    quantity REAL DEFAULT 0,
    min_quantity REAL DEFAULT 0,
    unit_cost INTEGER DEFAULT 0,
    supplier TEXT,
    last_purchase_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    quantity REAL NOT NULL,
    job_id INTEGER,
    employee_id INTEGER,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES inventory(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (employee_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cash_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL,
    category TEXT,
    amount INTEGER NOT NULL,
    description TEXT,
    job_id INTEGER,
    employee_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (employee_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
INSERT OR IGNORE INTO app_settings (key, value) VALUES
    ('currency', 'FCFA'),
    ('travel_fee_per_km', '200'),
    ('loyalty_points_per_fcfa', '1'),
    ('referral_bonus_points', '500'),
    ('free_service_points', '10000'),
    ('company_latitude', '0'),
    ('company_longitude', '0')
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

cursor.execute("""
INSERT OR IGNORE INTO inventory (name, category, unit, quantity, min_quantity, unit_cost, supplier) VALUES
    ('Shampoing auto', 'Produits', 'Litres', 20, 5, 2500, 'Fournisseur Local'),
    ('Cire liquide', 'Produits', 'Litres', 10, 3, 3500, 'Fournisseur Local'),
    ('Éponges', 'Matériel', 'Unités', 50, 10, 200, 'Fournisseur Local'),
    ('Chiffons microfibre', 'Matériel', 'Unités', 30, 10, 500, 'Fournisseur Local'),
    ('Polish', 'Produits', 'Litres', 8, 2, 4000, 'Fournisseur Local'),
    ('Détergent moteur', 'Produits', 'Litres', 15, 5, 3000, 'Fournisseur Local'),
    ('Brosse de lavage', 'Matériel', 'Unités', 10, 3, 1500, 'Fournisseur Local'),
    ('Aspirateur (sacs)', 'Consommables', 'Unités', 25, 5, 300, 'Fournisseur Local')
""")

conn.commit()
conn.close()

print("✅ Base de données AUTO CLEAN PRO - ÉDITION AFRICAINE initialisée avec succès!")
print("")
print("📌 Compte admin : username='admin', password='admin123'")
print("📌 6 services premium ajoutés")
print("📌 8 produits d'inventaire ajoutés")
print("")
print("🌍 NOUVELLES FONCTIONNALITÉS AFRICAINES :")
print("   ✅ Paiements échelonnés (acompte + échéances)")
print("   ✅ Programme de fidélité avec points")
print("   ✅ Géolocalisation GPS des clients")
print("   ✅ Frais de déplacement automatiques")
print("   ✅ Gestion inventaire et stock")
print("   ✅ Système de parrainage")
print("   ✅ Livre de caisse (comptabilité)")
print("   ✅ Configuration multi-devises")
print("")
print("🚀 Votre application est prête pour la commercialisation !")
