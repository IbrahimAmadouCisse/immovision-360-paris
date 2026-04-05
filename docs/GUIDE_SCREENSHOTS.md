# 📸 GUIDE - Prendre les Screenshots PostgreSQL

## Objectif
Prouver le bon fonctionnement du pipeline en capturant des screenshots de la base de données PostgreSQL remplie.

---

## Étape 1 : Charger les données dans PostgreSQL

### 1.1 Vérifier que PostgreSQL est installé et démarré

**Windows** :
```bash
# Vérifier si PostgreSQL est installé
pg_config --version

# Démarrer le service (si nécessaire)
# Aller dans Services Windows et démarrer "PostgreSQL"
```

**Linux/Mac** :
```bash
# Vérifier si PostgreSQL est installé
psql --version

# Démarrer le service
sudo service postgresql start   # Linux
brew services start postgresql  # Mac
```

### 1.2 Créer la base de données

Connectez-vous à PostgreSQL et créez la base de données :

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Dans le shell PostgreSQL :
CREATE DATABASE immovision_db;
\q
```

### 1.3 Configurer le fichier .env

Assurez-vous que votre fichier `.env` contient les bonnes informations :

```env
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
DB_NAME=immovision_db
```

### 1.4 Exécuter le script de chargement

```bash
# Activer l'environnement virtuel
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # Linux/Mac

# Charger les données
python scripts/06_load.py
```

**Résultat attendu** :
```
[06_load] Début de l'injection PostgreSQL...
[06_load] Chargement de data/processed/transformed_elysee.csv...
[06_load] 2625 lignes chargées.
[06_load] [OK] Connexion à PostgreSQL établie (localhost:5432/immovision_db)
[06_load] Injection dans la table 'elysee_listings_silver'...
[06_load] [OK] 2625 lignes injectées dans 'elysee_listings_silver'.
```

---

## Étape 2 : Prendre les Screenshots

### 2.1 Se connecter à PostgreSQL

```bash
psql -U postgres -d immovision_db
```

### 2.2 Screenshot 1 : Liste des tables

**Commande** :
```sql
\dt
```

**À capturer** : Liste des tables montrant `elysee_listings_silver`

**Nom du fichier** : `01_liste_tables.png`

---

### 2.3 Screenshot 2 : Structure de la table

**Commande** :
```sql
\d elysee_listings_silver
```

**À capturer** : Structure complète de la table (17 colonnes)

**Nom du fichier** : `02_structure_table.png`

---

### 2.4 Screenshot 3 : Nombre de lignes

**Commande** :
```sql
SELECT COUNT(*) AS nombre_logements FROM elysee_listings_silver;
```

**À capturer** : Résultat montrant ~2625 lignes

**Nom du fichier** : `03_count_lignes.png`

---

### 2.5 Screenshot 4 : Distribution des valeurs fictives (Standardization_Score)

**Commande** :
```sql
SELECT 
    "Standardization_Score", 
    COUNT(*) as nombre
FROM elysee_listings_silver 
GROUP BY "Standardization_Score"
ORDER BY "Standardization_Score";
```

**À capturer** : Distribution des valeurs {-1, 0, 1}

**Nom du fichier** : `04_distribution_standardization.png`

---

### 2.6 Screenshot 5 : Distribution des valeurs fictives (Neighborhood_Impact)

**Commande** :
```sql
SELECT 
    "Neighborhood_Impact", 
    COUNT(*) as nombre
FROM elysee_listings_silver 
GROUP BY "Neighborhood_Impact"
ORDER BY "Neighborhood_Impact";
```

**À capturer** : Distribution des valeurs {-1, 0, 1}

**Nom du fichier** : `05_distribution_neighborhood.png`

---

### 2.7 Screenshot 6 : Aperçu des données (10 premières lignes)

**Commande** :
```sql
SELECT 
    id, 
    name, 
    price, 
    "Standardization_Score", 
    "Neighborhood_Impact"
FROM elysee_listings_silver 
LIMIT 10;
```

**À capturer** : Échantillon de données avec les colonnes IA

**Nom du fichier** : `06_apercu_donnees.png`

---

### 2.8 Screenshot 7 : Statistiques globales

**Commande** :
```sql
SELECT 
    COUNT(*) as total_logements,
    COUNT(DISTINCT neighbourhood_cleansed) as quartiers,
    ROUND(AVG(review_scores_rating), 2) as note_moyenne,
    COUNT(DISTINCT "Standardization_Score") as valeurs_std_uniques,
    COUNT(DISTINCT "Neighborhood_Impact") as valeurs_neigh_uniques
FROM elysee_listings_silver;
```

**À capturer** : Statistiques récapitulatives

**Nom du fichier** : `07_statistiques_globales.png`

---

## Étape 3 : Organiser les Screenshots

Placez tous les screenshots dans le dossier :
```
docs/screenshots/
├── 01_liste_tables.png
├── 02_structure_table.png
├── 03_count_lignes.png
├── 04_distribution_standardization.png
├── 05_distribution_neighborhood.png
├── 06_apercu_donnees.png
└── 07_statistiques_globales.png
```

---

## Étape 4 : Mettre à jour le README

Les screenshots sont automatiquement référencés dans le README principal.

---

## Outils Recommandés pour les Screenshots

### Windows
- **Outil Capture d'écran** (Win + Shift + S)
- **Snipping Tool**
- **ShareX** (gratuit, open-source)

### Linux
- **Flameshot** (`sudo apt install flameshot`)
- **GNOME Screenshot** (Shift + PrtScn)

### Mac
- **Cmd + Shift + 4** (sélection de zone)
- **Cmd + Shift + 3** (plein écran)

---

## Alternative : Outil GUI PostgreSQL

Si vous préférez une interface graphique :

1. **pgAdmin 4** (officiel, gratuit) : https://www.pgadmin.org/download/
2. **DBeaver** (multi-bases, gratuit) : https://dbeaver.io/
3. **TablePlus** (moderne, payant) : https://tableplus.com/

---

## Checklist Finale

- [ ] PostgreSQL installé et démarré
- [ ] Base de données `immovision_db` créée
- [ ] Script `06_load.py` exécuté avec succès
- [ ] 2625 lignes chargées dans `elysee_listings_silver`
- [ ] 7 screenshots pris et sauvegardés
- [ ] Screenshots placés dans `docs/screenshots/`
- [ ] Commit et push sur GitHub

---

## 🎯 Résultat Attendu

Après avoir suivi ce guide, vous aurez :
- ✅ Une base de données PostgreSQL fonctionnelle
- ✅ 2625 logements chargés avec features IA fictives
- ✅ 7 screenshots prouvant le bon fonctionnement
- ✅ Un livrable complet pour GitHub

**Bon travail ! 🚀**
