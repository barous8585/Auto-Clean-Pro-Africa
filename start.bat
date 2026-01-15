@echo off
echo 🚗 Auto Clean Pro - Démarrage
echo ================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé
    pause
    exit /b 1
)

if not exist "database.db" (
    echo 📊 Initialisation de la base de données...
    python init_db.py
)

echo 🚀 Lancement de l'application...
echo.
echo 📱 L'application sera accessible sur:
echo    👉 http://localhost:8502
echo.
echo 🔐 Compte admin par défaut:
echo    Username: admin
echo    Password: admin123
echo.
echo ⚠️  Changez le mot de passe après la première connexion!
echo.
echo Pour arrêter l'application, appuyez sur Ctrl+C
echo ================================
echo.

python -m streamlit run main.py --server.port 8502
pause
