import streamlit as st
from database import get_connection
from datetime import date, timedelta
import base64


def auto_register_attendance(cursor, conn, user_id):
    today_str = date.today().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT id FROM attendance
        WHERE employee_id = ? AND date = ?
    """, (user_id, today_str))
    
    already_marked = cursor.fetchone()
    
    if not already_marked:
        cursor.execute("SELECT id FROM services WHERE active = 1 LIMIT 1")
        default_service = cursor.fetchone()
        
        if default_service:
            try:
                cursor.execute("""
                    INSERT INTO attendance (employee_id, service_id, status, date, comment)
                    VALUES (?, ?, 'Présent', ?, 'Présence automatique à la connexion')
                """, (user_id, default_service[0], today_str))
                conn.commit()
                st.success("✅ Présence enregistrée automatiquement pour aujourd'hui")
            except:
                pass


def employee_dashboard(user_id):
    st.title(f"👷 Espace Employé")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT full_name, username FROM users WHERE id = ?", (user_id,))
    user_info = cursor.fetchone()
    employee_name = user_info[0] if user_info[0] else user_info[1]
    
    auto_register_attendance(cursor, conn, user_id)
    
    st.subheader(f"Bonjour, {employee_name} !")
    
    tabs = st.tabs([
        "📊 Mon tableau de bord",
        "📋 Mes missions",
        "🕘 Présences",
        "💰 Mes gains"
    ])
    
    with tabs[0]:
        show_employee_dashboard(cursor, user_id)
    
    with tabs[1]:
        manage_employee_missions(cursor, conn, user_id)
    
    with tabs[2]:
        manage_attendance(cursor, conn, user_id)
    
    with tabs[3]:
        show_earnings(cursor, user_id)
    
    conn.close()


def show_employee_dashboard(cursor, user_id):
    st.header("📈 Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE employee_id = ?", (user_id,))
    total_missions = cursor.fetchone()[0]
    col1.metric("📋 Missions totales", total_missions)
    
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE employee_id = ? AND status IN ('Validée', 'Fait')
    """, (user_id,))
    completed = cursor.fetchone()[0]
    col2.metric("✅ Validées", completed)
    
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE employee_id = ? AND status = 'Prévu'
    """, (user_id,))
    pending = cursor.fetchone()[0]
    col3.metric("⏳ En cours", pending)
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE employee_id = ? AND date >= ?
    """, (user_id, week_ago.strftime("%Y-%m-%d")))
    week_missions = cursor.fetchone()[0]
    col4.metric("📅 Cette semaine", week_missions)
    
    st.divider()
    
    st.subheader("🔔 Alertes")
    
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE employee_id = ? AND status = 'Prévu'
    """, (user_id,))
    to_do = cursor.fetchone()[0]
    if to_do > 0:
        st.warning(f"📋 Vous avez {to_do} mission(s) prévue(s) à réaliser")
    
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE employee_id = ? AND status = 'En attente'
    """, (user_id,))
    waiting = cursor.fetchone()[0]
    if waiting > 0:
        st.info(f"⏳ {waiting} mission(s) en attente de validation admin")
    
    st.divider()
    
    st.subheader("📊 Mes performances ce mois")
    
    month_ago = today - timedelta(days=30)
    
    cursor.execute("""
        SELECT SUM(services.price)
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.employee_id = ? 
        AND jobs.status IN ('Validée', 'Fait')
        AND jobs.date >= ?
    """, (user_id, month_ago.strftime("%Y-%m-%d")))
    monthly_ca = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE employee_id = ? 
        AND status = 'Présent'
        AND date >= ?
    """, (user_id, month_ago.strftime("%Y-%m-%d")))
    attendance_count = cursor.fetchone()[0]
    
    col_a, col_b = st.columns(2)
    col_a.metric("💰 CA généré (30j)", f"{monthly_ca:,} FCFA")
    col_b.metric("✅ Jours présents (30j)", attendance_count)


def manage_employee_missions(cursor, conn, user_id):
    st.header("📋 Mes missions")
    
    tab1, tab2 = st.tabs(["Créer une mission", "Mes missions en cours"])
    
    with tab1:
        with st.form("new_employee_mission"):
            st.info("💡 Créez une mission pour un nouveau client ou sélectionnez un client existant")
            
            cursor.execute("SELECT id, name, phone, vehicle_plate FROM clients ORDER BY name")
            clients = cursor.fetchall()
            
            client_options = ["➕ Nouveau client"] + [f"{c[1]} - {c[3] if c[3] else 'Pas de plaque'}" for c in clients]
            selected_client_opt = st.selectbox("Client", client_options)
            
            if selected_client_opt == "➕ Nouveau client":
                col1, col2 = st.columns(2)
                with col1:
                    new_client_name = st.text_input("Nom du client *")
                    new_client_phone = st.text_input("Téléphone")
                with col2:
                    new_vehicle_brand = st.text_input("Marque véhicule")
                    new_vehicle_plate = st.text_input("Plaque")
                client_id = None
            else:
                client_idx = client_options.index(selected_client_opt) - 1
                client_id = clients[client_idx][0]
                new_client_name = None
            
            cursor.execute("SELECT id, name, price, description FROM services WHERE active = 1")
            services = cursor.fetchall()
            
            if services:
                service_options = {f"{s[1]} - {s[2]:,} FCFA": s[0] for s in services}
                selected_service = st.selectbox("Service à réaliser", list(service_options.keys()))
                
                mission_date = st.date_input("Date prévue", value=date.today())
                
                submitted = st.form_submit_button("➕ Créer la mission")
                
                if submitted:
                    if client_id or new_client_name:
                        if not client_id and new_client_name:
                            cursor.execute("""
                                INSERT INTO clients (name, phone, vehicle_brand, vehicle_plate)
                                VALUES (?, ?, ?, ?)
                            """, (new_client_name, new_client_phone, new_vehicle_brand, new_vehicle_plate))
                            conn.commit()
                            client_id = cursor.lastrowid
                        
                        cursor.execute("""
                            INSERT INTO jobs (client_id, service_id, employee_id, date, status)
                            VALUES (?, ?, ?, ?, 'En attente')
                        """, (client_id, service_options[selected_service], user_id, mission_date.strftime("%Y-%m-%d")))
                        conn.commit()
                        st.success("✅ Mission créée ! En attente de validation par l'admin.")
                        st.rerun()
                    else:
                        st.error("❌ Sélectionnez un client ou créez-en un nouveau")
            else:
                st.warning("⚠️ Aucun service disponible. Contactez l'admin.")
    
    with tab2:
        cursor.execute("""
            SELECT 
                j.id,
                COALESCE(c.name, j.client_name) as client_name,
                c.vehicle_plate,
                s.name as service,
                s.price,
                j.date,
                j.status
            FROM jobs j
            LEFT JOIN clients c ON j.client_id = c.id
            JOIN services s ON j.service_id = s.id
            WHERE j.employee_id = ?
            ORDER BY 
                CASE j.status
                    WHEN 'Prévu' THEN 1
                    WHEN 'En attente' THEN 2
                    WHEN 'À valider' THEN 3
                    WHEN 'Validée' THEN 4
                    ELSE 5
                END,
                j.date DESC
        """, (user_id,))
        
        missions = cursor.fetchall()
        
        if missions:
            for mission in missions:
                job_id = mission[0]
                client = mission[1]
                plate = mission[2]
                service = mission[3]
                price = mission[4]
                job_date = mission[5]
                status = mission[6]
                
                status_icons = {
                    "En attente": "⏳",
                    "Prévu": "📅",
                    "À valider": "🔍",
                    "Validée": "✅",
                    "Fait": "✅",
                    "Refusé": "❌"
                }
                icon = status_icons.get(status, "📋")
                
                plate_info = f" ({plate})" if plate else ""
                with st.expander(f"{icon} {client}{plate_info} - {service} - {job_date}"):
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"💰 **Prix:** {price:,} FCFA")
                    col2.write(f"📅 **Date:** {job_date}")
                    col3.write(f"📊 **Statut:** {status}")
                    
                    if status == "Prévu":
                        st.divider()
                        st.subheader("📤 Envoyer les preuves")
                        
                        photo_before = st.file_uploader(
                            "Photo AVANT",
                            type=["jpg", "jpeg", "png"],
                            key=f"before_{job_id}"
                        )
                        photo_after = st.file_uploader(
                            "Photo APRÈS",
                            type=["jpg", "jpeg", "png"],
                            key=f"after_{job_id}"
                        )
                        note = st.text_area("Commentaire (optionnel)", key=f"note_{job_id}")
                        
                        if st.button("📤 Envoyer", key=f"submit_{job_id}"):
                            if photo_before and photo_after:
                                before_bytes = base64.b64encode(photo_before.read()).decode()
                                after_bytes = base64.b64encode(photo_after.read()).decode()
                                
                                cursor.execute("""
                                    UPDATE jobs 
                                    SET photo_before = ?, photo_after = ?, employee_note = ?, status = 'À valider'
                                    WHERE id = ?
                                """, (before_bytes, after_bytes, note, job_id))
                                conn.commit()
                                st.success("✅ Preuves envoyées !")
                                st.rerun()
                            else:
                                st.error("❌ Les 2 photos sont obligatoires")
                    
                    elif status in ["À valider", "Validée"]:
                        st.success("✅ Preuves envoyées, en attente de validation")
                    
                    elif status == "En attente":
                        st.info("⏳ En attente de validation par l'admin")
                    
                    elif status == "Refusé":
                        st.error("❌ Mission refusée par l'admin")
        else:
            st.info("Aucune mission pour le moment")


def manage_attendance(cursor, conn, user_id):
    st.header("🕘 Gestion des présences")
    
    tab1, tab2 = st.tabs(["Enregistrer présence", "Mon historique"])
    
    with tab1:
        today_str = date.today().strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT id FROM attendance
            WHERE employee_id = ? AND date = ?
        """, (user_id, today_str))
        
        already_marked = cursor.fetchone()
        
        if already_marked:
            st.success("✅ Vous avez déjà enregistré votre présence aujourd'hui")
            
            if st.button("🔄 Modifier ma présence"):
                cursor.execute("""
                    DELETE FROM attendance WHERE employee_id = ? AND date = ?
                """, (user_id, today_str))
                conn.commit()
                st.rerun()
        else:
            with st.form("mark_attendance"):
                cursor.execute("SELECT id, name FROM services WHERE active = 1")
                services = cursor.fetchall()
                
                if services:
                    service_dict = {s[1]: s[0] for s in services}
                    selected_service = st.selectbox("Service du jour", list(service_dict.keys()))
                    
                    status = st.radio("Statut", ["Présent", "En retard", "Absent"])
                    comment = st.text_area("Commentaire (optionnel)")
                    
                    submitted = st.form_submit_button("✅ Enregistrer")
                    
                    if submitted:
                        cursor.execute("""
                            INSERT INTO attendance (employee_id, service_id, status, date, comment)
                            VALUES (?, ?, ?, ?, ?)
                        """, (user_id, service_dict[selected_service], status, today_str, comment))
                        conn.commit()
                        st.success("✅ Présence enregistrée !")
                        st.rerun()
                else:
                    st.warning("⚠️ Aucun service disponible")
    
    with tab2:
        cursor.execute("""
            SELECT a.date, s.name, a.status, a.comment
            FROM attendance a
            JOIN services s ON a.service_id = s.id
            WHERE a.employee_id = ?
            ORDER BY a.date DESC
            LIMIT 30
        """, (user_id,))
        
        records = cursor.fetchall()
        
        if records:
            for rec in records:
                status_icon = "🟢" if rec[2] == "Présent" else ("🟠" if rec[2] == "En retard" else "🔴")
                st.write(f"{status_icon} **{rec[0]}** | {rec[1]} | {rec[2]} {f'| 📝 {rec[3]}' if rec[3] else ''}")
        else:
            st.info("Aucun enregistrement")


