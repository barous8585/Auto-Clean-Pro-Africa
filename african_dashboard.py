"""
Modules additionnels pour dashboard admin - Édition Africaine
"""
import streamlit as st
import pandas as pd
from database import get_connection
from datetime import date, datetime, timedelta
from african_features import *


def manage_inventory(cursor, conn):
    """Gestion de l'inventaire des produits"""
    st.header("📦 Gestion de l'Inventaire")
    
    tab1, tab2, tab3 = st.tabs(["Stock Actuel", "Mouvements", "Alertes"])
    
    with tab1:
        st.subheader("Stock Disponible")
        
        cursor.execute("""
            SELECT id, name, category, quantity, unit, min_quantity, unit_cost, supplier
            FROM inventory
            ORDER BY category, name
        """)
        inventory = cursor.fetchall()
        
        if inventory:
            for item in inventory:
                status = "🟢" if item[3] > item[5] else ("🟠" if item[3] > 0 else "🔴")
                
                with st.expander(f"{status} {item[1]} - {item[3]} {item[4]}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Stock actuel", f"{item[3]} {item[4]}")
                    col2.metric("Stock minimum", f"{item[5]} {item[4]}")
                    col3.metric("Valeur", format_currency(item[3] * item[6]))
                    
                    st.write(f"📁 **Catégorie:** {item[2] if item[2] else 'N/A'}")
                    st.write(f"💰 **Coût unitaire:** {format_currency(item[6])}")
                    st.write(f"🏪 **Fournisseur:** {item[7] if item[7] else 'N/A'}")
                    
                    st.divider()
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("➕ Ajouter Stock", key=f"add_{item[0]}"):
                            st.session_state[f'add_stock_{item[0]}'] = True
                    
                    with col_b:
                        if st.button("➖ Retirer Stock", key=f"remove_{item[0]}"):
                            st.session_state[f'remove_stock_{item[0]}'] = True
                    
                    if st.session_state.get(f'add_stock_{item[0]}'):
                        with st.form(f"add_form_{item[0]}"):
                            qty = st.number_input("Quantité à ajouter", min_value=0.0, step=1.0)
                            notes = st.text_input("Notes (optionnel)")
                            if st.form_submit_button("Confirmer"):
                                cursor.execute("""
                                    INSERT INTO inventory_movements (inventory_id, type, quantity, notes)
                                    VALUES (?, 'entrée', ?, ?)
                                """, (item[0], qty, notes))
                                cursor.execute("""
                                    UPDATE inventory SET quantity = quantity + ? WHERE id = ?
                                """, (qty, item[0]))
                                conn.commit()
                                st.success(f"✅ {qty} {item[4]} ajouté(s)")
                                del st.session_state[f'add_stock_{item[0]}']
                                st.rerun()
                    
                    if st.session_state.get(f'remove_stock_{item[0]}'):
                        with st.form(f"remove_form_{item[0]}"):
                            qty = st.number_input("Quantité à retirer", min_value=0.0, max_value=float(item[3]), step=1.0)
                            notes = st.text_input("Notes (optionnel)")
                            if st.form_submit_button("Confirmer"):
                                cursor.execute("""
                                    INSERT INTO inventory_movements (inventory_id, type, quantity, notes)
                                    VALUES (?, 'sortie', ?, ?)
                                """, (item[0], qty, notes))
                                cursor.execute("""
                                    UPDATE inventory SET quantity = quantity - ? WHERE id = ?
                                """, (qty, item[0]))
                                conn.commit()
                                st.success(f"✅ {qty} {item[4]} retiré(s)")
                                del st.session_state[f'remove_stock_{item[0]}']
                                st.rerun()
        else:
            st.info("Aucun produit en inventaire")
    
    with tab2:
        st.subheader("📊 Historique des Mouvements")
        
        cursor.execute("""
            SELECT im.created_at, i.name, im.type, im.quantity, i.unit, im.notes
            FROM inventory_movements im
            JOIN inventory i ON im.inventory_id = i.id
            ORDER BY im.created_at DESC
            LIMIT 50
        """)
        movements = cursor.fetchall()
        
        if movements:
            for mov in movements:
                icon = "📥" if mov[2] == "entrée" else "📤"
                color = "green" if mov[2] == "entrée" else "red"
                st.markdown(f"{icon} **{mov[1]}** - {mov[2].upper()} - {mov[3]} {mov[4]} - {mov[0][:10]}")
                if mov[5]:
                    st.caption(f"📝 {mov[5]}")
                st.divider()
        else:
            st.info("Aucun mouvement enregistré")
    
    with tab3:
        st.subheader("⚠️ Alertes Stock Bas")
        
        alerts = check_inventory_alerts()
        
        if alerts:
            for alert in alerts:
                st.warning(f"🔴 **{alert['name']}** : {alert['quantity']} {alert['unit']} (min: {alert['min_quantity']} {alert['unit']})")
        else:
            st.success("✅ Tous les stocks sont au niveau optimal")


