#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          🚗 AUTO CLEAN PRO V3.0 - DÉMARRAGE                 ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

if [ ! -f "database.db" ]; then
    echo "📊 Initialisation de la base de données..."
    python3 init_db.py
fi

echo "🚀 Lancement de l'application..."
echo ""
echo "📱 L'application sera accessible sur:"
echo "   👉 http://localhost:8506"
echo ""
echo "🔐 Compte admin par défaut:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📌 NOUVEAU DANS LA VERSION 3.0:"
echo "   ✅ Gestion complète des clients"
echo "   ✅ Système de paiements intégré"
echo "   ✅ Dashboard professionnel à 7 onglets"
echo "   ✅ Statistiques avancées en temps réel"
echo "   ✅ Interface employé améliorée"
echo "   ✅ Design moderne et responsive"
echo ""
echo "⚠️  Changez le mot de passe admin après la première connexion!"
echo ""
echo "Pour arrêter l'application, appuyez sur Ctrl+C"
echo "══════════════════════════════════════════════════════════════"
echo ""

python3 -m streamlit run main.py --server.port 8506
