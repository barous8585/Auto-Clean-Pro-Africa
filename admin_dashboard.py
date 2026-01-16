import streamlit as st
import pandas as pd
from io import BytesIO
from database import get_connection
from datetime import date, datetime, timedelta
from security import hash_password
import base64
from african_features import *
from african_dashboard import manage_inventory, manage_loyalty_program, manage_cash_book, manage_app_settings


def admin_dashboard():
    st.title("📊 Dashboard Administrateur - Édition Africaine 🌍")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    check_inventory_alerts_notification(cursor)
    
    tabs = st.tabs([
        "📈 Vue d'ensemble",
        "👥 Clients",
        "👷 Employés",
        "🧼 Services",
        "📋 Missions",
        "💰 Paiements",
        "📊 Rapports",
        "📦 Inventaire",
        "🎁 Fidélité",
        "💼 Caisse",
        "⚙️ Paramètres",
        "👤 Mon Profil"
    ])
    
    with tabs[0]:
        show_overview(cursor)
    
    with tabs[1]:
        manage_clients(cursor, conn)
    
    with tabs[2]:
        manage_employees(cursor, conn)
    
    with tabs[3]:
        manage_services(cursor, conn)
    
    with tabs[4]:
        manage_missions(cursor, conn)
    
    with tabs[5]:
        manage_payments(cursor, conn)
    
    with tabs[6]:
        show_reports(cursor, conn)
    
    with tabs[7]:
        manage_inventory(cursor, conn)
    
    with tabs[8]:
        manage_loyalty_program(cursor, conn)
    
    with tabs[9]:
        manage_cash_book(cursor, conn)
    
    with tabs[10]:
        manage_app_settings(cursor, conn)
    
    with tabs[11]:
        manage_admin_profile(cursor, conn)
    
    conn.close()


def check_inventory_alerts_notification(cursor):
    """Afficher les alertes de stock bas dans la barre latérale"""
    alerts = check_inventory_alerts()
    if alerts:
        with st.sidebar:
            st.warning(f"⚠️ {len(alerts)} produit(s) en rupture de stock")


def show_overview(cursor):
    st.header("📈 Vue d'ensemble")
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    col1, col2, col3, col4 = st.columns(4)
    
    cursor.execute("""
        SELECT SUM(services.price)
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.status IN ('Validée', 'Fait') AND jobs.payment_status = 'Payé'
    """)
    total_ca = cursor.fetchone()[0] or 0
    col1.metric("💰 CA Total", f"{total_ca:,} FCFA")
    
    cursor.execute("""
        SELECT SUM(services.price)
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.status IN ('Validée', 'Fait') 
        AND jobs.payment_status = 'Payé'
        AND jobs.date >= ?
    """, (month_ago.strftime("%Y-%m-%d"),))
    ca_month = cursor.fetchone()[0] or 0
    col2.metric("📅 CA ce mois", f"{ca_month:,} FCFA")
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE date >= ?", (week_ago.strftime("%Y-%m-%d"),))
    missions_week = cursor.fetchone()[0]
    col3.metric("📋 Missions (7j)", missions_week)
    
    cursor.execute("SELECT COUNT(*) FROM clients")
    total_clients = cursor.fetchone()[0]
    col4.metric("👥 Clients", total_clients)
    
    st.divider()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Missions par statut")
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM jobs
            GROUP BY status
        """)
        status_data = cursor.fetchall()
        if status_data:
            df = pd.DataFrame(status_data, columns=['Statut', 'Nombre'])
            st.bar_chart(df.set_index('Statut'))
        else:
            st.info("Aucune donnée disponible")
    
    with col_right:
        st.subheader("💳 État des paiements")
        cursor.execute("""
            SELECT payment_status, COUNT(*) as count
            FROM jobs
            WHERE payment_status IS NOT NULL
            GROUP BY payment_status
        """)
        payment_data = cursor.fetchall()
        if payment_data:
            df = pd.DataFrame(payment_data, columns=['Statut', 'Nombre'])
            st.bar_chart(df.set_index('Statut'))
        else:
            st.info("Aucune donnée disponible")
    
    st.divider()
    st.subheader("🔔 Alertes et Notifications")
    
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE status = 'En attente'
    """)
    pending = cursor.fetchone()[0]
    if pending > 0:
        st.warning(f"⏳ {pending} mission(s) en attente de validation")
    
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE status = 'À valider'
    """)
    to_validate = cursor.fetchone()[0]
    if to_validate > 0:
        st.warning(f"🔍 {to_validate} preuve(s) à valider")
    
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE payment_status = 'En attente'
    """)
    unpaid = cursor.fetchone()[0]
    if unpaid > 0:
        st.error(f"💰 {unpaid} paiement(s) en attente")


