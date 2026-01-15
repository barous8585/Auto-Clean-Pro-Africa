#!/usr/bin/env python3

import sqlite3
import sys

def test_database():
    """Test de la structure de la base de données"""
    print("🧪 Test de la base de données...")
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        expected_tables = ['users', 'services', 'jobs', 'attendance']
        found_tables = [t[0] for t in tables]
        
        for table in expected_tables:
            if table in found_tables:
                print(f"  ✅ Table '{table}' existe")
            else:
                print(f"  ❌ Table '{table}' manquante")
                return False
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
        admin_count = cursor.fetchone()[0]
        if admin_count > 0:
            print(f"  ✅ Compte admin existe")
        else:
            print(f"  ❌ Pas de compte admin")
            return False
        
        cursor.execute("SELECT COUNT(*) FROM services")
        service_count = cursor.fetchone()[0]
        print(f"  ✅ {service_count} service(s) configuré(s)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur : {e}")
        return False

def test_imports():
    """Test des imports Python"""
    print("\n🧪 Test des imports...")
    
    try:
        import streamlit
        print("  ✅ streamlit")
    except:
        print("  ❌ streamlit manquant")
        return False
    
    try:
        import pandas
        print("  ✅ pandas")
    except:
        print("  ❌ pandas manquant")
        return False
    
    try:
        import bcrypt
        print("  ✅ bcrypt")
    except:
        print("  ❌ bcrypt manquant")
        return False
    
    try:
        import openpyxl
        print("  ✅ openpyxl")
    except:
        print("  ❌ openpyxl manquant")
        return False
    
    return True

def test_security():
    """Test des fonctions de sécurité"""
    print("\n🧪 Test de sécurité...")
    
    try:
        from security import hash_password, verify_password
        
        password = "test123"
        hashed = hash_password(password)
        
        if verify_password(password, hashed):
            print("  ✅ Hashage Bcrypt fonctionne")
        else:
            print("  ❌ Vérification du mot de passe échoue")
            return False
        
        if not verify_password("wrong", hashed):
            print("  ✅ Rejet des mauvais mots de passe")
        else:
            print("  ❌ Accepte les mauvais mots de passe")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur : {e}")
        return False

def test_files():
    """Test de la présence des fichiers essentiels"""
    print("\n🧪 Test des fichiers...")
    
    import os
    
    essential_files = [
        'main.py',
        'auth.py',
        'admin_dashboard.py',
        'employee_dashboard.py',
        'database.py',
        'security.py',
        'init_db.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} manquant")
            return False
    
    return True

def main():
    print("=" * 50)
    print("🚗 AUTO CLEAN PRO - TESTS DE VALIDATION")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_files()
    all_passed &= test_imports()
    all_passed &= test_security()
    all_passed &= test_database()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("🚀 L'application est prête pour le déploiement")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("⚠️  Veuillez corriger les erreurs avant de déployer")
        sys.exit(1)
    print("=" * 50)

if __name__ == "__main__":
    main()
