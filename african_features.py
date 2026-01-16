"""
Utilitaires pour fonctionnalités africaines
"""
import math
from database import get_connection
from datetime import datetime, timedelta


def get_app_setting(key, default=None):
    """Récupérer un paramètre de l'application"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default


def set_app_setting(key, value):
    """Définir un paramètre de l'application"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO app_settings (key, value, updated_at)
        VALUES (?, ?, ?)
    """, (key, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculer la distance entre deux points GPS en km (formule de Haversine)
    """
    if not all([lat1, lon1, lat2, lon2]):
        return 0
    
    R = 6371  # Rayon de la Terre en km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return round(R * c, 2)


def calculate_travel_fee(distance_km):
    """Calculer les frais de déplacement selon la distance"""
    fee_per_km = int(get_app_setting('travel_fee_per_km', 200))
    return int(distance_km * fee_per_km)


def add_loyalty_points(client_id, points, description, job_id=None):
    """Ajouter des points de fidélité à un client"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO loyalty_transactions (client_id, points, type, description, job_id)
        VALUES (?, ?, 'credit', ?, ?)
    """, (client_id, points, description, job_id))
    
    cursor.execute("""
        UPDATE clients SET loyalty_points = loyalty_points + ? WHERE id = ?
    """, (points, client_id))
    
    conn.commit()
    conn.close()


def deduct_loyalty_points(client_id, points, description):
    """Déduire des points de fidélité"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT loyalty_points FROM clients WHERE id = ?", (client_id,))
    current_points = cursor.fetchone()[0] or 0
    
    if current_points >= points:
        cursor.execute("""
            INSERT INTO loyalty_transactions (client_id, points, type, description)
            VALUES (?, ?, 'debit', ?)
        """, (client_id, -points, description))
        
        cursor.execute("""
            UPDATE clients SET loyalty_points = loyalty_points - ? WHERE id = ?
        """, (points, client_id))
        
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False


def get_client_loyalty_info(client_id):
    """Obtenir les infos de fidélité d'un client"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT loyalty_points, referral_code FROM clients WHERE id = ?", (client_id,))
    result = cursor.fetchone()
    
    cursor.execute("""
        SELECT COUNT(*) FROM clients WHERE referred_by = ?
    """, (client_id,))
    referrals = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM jobs WHERE client_id = ? AND status IN ('Validée', 'Fait')
    """, (client_id,))
    completed_jobs = cursor.fetchone()[0]
    
    conn.close()
    
    if result:
        return {
            'points': result[0] or 0,
            'referral_code': result[1],
            'referrals_count': referrals,
            'completed_jobs': completed_jobs
        }
    return None


def generate_referral_code(client_name, client_id):
    """Générer un code de parrainage unique"""
    import re
    clean_name = re.sub(r'[^a-zA-Z]', '', client_name.upper())[:4]
    return f"{clean_name}{client_id:04d}"


def format_currency(amount, currency=None):
    """Formater un montant selon la devise"""
    if currency is None:
        currency = get_app_setting('currency', 'FCFA')
    
    amount_str = f"{int(amount):,}".replace(',', ' ')
    
    if currency == 'FCFA' or currency == 'XOF' or currency == 'XAF':
        return f"{amount_str} FCFA"
    elif currency == 'USD':
        return f"${amount_str}"
    elif currency == 'EUR':
        return f"{amount_str}€"
    else:
        return f"{amount_str} {currency}"


def check_inventory_alerts():
    """Vérifier les alertes de stock bas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, quantity, min_quantity, unit
        FROM inventory
        WHERE quantity <= min_quantity
    """)
    
    low_stock = cursor.fetchall()
    conn.close()
    
    return [{
        'id': item[0],
        'name': item[1],
        'quantity': item[2],
        'min_quantity': item[3],
        'unit': item[4]
    } for item in low_stock]
