#!/usr/bin/env python3
"""
Wrapper pour capturer les erreurs au démarrage
"""
import sys
import traceback

try:
    # Rediriger stderr vers stdout pour voir les erreurs
    sys.stderr = sys.stdout
    
    print("=" * 80)
    print("🔍 DÉMARRAGE DE L'APPLICATION")
    print("=" * 80)
    
    print("\n1️⃣ Import streamlit...")
    import streamlit as st
    print("   ✅ streamlit importé")
    
    print("\n2️⃣ Import os et sys...")
    import os
    print("   ✅ os et sys importés")
    
    print("\n3️⃣ Configuration page...")
    st.set_page_config(
        page_title="Auto Clean Pro",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    print("   ✅ Page configurée")
    
    print("\n4️⃣ Vérification base de données...")
    db_exists = os.path.exists("database.db")
    print(f"   Base de données existe: {db_exists}")
    
    if not db_exists:
        print("\n5️⃣ Création base de données...")
        import init_db
        print("   ✅ Base de données créée")
    else:
        print("\n5️⃣ Migration base de données...")
        import migrate_db
        result = migrate_db.migrate_database()
        print(f"   Migration: {result}")
    
    print("\n6️⃣ Import auth...")
    from auth import login
    print("   ✅ auth importé")
    
    print("\n7️⃣ Import admin_dashboard...")
    from admin_dashboard import admin_dashboard
    print("   ✅ admin_dashboard importé")
    
    print("\n8️⃣ Import employee_dashboard...")
    from employee_dashboard import employee_dashboard
    print("   ✅ employee_dashboard importé")
    
    print("\n" + "=" * 80)
    print("✅ TOUS LES IMPORTS RÉUSSIS - DÉMARRAGE DE L'APP")
    print("=" * 80 + "\n")
    
    # CSS personnalisé
    custom_css = """
    <style>
        .stApp {
            max-width: 100%;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #1E88E5;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 10px 20px;
            background-color: #F0F2F6;
            border-radius: 8px 8px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E88E5;
            color: white;
        }
        div[data-testid="metric-container"] {
            background-color: #F0F2F6;
            border: 1px solid #E0E0E0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stButton>button {
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        div.stAlert {
            border-radius: 8px;
        }
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Initialiser la session
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    # Sidebar
    with st.sidebar:
        st.title("🚗 Auto Clean Pro")
        st.caption("Solution professionnelle de gestion")
        
        if st.session_state.get("authenticated"):
            st.success(f"👤 {st.session_state.get('username')}")
            role_label = "Admin" if st.session_state.get('role') == 'admin' else "Employé"
            st.info(f"🔑 {role_label}")
            
            st.divider()
            
            if st.button("🚪 Déconnexion", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        else:
            st.info("Veuillez vous connecter")
    
    # Routing
    if not st.session_state["authenticated"]:
        login()
    else:
        if st.session_state["role"] == "admin":
            admin_dashboard()
        else:
            employee_dashboard(st.session_state["user_id"])

except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERREUR FATALE AU DÉMARRAGE")
    print("=" * 80)
    print(f"\nType d'erreur: {type(e).__name__}")
    print(f"Message: {str(e)}")
    print("\nTraceback complet:")
    print(traceback.format_exc())
    print("=" * 80 + "\n")
    
    # Essayer d'afficher l'erreur dans Streamlit si possible
    try:
        import streamlit as st
        st.error(f"❌ Erreur fatale: {e}")
        st.code(traceback.format_exc())
    except:
        pass
    
    # Sortir avec code d'erreur
    sys.exit(1)