def manage_loyalty_program(cursor, conn):
    """Gestion du programme de fidélité"""
    st.header("🎁 Programme de Fidélité")
    
    tab1, tab2 = st.tabs(["Clients Fidèles", "Historique Points"])
    
    with tab1:
        st.subheader("👥 Classement Clients")
        
        cursor.execute("""
            SELECT id, name, phone, loyalty_points, referral_code
            FROM clients
            WHERE loyalty_points > 0
            ORDER BY loyalty_points DESC
            LIMIT 20
        """)
        loyal_clients = cursor.fetchall()
        
        if loyal_clients:
            for idx, client in enumerate(loyal_clients, 1):
                medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else "🏅"))
                
                with st.expander(f"{medal} #{idx} - {client[1]} - {client[3]} points"):
                    info = get_client_loyalty_info(client[0])
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💰 Points", info['points'])
                    col2.metric("✅ Services", info['completed_jobs'])
                    col3.metric("👥 Parrainages", info['referrals_count'])
                    
                    st.write(f"📞 **Téléphone:** {client[2] if client[2] else 'N/A'}")
                    st.write(f"🎫 **Code parrainage:** `{client[4]}`")
                    
                    free_service_points = int(get_app_setting('free_service_points', 10000))
                    progress = min(100, int((info['points'] / free_service_points) * 100))
                    st.progress(progress / 100, text=f"Prochain service gratuit : {progress}%")
                    
                    if st.button(f"➕ Ajouter des points", key=f"add_pts_{client[0]}"):
                        st.session_state[f'add_points_{client[0]}'] = True
                    
                    if st.session_state.get(f'add_points_{client[0]}'):
                        with st.form(f"points_form_{client[0]}"):
                            pts = st.number_input("Points à ajouter", min_value=1, step=100)
                            desc = st.text_input("Raison")
                            if st.form_submit_button("Ajouter"):
                                add_loyalty_points(client[0], pts, desc)
                                st.success(f"✅ {pts} points ajoutés")
                                del st.session_state[f'add_points_{client[0]}']
                                st.rerun()
        else:
            st.info("Aucun client avec des points de fidélité")
    
    with tab2:
        st.subheader("📊 Dernières Transactions")
        
        cursor.execute("""
            SELECT lt.created_at, c.name, lt.type, lt.points, lt.description
            FROM loyalty_transactions lt
            JOIN clients c ON lt.client_id = c.id
            ORDER BY lt.created_at DESC
            LIMIT 30
        """)
        transactions = cursor.fetchall()
        
        if transactions:
            for trans in transactions:
                icon = "➕" if trans[2] == "credit" else "➖"
                color = "green" if trans[2] == "credit" else "red"
                st.markdown(f"{icon} **{trans[1]}** - {trans[3]} points - {trans[4]} - {trans[0][:10]}")
                st.divider()
        else:
            st.info("Aucune transaction")


