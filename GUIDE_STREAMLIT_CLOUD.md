# 🚀 Guide de Déploiement sur Streamlit Cloud

## 📋 Qu'est-ce que Streamlit Cloud ?

**Streamlit Cloud** est un service d'hébergement **GRATUIT** pour les applications Streamlit. Il vous permet de déployer votre application en quelques clics directement depuis GitHub.

### ✅ Avantages :
- 🆓 **100% Gratuit** pour les projets publics
- ⚡ **Déploiement automatique** depuis GitHub
- 🔄 **Mises à jour automatiques** à chaque push
- 🌐 **URL publique** accessible depuis n'importe où
- 💾 **Stockage persistant** pour votre base de données

---

## 🎯 Étapes de Déploiement (5 minutes)

### 1️⃣ Préparation (Déjà fait ✅)

Tous les fichiers nécessaires sont déjà prêts :
- ✅ `requirements.txt` - Liste des dépendances
- ✅ `main.py` - Point d'entrée de l'application
- ✅ `.streamlit/config.toml` - Configuration Streamlit
- ✅ Code poussé sur GitHub

---

### 2️⃣ Créer un compte Streamlit Cloud

1. **Allez sur [share.streamlit.io](https://share.streamlit.io)**

2. **Cliquez sur "Sign in with GitHub"**
   ![Sign in](https://docs.streamlit.io/images/streamlit-community-cloud/deploy-empty-state.png)

3. **Autorisez Streamlit à accéder à votre GitHub**
   - Cliquez sur "Authorize streamlit"
   - Entrez votre mot de passe GitHub si demandé

---

### 3️⃣ Déployer votre application

1. **Sur la page d'accueil Streamlit Cloud, cliquez sur "New app"**

2. **Remplissez les informations :**

   ```
   Repository:     barous8585/WashBrain-Etudiant-Nettoyeur
   Branch:         main
   Main file path: main.py
   App URL:        [laissez par défaut ou personnalisez]
   ```

   Exemple de configuration :
   ```
   ┌─────────────────────────────────────────────────┐
   │ Repository                                      │
   │ barous8585/WashBrain-Etudiant-Nettoyeur        │
   ├─────────────────────────────────────────────────┤
   │ Branch                                          │
   │ main                                            │
   ├─────────────────────────────────────────────────┤
   │ Main file path                                  │
   │ main.py                                         │
   ├─────────────────────────────────────────────────┤
   │ App URL (optional)                              │
   │ washbrain-auto-clean                            │
   └─────────────────────────────────────────────────┘
   ```

3. **Cliquez sur "Deploy!"**

4. **Attendez 2-3 minutes**
   - Streamlit installe les dépendances
   - Configure l'environnement
   - Lance votre application

5. **Votre app est en ligne ! 🎉**

   Vous obtiendrez une URL du type :
   ```
   https://washbrain-auto-clean-barous8585.streamlit.app
   ```

---

### 4️⃣ Premier lancement

Lors du premier accès à votre application en ligne :

1. **L'application va se lancer**
2. **La base de données sera créée automatiquement** (grâce à `init_db.py`)
3. **Le compte admin sera créé** (`admin` / `admin123`)

**C'est tout !** Votre application est maintenant accessible depuis n'importe où dans le monde ! 🌍

---

## 🔧 Configuration Avancée (Optionnel)

### Personnaliser l'URL de votre app

Lors du déploiement, vous pouvez personnaliser l'URL :
- Par défaut : `app-name-username.streamlit.app`
- Personnalisé : `auto-clean-pro-barous8585.streamlit.app`

### Secrets (si nécessaire)

Pour ajouter des secrets (API keys, etc.) :

1. Dans Streamlit Cloud, allez dans **Settings** > **Secrets**
2. Ajoutez vos secrets au format TOML :
   ```toml
   # Exemple (pas nécessaire pour cette app)
   api_key = "votre_cle_api"
   ```

---

## 📊 Gestion de votre application

### Accéder au dashboard

Sur [share.streamlit.io](https://share.streamlit.io), vous verrez :
- 📈 **Analytics** : Nombre de visiteurs, temps de chargement
- 🔄 **Logs** : Logs en temps réel de votre application
- ⚙️ **Settings** : Configuration, secrets, variables d'environnement
- 🗑️ **Delete** : Supprimer l'application

### Mettre à jour votre application

**C'est automatique !** 🎉

Chaque fois que vous poussez du code sur GitHub :
1. Streamlit Cloud détecte le changement
2. Redéploie automatiquement votre application
3. Votre app est mise à jour en ~1 minute

Exemple :
```bash
# Vous faites des modifications localement
git add .
git commit -m "Nouvelle fonctionnalité"
git push origin main

# Streamlit Cloud met à jour automatiquement votre app !
```

---

## ⚠️ Points Importants

### 1. Base de données SQLite

**Limitation :** Streamlit Cloud **redémarre** l'application régulièrement (toutes les 48h ou en cas d'inactivité).

**Conséquence :** La base de données SQLite sera **réinitialisée** à chaque redémarrage.

**Solutions :**

#### Option A : Pour tests/démo (OK)
Gardez SQLite, idéal pour :
- Démonstration
- Prototypage
- Tests

#### Option B : Pour production (Recommandé)
Utilisez une base de données externe :
- **Supabase** (PostgreSQL gratuit)
- **PlanetScale** (MySQL gratuit)
- **MongoDB Atlas** (NoSQL gratuit)

Je peux vous aider à migrer vers une de ces solutions si vous le souhaitez !

### 2. Fichiers uploadés (photos)

Les photos uploadées seront **perdues** au redémarrage.

**Solutions :**
- **Cloudinary** (stockage d'images gratuit)
- **AWS S3** (stockage cloud)
- **Supabase Storage** (stockage gratuit)

### 3. Limites du plan gratuit

- ✅ **Apps publiques illimitées**
- ✅ **1 GB de RAM par app**
- ✅ **1 CPU par app**
- ⏱️ **Apps dorment après 7 jours d'inactivité** (se réveillent au premier accès)

---

## 🎬 Résumé : Déploiement en 3 clics

```
1. https://share.streamlit.io → Sign in with GitHub
2. New app → barous8585/WashBrain-Etudiant-Nettoyeur
3. Deploy! → Attendez 2 minutes → C'est en ligne ! 🎉
```

---

## 🆘 Dépannage

### Erreur "Module not found"
- Vérifiez que `requirements.txt` contient toutes les dépendances
- Relancez le déploiement

### L'app ne démarre pas
- Vérifiez les logs dans le dashboard Streamlit Cloud
- Assurez-vous que `main.py` est bien à la racine

### Base de données non créée
- L'application crée automatiquement `database.db` au premier lancement
- Si problème, vérifiez que `init_db.py` s'exécute correctement

---

## 📞 Support

- **Documentation Streamlit Cloud :** [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
- **Forum Streamlit :** [discuss.streamlit.io](https://discuss.streamlit.io)

---

## 🎉 Félicitations !

Vous êtes maintenant prêt à déployer **Auto Clean Pro** sur Streamlit Cloud !

Votre application sera accessible **24/7** depuis n'importe où dans le monde ! 🌍✨
