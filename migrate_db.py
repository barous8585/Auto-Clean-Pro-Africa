"""
Script de migration pour ajouter les nouvelles tables de l'édition africaine
"""
import sqlite3
import os

def migrate_database():
    """Ajouter les nouvelles tables si elles n'existent pas"""
    if not os.path.exists("database.db"):
        return False
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Vérifier si les nouvelles tables existent déjà
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory'")
    if cursor.fetchone():
        conn.close()
        return False  # Tables déjà migrées
    
    print("🔄 Migration de la base de données vers l'édition africaine...")
    
    # Ajouter colonnes aux tables existantes
    try:
        cursor.execute("ALTER TABLE clients ADD COLUMN gps_latitude REAL")
        cursor.execute("ALTER TABLE clients ADD COLUMN gps_longitude REAL")
        cursor.execute("ALTER TABLE clients ADD COLUMN loyalty_points INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE clients ADD COLUMN referral_code TEXT UNIQUE")
        cursor.execute("ALTER TABLE clients ADD COLUMN referred_by INTEGER")
    except:
        pass  # Colonnes déjà existantes
    
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN travel_fee INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE jobs ADD COLUMN total_amount INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE jobs ADD COLUMN distance_km REAL DEFAULT 0")
    except:
        pass
    
    # Créer les nouvelles tables
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
    
    # Insérer les paramètres par défaut
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
    
    # Insérer les produits d'inventaire
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
    
    print("✅ Migration réussie ! Base de données mise à jour vers l'édition africaine.")
    return True

if __name__ == "__main__":
    migrate_database()
