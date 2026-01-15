import streamlit as st
from database import get_connection
from datetime import date
import base64


def employee_dashboard(user_id):
    st.title(f"👷 Espace Employé – {st.session_state.get('username')}")

    conn = get_connection()
    cursor = conn.cursor()

    st.subheader("📊 Mes performances")

    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE employee_id = ?",
        (user_id,)
    )
    total_jobs = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE employee_id = ? AND status IN ('Validée', 'Fait')",
        (user_id,)
    )
    done_jobs = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(services.price)
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.employee_id = ? AND jobs.status IN ('Validée', 'Fait')
    """, (user_id,))
    ca = cursor.fetchone()[0]
    ca = ca if ca else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📋 Missions totales", total_jobs)
    col2.metric("✅ Missions validées", done_jobs)
    col3.metric("💰 CA généré", f"{ca:,} FCFA")

    st.divider()

    st.subheader("📝 Créer une mission")

    client_name = st.text_input("Nom du client")

    cursor.execute("SELECT id, name FROM services")
    services = cursor.fetchall()

    if not services:
        st.warning("Aucun service disponible. Contactez l'administrateur.")
    else:
        service_dict = {s[1]: s[0] for s in services}
        selected_service = st.selectbox(
            "Service à exécuter",
            list(service_dict.keys())
        )

        mission_date = st.date_input(
            "Date de la mission",
            value=date.today()
        )

        if st.button("Créer ma mission"):
            if not client_name:
                st.warning("⚠️ Le nom du client est obligatoire.")
            else:
                cursor.execute("""
                    INSERT INTO jobs (client_name, service_id, employee_id, date, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    client_name,
                    service_dict[selected_service],
                    user_id,
                    mission_date.strftime("%Y-%m-%d"),
                    "En attente"
                ))
                conn.commit()
                st.success("✅ Mission créée avec succès")
                st.rerun()

    st.divider()
    st.subheader("🗂️ Mon historique")

    cursor.execute("""
        SELECT 
            jobs.id,
            jobs.client_name, 
            services.name, 
            services.price, 
            jobs.date, 
            jobs.status
        FROM jobs
        JOIN services ON jobs.service_id = services.id
        WHERE jobs.employee_id = ?
        ORDER BY jobs.date DESC
    """, (user_id,))

    missions = cursor.fetchall()

    if missions:
        for m in missions:
            job_id = m[0]
            client = m[1]
            service = m[2]
            price = m[3]
            date_mission = m[4]
            job_status = m[5]
            
            status_emoji = {
                "En attente": "⏳",
                "Prévu": "📅",
                "Fait": "✅",
                "À valider": "🔍",
                "Validée": "✅",
                "Refusé": "❌"
            }.get(job_status, "📋")
            
            st.write(
                f"{status_emoji} **{client}** | 🧼 {service} | 💰 {price:,} FCFA | 📅 {date_mission} | {job_status}"
            )
            
            if job_status == "Prévu":
                with st.expander(f"📤 Envoyer les preuves pour {client}"):
                    photo_before = st.file_uploader(
                        "Photo AVANT le nettoyage", 
                        type=["jpg", "jpeg", "png"],
                        key=f"before_{job_id}"
                    )
                    photo_after = st.file_uploader(
                        "Photo APRÈS le nettoyage", 
                        type=["jpg", "jpeg", "png"],
                        key=f"after_{job_id}"
                    )
                    note = st.text_area(
                        "Commentaire (optionnel)",
                        key=f"note_{job_id}"
                    )

                    if st.button("📤 Envoyer les preuves", key=f"submit_{job_id}"):
                        if photo_before and photo_after:
                            before_bytes = base64.b64encode(photo_before.read()).decode()
                            after_bytes = base64.b64encode(photo_after.read()).decode()
                            
                            cursor.execute("""
                                UPDATE jobs 
                                SET photo_before = ?, photo_after = ?, employee_note = ?, status = 'À valider'
                                WHERE id = ?
                            """, (before_bytes, after_bytes, note, job_id))
                            conn.commit()
                            st.success("✅ Preuves envoyées ! En attente de validation admin.")
                            st.rerun()
                        else:
                            st.warning("⚠️ Les 2 photos sont obligatoires.")
            
            elif job_status in ["À valider", "Validée"]:
                st.info("🔒 Preuves déjà envoyées. En attente de validation admin.")

    else:
        st.info("Aucune mission pour le moment")

    st.divider()
    st.subheader("🕘 Enregistrement de présence")

    cursor.execute("SELECT id, name FROM services")
    services = cursor.fetchall()

    if services:
        service_dict = {s[1]: s[0] for s in services}
        service_selected = st.selectbox("Service exécuté", list(service_dict.keys()))

        status = st.radio(
            "Statut du jour",
            ["Présent", "En retard", "Absent"]
        )

        comment = st.text_area("Commentaire (optionnel)")

        if st.button("Enregistrer ma présence"):
            today = date.today().strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT id FROM attendance
                WHERE employee_id = ? AND date = ?
            """, (user_id, today))

            already_exists = cursor.fetchone()

            if already_exists:
                st.warning("⚠️ Vous avez déjà enregistré votre présence aujourd'hui.")
            else:
                cursor.execute("""
                    INSERT INTO attendance (employee_id, service_id, status, date, comment)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_id,
                    service_dict[service_selected],
                    status,
                    today,
                    comment
                ))
                conn.commit()
                st.success("✅ Présence enregistrée avec succès")
                st.rerun()
    
    st.divider()
    st.subheader("📅 Mon historique de présence")

    cursor.execute("""
        SELECT attendance.date, services.name, attendance.status, attendance.comment
        FROM attendance
        JOIN services ON attendance.service_id = services.id
        WHERE attendance.employee_id = ?
        ORDER BY attendance.date DESC
        LIMIT 20
    """, (user_id,))

    records = cursor.fetchall()

    if records:
        for r in records:
            st.write(
                f"📅 {r[0]} | 🧼 {r[1]} | ⏱️ {r[2]} | 📝 {r[3] if r[3] else ''}"
            )
    else:
        st.info("Aucun enregistrement pour le moment")

    conn.close()