def manage_clients(cursor, conn):
    st.header("👥 Gestion des Clients")
    
    tab1, tab2 = st.tabs(["Ajouter Client", "Liste Clients"])
    
    with tab1:
        with st.form("new_client"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nom complet *", key="client_name")
                phone = st.text_input("Téléphone", key="client_phone")
                email = st.text_input("Email", key="client_email")
            with col2:
                vehicle_brand = st.text_input("Marque véhicule", key="client_brand")
                vehicle_model = st.text_input("Modèle véhicule", key="client_model")
                vehicle_plate = st.text_input("Plaque d'immatriculation", key="client_plate")
            
            address = st.text_area("Adresse", key="client_address")
            notes = st.text_area("Notes", key="client_notes")
            
            submitted = st.form_submit_button("➕ Ajouter le client")
            
            if submitted:
                if name:
                    cursor.execute("""
                        INSERT INTO clients (name, phone, email, address, vehicle_brand, vehicle_model, vehicle_plate, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, phone, email, address, vehicle_brand, vehicle_model, vehicle_plate, notes))
                    conn.commit()
                    st.success("✅ Client ajouté avec succès")
                    st.rerun()
                else:
                    st.error("❌ Le nom est obligatoire")
    
    with tab2:
        search = st.text_input("🔍 Rechercher un client", key="search_client")
        
        if search:
            cursor.execute("""
                SELECT * FROM clients 
                WHERE name LIKE ? OR phone LIKE ? OR vehicle_plate LIKE ?
                ORDER BY created_at DESC
            """, (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("SELECT * FROM clients ORDER BY created_at DESC LIMIT 50")
        
        clients = cursor.fetchall()
        
        if clients:
            for client in clients:
                with st.expander(f"👤 {client[1]} - {client[7] if client[7] else 'Pas de plaque'}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"📞 **Téléphone:** {client[2] if client[2] else 'N/A'}")
                        st.write(f"📧 **Email:** {client[3] if client[3] else 'N/A'}")
                        st.write(f"📍 **Adresse:** {client[4] if client[4] else 'N/A'}")
                    with col2:
                        st.write(f"🚗 **Marque:** {client[5] if client[5] else 'N/A'}")
                        st.write(f"🚙 **Modèle:** {client[6] if client[6] else 'N/A'}")
                        st.write(f"🔢 **Plaque:** {client[7] if client[7] else 'N/A'}")
                    
                    if client[8]:
                        st.info(f"📝 {client[8]}")
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM jobs WHERE client_id = ?
                    """, (client[0],))
                    job_count = cursor.fetchone()[0]
                    st.caption(f"📋 {job_count} mission(s) réalisée(s)")
        else:
            st.info("Aucun client trouvé")


def manage_employees(cursor, conn):
    st.header("👷 Gestion des Employés")
    
    tab1, tab2 = st.tabs(["Créer Employé", "Liste Employés"])
    
    with tab1:
        with st.form("new_employee"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Nom d'utilisateur *")
                password = st.text_input("Mot de passe *", type="password")
                full_name = st.text_input("Nom complet *")
            with col2:
                phone = st.text_input("Téléphone")
                email = st.text_input("Email")
            
            submitted = st.form_submit_button("➕ Créer l'employé")
            
            if submitted:
                if username and password and full_name:
                    try:
                        hashed_pw = hash_password(password)
                        cursor.execute("""
                            INSERT INTO users (username, password, role, full_name, phone, email)
                            VALUES (?, ?, 'employee', ?, ?, ?)
                        """, (username, hashed_pw, full_name, phone, email))
                        conn.commit()
                        st.success(f"✅ Employé {full_name} créé avec succès")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
                else:
                    st.error("❌ Tous les champs marqués * sont obligatoires")
    
    with tab2:
        cursor.execute("""
            SELECT id, username, full_name, phone, email, created_at 
            FROM users 
            WHERE role = 'employee'
            ORDER BY created_at DESC
        """)
        employees = cursor.fetchall()
        
        if employees:
            for emp in employees:
                with st.expander(f"👤 {emp[2]} (@{emp[1]})"):
                    col1, col2, col3 = st.columns(3)
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM jobs WHERE employee_id = ?
                    """, (emp[0],))
                    job_count = cursor.fetchone()[0]
                    col1.metric("📋 Missions", job_count)
                    
                    cursor.execute("""
                        SELECT SUM(services.price)
                        FROM jobs
                        JOIN services ON jobs.service_id = services.id
                        WHERE jobs.employee_id = ? AND jobs.status IN ('Validée', 'Fait')
                    """, (emp[0],))
                    ca = cursor.fetchone()[0] or 0
                    col2.metric("💰 CA Généré", f"{ca:,} FCFA")
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM attendance 
                        WHERE employee_id = ? AND status = 'Présent'
                        AND date >= date('now', '-30 days')
                    """, (emp[0],))
                    attendance = cursor.fetchone()[0]
                    col3.metric("✅ Présences (30j)", attendance)
                    
                    st.write(f"📞 {emp[3] if emp[3] else 'N/A'} | 📧 {emp[4] if emp[4] else 'N/A'}")
        else:
            st.info("Aucun employé")


def manage_services(cursor, conn):
    st.header("🧼 Gestion des Services")
    
    tab1, tab2 = st.tabs(["Ajouter Service", "Liste Services"])
    
    with tab1:
        with st.form("new_service"):
            name = st.text_input("Nom du service *")
            description = st.text_area("Description")
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Prix (FCFA) *", min_value=0, step=500)
            with col2:
                duration = st.number_input("Durée (minutes)", min_value=0, step=15)
            
            submitted = st.form_submit_button("➕ Ajouter le service")
            
            if submitted:
                if name and price > 0:
                    cursor.execute("""
                        INSERT INTO services (name, description, price, duration)
                        VALUES (?, ?, ?, ?)
                    """, (name, description, price, duration))
                    conn.commit()
                    st.success("✅ Service ajouté")
                    st.rerun()
                else:
                    st.error("❌ Nom et prix obligatoires")
    
    with tab2:
        cursor.execute("""
            SELECT s.id, s.name, s.description, s.price, s.duration, s.active, 
                   s.created_at, COUNT(j.id) as job_count
            FROM services s
            LEFT JOIN jobs j ON s.id = j.service_id
            GROUP BY s.id, s.name, s.description, s.price, s.duration, s.active, s.created_at
            ORDER BY s.active DESC, s.created_at DESC
        """)
        services = cursor.fetchall()
        
        if services:
            for service in services:
                status_icon = "✅" if service[5] else "❌"
                with st.expander(f"{status_icon} {service[1]} - {service[3]:,} FCFA"):
                    if service[2]:
                        st.write(f"📝 {service[2]}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💰 Prix", f"{service[3]:,} FCFA")
                    col2.metric("⏱️ Durée", f"{service[4] if service[4] else 0} min")
                    col3.metric("📋 Utilisations", service[7])
                    
                    if service[5]:
                        if st.button(f"❌ Désactiver", key=f"deact_{service[0]}"):
                            cursor.execute("UPDATE services SET active = 0 WHERE id = ?", (service[0],))
                            conn.commit()
                            st.rerun()
                    else:
                        if st.button(f"✅ Activer", key=f"act_{service[0]}"):
                            cursor.execute("UPDATE services SET active = 1 WHERE id = ?", (service[0],))
                            conn.commit()
                            st.rerun()
        else:
            st.info("Aucun service")


def manage_missions(cursor, conn):
    st.header("📋 Gestion des Missions")
    
    tab1, tab2, tab3 = st.tabs(["Créer Mission", "Valider Missions", "Valider Preuves"])
    
    with tab1:
        with st.form("new_mission"):
            cursor.execute("SELECT id, name, phone, vehicle_plate FROM clients ORDER BY name")
            clients = cursor.fetchall()
            
            if not clients:
                st.warning("⚠️ Aucun client disponible. Créez d'abord un client dans l'onglet 'Clients'.")
                st.form_submit_button("Créer la mission", disabled=True)
            else:
                client_options = {f"{c[1]} - {c[3] if c[3] else 'Pas de plaque'}": c[0] for c in clients}
                selected_client = st.selectbox("Client", list(client_options.keys()))
                client_id = client_options[selected_client]
                
                cursor.execute("SELECT id, name, price FROM services WHERE active = 1")
                services = cursor.fetchall()
                
                if not services:
                    st.warning("⚠️ Aucun service actif disponible.")
                    st.form_submit_button("Créer la mission", disabled=True)
                else:
                    service_dict = {f"{s[1]} - {s[2]:,} FCFA": s[0] for s in services}
                    selected_service = st.selectbox("Service", list(service_dict.keys()))
                    
                    cursor.execute("SELECT id, username, full_name FROM users WHERE role='employee'")
                    employees = cursor.fetchall()
                    
                    if not employees:
                        st.warning("⚠️ Aucun employé disponible. Créez d'abord un employé.")
                        st.form_submit_button("Créer la mission", disabled=True)
                    else:
                        employee_dict = {f"{e[2]} (@{e[1]})": e[0] for e in employees}
                        selected_employee = st.selectbox("Employé", list(employee_dict.keys()))
                        
                        mission_date = st.date_input("Date", value=date.today())
                        status = st.selectbox("Statut", ["Prévu", "Fait"])
                        
                        submitted = st.form_submit_button("➕ Créer la mission")
                        
                        if submitted:
                            cursor.execute("""
                                INSERT INTO jobs (client_id, service_id, employee_id, date, status)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                client_id,
                                service_dict[selected_service],
                                employee_dict[selected_employee],
                                mission_date.strftime("%Y-%m-%d"),
                                status
                            ))
                            conn.commit()
                            st.success("✅ Mission créée")
                            st.rerun()
    
    with tab2:
        cursor.execute("""
            SELECT j.id, c.name, u.full_name, s.name, j.date
            FROM jobs j
            LEFT JOIN clients c ON j.client_id = c.id
            JOIN users u ON j.employee_id = u.id
            JOIN services s ON j.service_id = s.id
            WHERE j.status = 'En attente'
            ORDER BY j.date
        """)
        pending = cursor.fetchall()
        
        if pending:
            for job in pending:
                st.markdown(f"📋 **{job[1]}** | 👷 {job[2]} | 🧼 {job[3]} | 📅 {job[4]}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Valider", key=f"val_{job[0]}"):
                        cursor.execute("UPDATE jobs SET status = 'Prévu' WHERE id = ?", (job[0],))
                        conn.commit()
                        st.success("✅ Validée")
                        st.rerun()
                with col2:
                    if st.button("❌ Refuser", key=f"ref_{job[0]}"):
                        cursor.execute("UPDATE jobs SET status = 'Refusé' WHERE id = ?", (job[0],))
                        conn.commit()
                        st.warning("❌ Refusée")
                        st.rerun()
                st.divider()
        else:
            st.info("✅ Aucune mission en attente")
    
    with tab3:
        cursor.execute("""
            SELECT j.id, c.name, u.full_name, s.name, j.photo_before, j.photo_after, j.employee_note
            FROM jobs j
            LEFT JOIN clients c ON j.client_id = c.id
            JOIN users u ON j.employee_id = u.id
            JOIN services s ON j.service_id = s.id
            WHERE j.status = 'À valider'
        """)
        to_validate = cursor.fetchall()
        
        if to_validate:
            for job in to_validate:
                st.markdown(f"📋 **{job[1]}** | 👷 {job[2]} | 🧼 {job[3]}")
                
                col1, col2 = st.columns(2)
                if job[4]:
                    with col1:
                        st.image(f"data:image/png;base64,{job[4]}", caption="Avant", width=300)
                if job[5]:
                    with col2:
                        st.image(f"data:image/png;base64,{job[5]}", caption="Après", width=300)
                
                if job[6]:
                    st.info(f"📝 {job[6]}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Valider", key=f"pval_{job[0]}"):
                        cursor.execute("UPDATE jobs SET status = 'Validée' WHERE id = ?", (job[0],))
                        conn.commit()
                        st.success("✅ Validée")
                        st.rerun()
                with col_b:
                    if st.button("❌ Refuser", key=f"pref_{job[0]}"):
                        cursor.execute("UPDATE jobs SET status = 'Prévu' WHERE id = ?", (job[0],))
                        conn.commit()
                        st.warning("❌ Refusée")
                        st.rerun()
                st.divider()
        else:
            st.info("✅ Aucune preuve à valider")


def manage_payments(cursor, conn):
    st.header("💰 Gestion des Paiements")
    
    cursor.execute("""
        SELECT j.id, c.name, s.name, s.price, j.payment_status, j.date, u.full_name
        FROM jobs j
        LEFT JOIN clients c ON j.client_id = c.id
        JOIN services s ON j.service_id = s.id
        JOIN users u ON j.employee_id = u.id
        WHERE j.status IN ('Validée', 'Fait')
        ORDER BY j.payment_status, j.date DESC
    """)
    payments = cursor.fetchall()
    
    if payments:
        for pay in payments:
            status_color = "🔴" if pay[4] == "En attente" else "🟢"
            with st.expander(f"{status_color} {pay[1]} - {pay[2]} - {pay[3]:,} FCFA"):
                col1, col2, col3 = st.columns(3)
                col1.write(f"📅 **Date:** {pay[5]}")
                col2.write(f"👷 **Employé:** {pay[6]}")
                col3.write(f"💰 **Montant:** {pay[3]:,} FCFA")
                
                if pay[4] == "En attente":
                    method = st.selectbox(
                        "Méthode de paiement",
                        ["Espèces", "Mobile Money", "Carte bancaire", "Virement"],
                        key=f"method_{pay[0]}"
                    )
                    if st.button("✅ Marquer comme payé", key=f"paid_{pay[0]}"):
                        cursor.execute("""
                            UPDATE jobs 
                            SET payment_status = 'Payé', payment_method = ?, amount_paid = ?
                            WHERE id = ?
                        """, (method, pay[3], pay[0]))
                        conn.commit()
                        st.success("✅ Paiement enregistré")
                        st.rerun()
                else:
                    st.success(f"✅ Payé via {pay[4]}")
    else:
        st.info("Aucun paiement à gérer")


def show_reports(cursor, conn):
    st.header("📊 Rapports et Statistiques")
    
    period = st.selectbox("Période", ["7 derniers jours", "30 derniers jours", "Cette année", "Tout"])
    
    if period == "7 derniers jours":
        date_filter = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    elif period == "30 derniers jours":
        date_filter = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    elif period == "Cette année":
        date_filter = f"{date.today().year}-01-01"
    else:
        date_filter = "2000-01-01"
    
    cursor.execute("""
        SELECT 
            j.id,
            COALESCE(c.name, j.client_name) as client,
            u.full_name as employee,
            s.name as service,
            s.price,
            j.date,
            j.status,
            j.payment_status
        FROM jobs j
        LEFT JOIN clients c ON j.client_id = c.id
        JOIN users u ON j.employee_id = u.id
        JOIN services s ON j.service_id = s.id
        WHERE j.date >= ?
        ORDER BY j.date DESC
    """, (date_filter,))
    
    rows = cursor.fetchall()
    
    if rows:
        df = pd.DataFrame(rows, columns=[
            "ID", "Client", "Employé", "Service", "Prix", "Date", "Statut", "Paiement"
        ])
        
        st.subheader("📊 Aperçu des données")
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📋 Total missions", len(df))
            ca_total = df['Prix'].sum()
            st.metric("💰 CA Total", f"{ca_total:,} FCFA")
        
        with col2:
            paid = df[df['Paiement'] == 'Payé']['Prix'].sum()
            st.metric("💵 Encaissé", f"{paid:,} FCFA")
            unpaid = ca_total - paid
            st.metric("⏳ À encaisser", f"{unpaid:,} FCFA")
        
        st.divider()
        st.subheader("📤 Export Excel")
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Missions")
        
        st.download_button(
            label="📥 Télécharger le rapport complet",
            data=buffer.getvalue(),
            file_name=f"rapport_auto_clean_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Aucune donnée pour cette période")


def manage_admin_profile(cursor, conn):
    st.header("⚙️ Mon Profil Administrateur")
    
    admin_id = st.session_state.get("user_id")
    
    cursor.execute("""
        SELECT username, full_name, email, phone
        FROM users
        WHERE id = ?
    """, (admin_id,))
    admin_data = cursor.fetchone()
    
    if admin_data:
        st.subheader("📝 Modifier mes informations")
        
        with st.form("update_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Nom d'utilisateur", value=admin_data[0])
                new_full_name = st.text_input("Nom complet", value=admin_data[1] if admin_data[1] else "")
            
            with col2:
                new_email = st.text_input("Email", value=admin_data[2] if admin_data[2] else "")
                new_phone = st.text_input("Téléphone", value=admin_data[3] if admin_data[3] else "")
            
            submitted = st.form_submit_button("💾 Enregistrer les modifications")
            
            if submitted:
                try:
                    cursor.execute("""
                        UPDATE users
                        SET username = ?, full_name = ?, email = ?, phone = ?
                        WHERE id = ?
                    """, (new_username, new_full_name, new_email, new_phone, admin_id))
                    conn.commit()
                    st.session_state["username"] = new_username
                    st.success("✅ Informations mises à jour avec succès")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")
        
        st.divider()
        st.subheader("🔒 Changer mon mot de passe")
        
        with st.form("change_password"):
            old_password = st.text_input("Mot de passe actuel", type="password")
            new_password = st.text_input("Nouveau mot de passe", type="password")
            confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password")
            
            submit_password = st.form_submit_button("🔑 Changer le mot de passe")
            
            if submit_password:
                if not old_password or not new_password or not confirm_password:
                    st.error("❌ Tous les champs sont obligatoires")
                elif len(new_password) < 6:
                    st.error("❌ Le nouveau mot de passe doit contenir au moins 6 caractères")
                elif new_password != confirm_password:
                    st.error("❌ Les mots de passe ne correspondent pas")
                else:
                    cursor.execute("SELECT password FROM users WHERE id = ?", (admin_id,))
                    current_hash = cursor.fetchone()[0]
                    
                    from security import verify_password, hash_password
                    
                    if verify_password(old_password, current_hash):
                        new_hash = hash_password(new_password)
                        cursor.execute("""
                            UPDATE users
                            SET password = ?
                            WHERE id = ?
                        """, (new_hash, admin_id))
                        conn.commit()
                        st.success("✅ Mot de passe changé avec succès")
                    else:
                        st.error("❌ Mot de passe actuel incorrect")
    else:
        st.error("❌ Impossible de charger les informations du profil")
