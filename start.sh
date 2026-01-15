#!/bin/bash

echo "🚗 Auto Clean Pro - Démarrage"
echo "================================"

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
echo "   👉 http://localhost:8502"
echo ""
echo "🔐 Compte admin par défaut:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  Changez le mot de passe après la première connexion!"
echo ""
echo "Pour arrêter l'application, appuyez sur Ctrl+C"
echo "================================"
echo ""

python3 -m streamlit run main.py --server.port 8502
