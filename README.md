# 🚗 Auto Clean Pro

Application professionnelle de gestion de nettoyage automobile esthétique.

## 🎯 Fonctionnalités

### Pour les Administrateurs
- ✅ Création et gestion des employés
- ✅ Création et gestion des services
- ✅ Création et attribution des missions
- ✅ Validation des missions créées par les employés
- ✅ Validation des preuves terrain (photos avant/après)
- ✅ Suivi des présences (Présent/En retard/Absent)
- ✅ Statistiques complètes (CA, missions, performances)
- ✅ Export Excel des données

### Pour les Employés
- ✅ Création de missions
- ✅ Upload de preuves (photos avant/après + commentaire)
- ✅ Enregistrement de présence
- ✅ Suivi des performances personnelles
- ✅ Historique des missions

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Étapes d'installation

1. Cloner ou télécharger le projet

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Initialiser la base de données :
```bash
python init_db.py
```

4. Lancer l'application :
```bash
streamlit run main.py
```

## 🔐 Connexion

### Compte administrateur par défaut
- **Username:** admin
- **Password:** admin123

⚠️ **Important:** Changez le mot de passe admin après la première connexion pour des raisons de sécurité.

## 📊 Workflow

1. **Admin** crée des employés
2. **Admin** crée des services (ou utilise les services par défaut)
3. **Admin** ou **Employé** crée des missions
4. **Admin** valide les missions créées par les employés
5. **Employé** exécute la mission et upload les preuves (photos + commentaire)
6. **Admin** valide les preuves et finalise la mission
7. **Employé** enregistre sa présence quotidienne

## 🛠️ Technologies

- **Frontend:** Streamlit
- **Base de données:** SQLite
- **Sécurité:** Bcrypt
- **Export:** Pandas + OpenPyXL

## 📁 Structure du projet

```
auto-clean-pro/
├── main.py                 # Point d'entrée de l'application
├── auth.py                 # Système d'authentification
├── admin_dashboard.py      # Interface administrateur
├── employee_dashboard.py   # Interface employé
├── database.py             # Connexion à la base de données
├── security.py             # Fonctions de sécurité (hashage)
├── init_db.py              # Script d'initialisation de la BDD
├── requirements.txt        # Dépendances Python
└── database.db            # Base de données SQLite (générée)
```

## 🔄 Statuts des missions

- **En attente:** Mission créée par l'employé, en attente de validation admin
- **Prévu:** Mission validée par l'admin, en attente d'exécution
- **À valider:** Mission exécutée avec preuves envoyées, en attente de validation admin
- **Validée:** Mission complètement validée et verrouillée
- **Refusé:** Mission refusée par l'admin

## 💡 Conseils d'utilisation

1. Créez vos employés dès le premier jour
2. Configurez vos services selon vos tarifs
3. Encouragez les employés à créer leurs missions pour plus d'autonomie
4. Validez régulièrement les missions et preuves
5. Exportez les rapports mensuels pour votre comptabilité

## 📞 Support

Pour toute question ou problème, contactez l'administrateur système.

## 📝 Licence

© 2026 Auto Clean Pro - Tous droits réservés
