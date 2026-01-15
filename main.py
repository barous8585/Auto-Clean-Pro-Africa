import streamlit as st

from auth import login
from admin_dashboard import admin_dashboard
from employee_dashboard import employee_dashboard

st.set_page_config(
    page_title="Auto Clean Pro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

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

if not st.session_state["authenticated"]:
    login()
else:
    if st.session_state["role"] == "admin":
        admin_dashboard()
    else:
        employee_dashboard(st.session_state["user_id"])