def show_earnings(cursor, user_id):
    st.header("💰 Mes gains")
    
    period = st.selectbox("Période", ["7 derniers jours", "30 derniers jours", "Cette année", "Tout"])
    
    if period == "7 derniers jours":
        days = 7
    elif period == "30 derniers jours":
        days = 30
    elif period == "Cette année":
        days = 365
    else:
        days = 10000
    
    date_filter = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT 
            COUNT(*) as missions,
            SUM(CASE WHEN j.status IN ('Validée', 'Fait') THEN s.price ELSE 0 END) as ca_generated
        FROM jobs j
        JOIN services s ON j.service_id = s.id
        WHERE j.employee_id = ?
        AND j.date >= ?
    """, (user_id, date_filter))
    
    result = cursor.fetchone()
    missions_count = result[0]
    ca_generated = result[1] or 0
    
    col1, col2 = st.columns(2)
    col1.metric("📋 Missions réalisées", missions_count)
    col2.metric("💰 CA généré", f"{ca_generated:,} FCFA")
    
    st.divider()
    
    st.subheader("📊 Détail par service")
    
    cursor.execute("""
        SELECT 
            s.name,
            COUNT(*) as count,
            SUM(s.price) as total
        FROM jobs j
        JOIN services s ON j.service_id = s.id
        WHERE j.employee_id = ?
        AND j.date >= ?
        AND j.status IN ('Validée', 'Fait')
        GROUP BY s.name
        ORDER BY total DESC
    """, (user_id, date_filter))
    
    services = cursor.fetchall()
    
    if services:
        for svc in services:
            st.write(f"🧼 **{svc[0]}** : {svc[1]} mission(s) | {svc[2]:,} FCFA")
    else:
        st.info("Aucune donnée pour cette période")
    
    st.divider()
    
    st.subheader("📋 Mes dernières missions validées")
    
    cursor.execute("""
        SELECT 
            COALESCE(c.name, j.client_name) as client,
            s.name as service,
            s.price,
            j.date,
            j.payment_status
        FROM jobs j
        LEFT JOIN clients c ON j.client_id = c.id
        JOIN services s ON j.service_id = s.id
        WHERE j.employee_id = ?
        AND j.status IN ('Validée', 'Fait')
        ORDER BY j.date DESC
        LIMIT 10
    """, (user_id,))
    
    recent = cursor.fetchall()
    
    if recent:
        for job in recent:
            payment_icon = "💵" if job[4] == "Payé" else "⏳"
            st.write(f"{payment_icon} **{job[0]}** | {job[1]} | {job[2]:,} FCFA | {job[3]}")
    else:
        st.info("Aucune mission validée")
