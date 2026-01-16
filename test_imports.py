#!/usr/bin/env python3
"""Script de test des imports pour diagnostic"""

print("🔍 Test des imports...")

try:
    print("1. Import streamlit...")
    import streamlit
    print("   ✅ streamlit OK")
except Exception as e:
    print(f"   ❌ streamlit: {e}")

try:
    print("2. Import pandas...")
    import pandas
    print("   ✅ pandas OK")
except Exception as e:
    print(f"   ❌ pandas: {e}")

try:
    print("3. Import bcrypt...")
    import bcrypt
    print("   ✅ bcrypt OK")
except Exception as e:
    print(f"   ❌ bcrypt: {e}")

try:
    print("4. Import security...")
    import security
    print("   ✅ security OK")
except Exception as e:
    print(f"   ❌ security: {e}")

try:
    print("5. Import database...")
    import database
    print("   ✅ database OK")
except Exception as e:
    print(f"   ❌ database: {e}")

try:
    print("6. Import african_features...")
    import african_features
    print("   ✅ african_features OK")
except Exception as e:
    print(f"   ❌ african_features: {e}")

try:
    print("7. Import african_dashboard...")
    import african_dashboard
    print("   ✅ african_dashboard OK")
except Exception as e:
    print(f"   ❌ african_dashboard: {e}")

try:
    print("8. Import admin_dashboard...")
    import admin_dashboard
    print("   ✅ admin_dashboard OK")
except Exception as e:
    print(f"   ❌ admin_dashboard: {e}")

try:
    print("9. Import init_db...")
    import init_db
    print("   ✅ init_db OK")
except Exception as e:
    print(f"   ❌ init_db: {e}")

print("\n✅ Tous les imports testés !")