def manage_cash_book(cursor, conn):
    """Livre de caisse simplifié"""
    st.header("💼 Livre de Caisse")
    
    tab1, tab2, tab3 = st.tabs(["Vue d'ensemble", "Ajouter Entrée/Sortie", "Historique"])
    
    with tab1:
        period = st.selectbox("Période", ["Aujourd'hui", "7 jours", "30 jours", "Tout"], key="cash_period")
        
        if period == "Aujourd'hui":
            date_filter = date.today().strftime("%Y-%m-%d")
        elif period == "7 jours":
            date_filter = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        elif period == "30 jours":
            date_filter = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            date_filter = "2000-01-01"
        
        cursor.execute("""
            SELECT SUM(amount) FROM cash_book
            WHERE type = 'entrée' AND date >= ?
        """, (date_filter,))
        total_in = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT SUM(amount) FROM cash_book
            WHERE type = 'sortie' AND date >= ?
        """, (date_filter,))
        total_out = cursor.fetchone()[0] or 0
        
        balance = total_in - total_out
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📥 Entrées", format_currency(total_in))
        col2.metric("📤 Sorties", format_currency(total_out))
        col3.metric("💰 Solde", format_currency(balance), delta=format_currency(balance))
        
        st.divider()
        
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM cash_book
            WHERE type = 'sortie' AND date >= ?
            GROUP BY category
            ORDER BY total DESC
        """, (date_filter,))
        expenses = cursor.fetchall()
        
        if expenses:
            st.subheader("📊 Dépenses par Catégorie")
            for exp in expenses:
                st.write(f"**{exp[0] or 'Non catégorisé'}** : {format_currency(exp[1])}")
    
    with tab2:
        with st.form("new_cash_entry"):
            type_entry = st.selectbox("Type", ["entrée", "sortie"])
            amount = st.number_input("Montant", min_value=0, step=100)
            category = st.selectbox("Catégorie", [
                "Ventes/Services",
                "Achat matériel",
                "Salaires",
                "Loyer",
                "Électricité/Eau",
                "Transport",
                "Taxes",
                "Autre"
            ])
            description = st.text_area("Description")
            entry_date = st.date_input("Date", value=date.today())
            
            submitted = st.form_submit_button("💾 Enregistrer")
            
            if submitted and amount > 0:
                cursor.execute("""
                    INSERT INTO cash_book (date, type, category, amount, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (entry_date.strftime("%Y-%m-%d"), type_entry, category, amount, description))
                conn.commit()
                st.success(f"✅ {type_entry.capitalize()} de {format_currency(amount)} enregistrée")
                st.rerun()
    
    with tab3:
        st.subheader("📋 Dernières Opérations")
        
        cursor.execute("""
            SELECT date, type, category, amount, description
            FROM cash_book
            ORDER BY date DESC, created_at DESC
            LIMIT 30
        """)
        operations = cursor.fetchall()
        
        if operations:
            for op in operations:
                icon = "📥" if op[1] == "entrée" else "📤"
                st.markdown(f"{icon} **{op[0]}** - {op[2]} - {format_currency(op[3])} - {op[4][:50] if op[4] else ''}")
                st.divider()
        else:
            st.info("Aucune opération enregistrée")


def manage_app_settings(cursor, conn):
    """Paramètres de l'application"""
    st.header("⚙️ Paramètres de l'Application")
    
    tab1, tab2, tab3 = st.tabs(["Devise", "Frais de Déplacement", "Fidélité"])
    
    with tab1:
        st.subheader("💱 Configuration Devise")
        
        current_currency = get_app_setting('currency', 'FCFA')
        
        currency = st.selectbox("Devise principale", [
            "FCFA", "XOF", "XAF", "USD", "EUR", "GBP", "NGN", "GHS", "MAD"
        ], index=["FCFA", "XOF", "XAF", "USD", "EUR", "GBP", "NGN", "GHS", "MAD"].index(current_currency) if current_currency in ["FCFA", "XOF", "XAF", "USD", "EUR", "GBP", "NGN", "GHS", "MAD"] else 0)
        
        if st.button("💾 Enregistrer Devise"):
            set_app_setting('currency', currency)
            st.success(f"✅ Devise changée en {currency}")
            st.rerun()
    
    with tab2:
        st.subheader("🚗 Frais de Déplacement")
        
        current_fee = int(get_app_setting('travel_fee_per_km', 200))
        
        fee_per_km = st.number_input("Frais par kilomètre", min_value=0, value=current_fee, step=50)
        
        st.info(f"💡 Exemple : Un déplacement de 10 km coûtera {format_currency(fee_per_km * 10)}")
        
        col1, col2 = st.columns(2)
        with col1:
            company_lat = st.number_input("Latitude entreprise", value=float(get_app_setting('company_latitude', 0)), format="%.6f")
        with col2:
            company_lon = st.number_input("Longitude entreprise", value=float(get_app_setting('company_longitude', 0)), format="%.6f")
        
        if st.button("💾 Enregistrer Frais"):
            set_app_setting('travel_fee_per_km', str(fee_per_km))
            set_app_setting('company_latitude', str(company_lat))
            set_app_setting('company_longitude', str(company_lon))
            st.success("✅ Paramètres de déplacement enregistrés")
            st.rerun()
    
    with tab3:
        st.subheader("🎁 Paramètres Fidélité")
        
        points_per_fcfa = int(get_app_setting('loyalty_points_per_fcfa', 1))
        referral_bonus = int(get_app_setting('referral_bonus_points', 500))
        free_service = int(get_app_setting('free_service_points', 10000))
        
        pts_fcfa = st.number_input("Points gagnés par FCFA dépensé", min_value=1, value=points_per_fcfa)
        ref_bonus = st.number_input("Bonus parrainage (points)", min_value=0, value=referral_bonus, step=100)
        free_svc = st.number_input("Points pour service gratuit", min_value=1000, value=free_service, step=1000)
        
        if st.button("💾 Enregistrer Fidélité"):
            set_app_setting('loyalty_points_per_fcfa', str(pts_fcfa))
            set_app_setting('referral_bonus_points', str(ref_bonus))
            set_app_setting('free_service_points', str(free_svc))
            st.success("✅ Paramètres de fidélité enregistrés")
            st.rerun()
