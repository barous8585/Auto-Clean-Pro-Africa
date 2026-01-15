# 🚗 Auto Clean Pro - Solution de Gestion pour Nettoyage de Véhicules

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

Application professionnelle de gestion de nettoyage automobile esthétique.

## ✨ Nouveautés Version 3.1

### ⚙️ Gestion du Profil Administrateur
- Modification username, nom complet, email, téléphone
- Changement de mot de passe sécurisé
- Nouvel onglet "Mon Profil" dans le dashboard admin

### ✅ Présence Automatique des Employés
- Enregistrement automatique à la connexion
- Protection anti-doublon (1 seul enregistrement par jour)
- Message de confirmation visuel

## 🎯 Fonctionnalités

### Pour les Administrateurs
- ✅ Création et gestion des employés
- ✅ Création et gestion des services
- ✅ Création et attribution des missions
- ✅ Gestion clients avec recherche avancée
- ✅ Validation des missions créées par les employés
- ✅ Validation des preuves terrain (photos avant/après)
- ✅ Suivi des présences (Présent/En retard/Absent)
- ✅ Suivi des paiements multi-méthodes
- ✅ Statistiques complètes (CA, missions, performances)
- ✅ Export Excel des données
- ✅ **NOUVEAU** : Gestion du profil admin (modification infos + mot de passe)

### Pour les Employés
- ✅ Création de missions et clients
- ✅ Upload de preuves (photos avant/après + commentaire)
- ✅ **NOUVEAU** : Présence automatique à la connexion
- ✅ Suivi des performances personnelles
- ✅ Historique des missions et gains

## 🚀 Déploiement sur Streamlit Cloud

### Méthode Rapide (Recommandée)

1. **Allez sur [share.streamlit.io](https://share.streamlit.io)**

2. **Connectez-vous avec GitHub**

3. **Créez une nouvelle app** :
   - Repository : `barous8585/WashBrain-Etudiant-Nettoyeur`
   - Branch : `main`
   - Main file path : `main.py`

4. **Cliquez sur "Deploy"** et attendez 2-3 minutes

5. **Votre app est en ligne !** 🎉

### Configuration Automatique

L'application :
- ✅ Installe automatiquement les dépendances (requirements.txt)
- ✅ Crée la base de données au premier lancement
- ✅ Configure le compte admin par défaut

## 💻 Installation Locale

### Prérequis
- Python 3.8+
- pip

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/barous8585/WashBrain-Etudiant-Nettoyeur.git
cd WashBrain-Etudiant-Nettoyeur
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Initialiser la base de données**
```bash
python init_db.py
```

4. **Lancer l'application**
```bash
streamlit run main.py
```

L'application sera accessible sur : http://localhost:8501

## 🔐 Connexion

### Compte administrateur par défaut
- **Username:** admin
- **Password:** admin123

⚠️ **IMPORTANT:** Changez le mot de passe via l'onglet "⚙️ Mon Profil" après la première connexion !

## 📊 Workflow

1. **Admin** crée des employés
2. **Admin** crée des services (ou utilise les services par défaut)
3. **Admin** ou **Employé** crée des clients et missions
4. **Admin** valide les missions créées par les employés
5. **Employé** exécute la mission et upload les preuves (photos + commentaire)
6. **Admin** valide les preuves et finalise la mission
7. **Employé** se connecte → Présence automatiquement enregistrée ✨
8. **Admin** gère les paiements et exporte les rapports

## 🛠️ Technologies

- **Framework:** Streamlit 1.31.0
- **Base de données:** SQLite
- **Sécurité:** Bcrypt (hashage mots de passe)
- **Export:** Pandas + OpenPyXL (Excel)
- **Images:** Pillow + Base64

## 📁 Structure du projet

```
WashBrain-Etudiant-Nettoyeur/
├── main.py                          # Point d'entrée de l'application
├── auth.py                          # Système d'authentification
├── admin_dashboard.py               # Interface administrateur (8 onglets)
├── employee_dashboard.py            # Interface employé (4 onglets)
├── database.py                      # Connexion à la base de données
├── security.py                      # Fonctions de sécurité (hashage Bcrypt)
├── init_db.py                       # Script d'initialisation de la BDD
├── requirements.txt                 # Dépendances Python
├── .streamlit/
│   └── config.toml                  # Configuration Streamlit
├── LISEZMOI.txt                     # Guide complet visuel
├── NOUVELLES_FONCTIONNALITES.md     # Documentation V3.1
├── test_nouvelles_fonctions.py      # Tests automatisés
└── database.db                      # Base de données SQLite (générée)
```

## 🔄 Statuts des missions

- **En attente:** Mission créée par l'employé, en attente de validation admin
- **Prévu:** Mission validée par l'admin, en attente d'exécution
- **À valider:** Mission exécutée avec preuves envoyées, en attente de validation admin
- **Validée:** Mission complètement validée et verrouillée
- **Refusé:** Mission refusée par l'admin

## 🔒 Sécurité

- ✅ Hashage Bcrypt pour tous les mots de passe
- ✅ Protection SQL injection (requêtes paramétrées)
- ✅ Validation des entrées utilisateur
- ✅ Gestion sécurisée des sessions
- ✅ Vérification de l'ancien mot de passe pour changement

## 🧪 Tests

Pour exécuter les tests en local :

```bash
python3 test_nouvelles_fonctions.py
```

## 💡 Conseils d'utilisation

1. Changez le mot de passe admin dès la première connexion
2. Créez vos employés et configurez leurs accès
3. Configurez vos services selon vos tarifs
4. Créez des clients pour faciliter la gestion des missions
5. Validez régulièrement les missions et preuves
6. Suivez les paiements pour éviter les impayés
7. Exportez les rapports mensuels pour votre comptabilité

## 📖 Documentation Complète

- **LISEZMOI.txt** : Guide complet visuel
- **NOUVELLES_FONCTIONNALITES.md** : Documentation V3.1
- **FINALISATION.md** : Récapitulatif technique
- **VERSION_3.0_COMMERCIALE.md** : Fonctionnalités V3.0

## 📞 Support

Pour toute question, consultez la documentation ou créez une issue sur GitHub.

## 🎉 Statut

**Version 3.1 - Production Ready**
- ✅ Fonctionnalités : 100% opérationnelles
- ✅ Tests : Tous validés
- ✅ Sécurité : Bcrypt + validations complètes
- ✅ Documentation : Complète
- ✅ Déploiement : Prêt pour Streamlit Cloud

## 📝 Licence

© 2025-2026 Auto Clean Pro - Tous droits réservés

---

**Développé avec ❤️ pour les professionnels du nettoyage automobile**
