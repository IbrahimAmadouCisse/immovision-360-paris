# README - Chargement PostgreSQL (06_load.py)

## Vue d'ensemble

Le script `06_load.py` charge les donnees transformees (`transformed_elysee.csv`) dans une base de donnees PostgreSQL pour la zone Silver du Data Lake.

---

## Configuration requise

### 1. Installation PostgreSQL

Assurez-vous que PostgreSQL est installe et demarre sur votre machine :
- **Windows** : [Telecharger PostgreSQL](https://www.postgresql.org/download/windows/)
- **Linux/Mac** : `sudo apt install postgresql` ou `brew install postgresql`

### 2. Creation de la base de donnees

Connectez-vous a PostgreSQL et creez la base de donnees :

```bash
psql -U postgres
CREATE DATABASE immovision_db;
\q
```

### 3. Configuration du fichier .env

Copiez le fichier `.env.example` en `.env` et remplissez vos identifiants :

```bash
cp .env.example .env
```

Editez `.env` avec vos parametres PostgreSQL :

```env
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
DB_NAME=immovision_db
```

### 4. Installation des dependances Python

```bash
pip install sqlalchemy psycopg2-binary
```

---

## Execution

```bash
python scripts/06_load.py
```

### Comportement

- **Table cible** : `elysee_listings_silver`
- **Mode** : `if_exists='replace'` (la table est recreee a chaque execution)
- **Donnees** : 2,625 lignes x 17 colonnes

### Colonnes chargees

| Groupe | Colonnes |
|--------|----------|
| **Identifiants** | `id`, `name` |
| **Localisation** | `neighbourhood_cleansed`, `latitude`, `longitude` |
| **Hypothese A (economique)** | `calculated_host_listings_count`, `price`, `property_type`, `room_type`, `availability_365` |
| **Hypothese B (sociale)** | `host_response_time`, `host_response_rate`, `Neighborhood_Impact` (valeurs fictives : 1, -1, 0) |
| **Hypothese C (visuelle)** | `Standardization_Score` (valeurs fictives : 1, -1, 0) |
| **Evaluation** | `number_of_reviews`, `review_scores_rating`, `reviews_per_month` |

---

## Verification

Apres l'execution, verifiez que les donnees sont bien chargees :

```sql
-- Connexion a la base
psql -U postgres -d immovision_db

-- Verification du nombre de lignes
SELECT COUNT(*) FROM elysee_listings_silver;

-- Verification des colonnes IA fictives
SELECT 
    Standardization_Score, 
    COUNT(*) 
FROM elysee_listings_silver 
GROUP BY Standardization_Score;

SELECT 
    Neighborhood_Impact, 
    COUNT(*) 
FROM elysee_listings_silver 
GROUP BY Neighborhood_Impact;

-- Apercu des donnees
SELECT id, name, Standardization_Score, Neighborhood_Impact 
FROM elysee_listings_silver 
LIMIT 10;
```

---

## Gestion des erreurs

### Erreur : "could not connect to server"
- Verifiez que PostgreSQL est demarre : `sudo service postgresql start` (Linux) ou verifiez les services Windows
- Verifiez que le port 5432 est bien ouvert

### Erreur : "authentication failed"
- Verifiez vos identifiants dans le fichier `.env`
- Verifiez que l'utilisateur PostgreSQL existe et a les droits necessaires

### Erreur : "database does not exist"
- Creez la base manuellement : `CREATE DATABASE immovision_db;`

---

## Note sur les donnees fictives

⚠️ **Important** : Les colonnes `Standardization_Score` et `Neighborhood_Impact` contiennent actuellement des valeurs aleatoires (1, -1, 0) generees pour les tests.

Ces valeurs seront remplacees par de vraies features generees par IA (Google Gemini) lorsque :
1. Une cle API `GEMINI_API_KEY` sera configuree dans `.env`
2. Le script `05_transform.py` sera re-execute avec l'API active

Les valeurs actuelles permettent de tester l'ensemble du pipeline ETL sans limitation de quota API.
