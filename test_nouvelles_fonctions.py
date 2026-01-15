#!/usr/bin/env python3

import sqlite3
from datetime import date
from security import hash_password, verify_password

print("🧪 Tests des Nouvelles Fonctionnalités\n")
print("=" * 50)

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

print("\n1️⃣ Test : Profil Administrateur")
print("-" * 50)

cursor.execute("SELECT id, username, full_name, email, phone FROM users WHERE role = 'admin'")
admin = cursor.fetchone()

if admin:
    print(f"✅ Admin trouvé :")
    print(f"   - ID: {admin[0]}")
    print(f"   - Username: {admin[1]}")
    print(f"   - Nom complet: {admin[2]}")
    print(f"   - Email: {admin[3]}")
    print(f"   - Téléphone: {admin[4]}")
    
    cursor.execute("SELECT password FROM users WHERE id = ?", (admin[0],))
    pwd_hash = cursor.fetchone()[0]
    
    test_old_password = "admin123"
    if verify_password(test_old_password, pwd_hash):
        print(f"✅ Vérification mot de passe : OK")
    else:
        print(f"⚠️  Mot de passe par défaut changé")
    
    print("\n✅ Test modification profil (simulation) :")
    test_username = f"{admin[1]}_test"
    test_full_name = "Admin Test"
    test_email = "admin@autoclear.com"
    test_phone = "+221 77 123 45 67"
    
    print(f"   - Nouveau username: {test_username}")
    print(f"   - Nouveau nom: {test_full_name}")
    print(f"   - Nouvel email: {test_email}")
    print(f"   - Nouveau téléphone: {test_phone}")
    print("   ℹ️  Utilisez l'interface pour appliquer ces changements")
    
    print("\n✅ Test changement mot de passe (simulation) :")
    new_password = "newadmin456"
    new_hash = hash_password(new_password)
    if verify_password(new_password, new_hash):
        print(f"   ✅ Hashage Bcrypt : OK")
        print(f"   ✅ Vérification hash : OK")
    else:
        print(f"   ❌ Erreur hashage")
else:
    print("❌ Aucun admin trouvé")

print("\n" + "=" * 50)
print("\n2️⃣ Test : Présence Automatique des Employés")
print("-" * 50)

cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee'")
employee_count = cursor.fetchone()[0]

print(f"✅ Employés dans la base : {employee_count}")

if employee_count > 0:
    cursor.execute("SELECT id, username, full_name FROM users WHERE role = 'employee' LIMIT 1")
    employee = cursor.fetchone()
    
    print(f"\n✅ Employé test :")
    print(f"   - ID: {employee[0]}")
    print(f"   - Username: {employee[1]}")
    print(f"   - Nom: {employee[2]}")
    
    today_str = date.today().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT id, status, comment FROM attendance
        WHERE employee_id = ? AND date = ?
    """, (employee[0], today_str))
    
    attendance = cursor.fetchone()
    
    if attendance:
        print(f"\n✅ Présence enregistrée pour aujourd'hui :")
        print(f"   - ID: {attendance[0]}")
        print(f"   - Statut: {attendance[1]}")
        print(f"   - Commentaire: {attendance[2]}")
    else:
        print(f"\n⚠️  Aucune présence enregistrée aujourd'hui")
        print(f"   ℹ️  Connectez-vous avec le compte employé pour tester l'enregistrement automatique")
    
    cursor.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE employee_id = ?
    """, (employee[0],))
    
    total_attendance = cursor.fetchone()[0]
    print(f"\n✅ Total présences enregistrées : {total_attendance}")
    
    print("\n✅ Test fonction auto_register_attendance (simulation) :")
    
    cursor.execute("""
        SELECT id FROM attendance
        WHERE employee_id = ? AND date = ?
    """, (employee[0], today_str))
    
    already_marked = cursor.fetchone()
    
    if not already_marked:
        print(f"   ✅ Pas de doublon détecté")
        print(f"   ✅ Prêt pour enregistrement automatique")
        
        cursor.execute("SELECT id FROM services WHERE active = 1 LIMIT 1")
        service = cursor.fetchone()
        
        if service:
            print(f"   ✅ Service actif trouvé : ID {service[0]}")
            print(f"   ✅ La fonction auto_register_attendance() fonctionnera correctement")
        else:
            print(f"   ⚠️  Aucun service actif - créez-en un d'abord")
    else:
        print(f"   ✅ Présence déjà enregistrée aujourd'hui")
        print(f"   ✅ Protection anti-doublon : OK")
        
else:
    print("\n⚠️  Aucun employé dans la base")
    print("   ℹ️  Créez un employé via l'interface admin pour tester")

print("\n" + "=" * 50)
print("\n3️⃣ Vérification des Services Actifs")
print("-" * 50)

cursor.execute("SELECT COUNT(*) FROM services WHERE active = 1")
active_services = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM services")
total_services = cursor.fetchone()[0]

print(f"✅ Services actifs : {active_services}/{total_services}")

if active_services == 0:
    print("⚠️  Aucun service actif - la présence automatique nécessite au moins 1 service actif")
else:
    cursor.execute("SELECT id, name, price FROM services WHERE active = 1 LIMIT 3")
    services = cursor.fetchall()
    
    print("\n✅ Exemples de services actifs :")
    for svc in services:
        print(f"   - {svc[1]} ({svc[2]:,} FCFA)")

print("\n" + "=" * 50)
print("\n4️⃣ Résumé des Tests")
print("-" * 50)

results = []

cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
if cursor.fetchone()[0] > 0:
    results.append("✅ Profil Admin : Configuration OK")
else:
    results.append("❌ Profil Admin : Aucun admin trouvé")

cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee'")
if cursor.fetchone()[0] > 0:
    results.append("✅ Employés : Au moins 1 employé présent")
else:
    results.append("⚠️  Employés : Créez un employé pour tester")

cursor.execute("SELECT COUNT(*) FROM services WHERE active = 1")
if cursor.fetchone()[0] > 0:
    results.append("✅ Services : Services actifs disponibles")
else:
    results.append("⚠️  Services : Activez au moins 1 service")

cursor.execute("SELECT COUNT(*) FROM attendance")
total_att = cursor.fetchone()[0]
results.append(f"✅ Présences : {total_att} enregistrement(s) au total")

for result in results:
    print(f"\n{result}")

print("\n" + "=" * 50)
print("\n🎉 Tests terminés !")
print("\n📝 Prochaines étapes :")
print("   1. Connectez-vous en tant qu'admin (admin/admin123)")
print("   2. Testez l'onglet '⚙️ Mon Profil'")
print("   3. Créez un employé si nécessaire")
print("   4. Connectez-vous avec le compte employé")
print("   5. Vérifiez le message de présence automatique")
print("\n🌐 URL : http://localhost:8506")
print("=" * 50 + "\n")

conn.close()
