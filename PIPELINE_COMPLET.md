# Pipeline ETL Complet - ImmoVision360 DataLake

## Vue d'ensemble

Ce document decrit le pipeline complet d'extraction, transformation et chargement (ETL) des donnees Airbnb pour le projet ImmoVision360.

---

## Architecture du Data Lake

```
┌─────────────────────────────────────────────────────────────┐
│                     ZONE BRONZE (Raw)                        │
│  data/raw/                                                   │
│  ├── tabular/   (CSV bruts d'Inside Airbnb)                │
│  ├── images/    (Photos des logements)                      │
│  └── texts/     (Commentaires agreges)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ZONE SILVER (Processed)                   │
│  data/processed/                                             │
│  ├── filtered_elysee.csv   (Donnees filtrees)              │
│  └── transformed_elysee.csv (Donnees enrichies)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     ZONE GOLD (Analytics)                    │
│  PostgreSQL Database: immovision_db                          │
│  └── Table: elysee_listings_silver                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Scripts du Pipeline

### 1. Ingestion (BRONZE)

#### `01_ingestion_images.py`
- **Objectif** : Telecharger les photos des logements depuis les URLs Airbnb
- **Entree** : `data/raw/tabular/listings.csv`
- **Sortie** : `data/raw/images/{id}.jpg`
- **Documentation** : Voir `README_DATALAKE.md`

#### `02_ingestion_textes.py`
- **Objectif** : Agreger tous les commentaires par logement
- **Entree** : `data/raw/tabular/reviews.csv`
- **Sortie** : `data/raw/texts/{id}.txt`
- **Documentation** : Voir `README_DATALAKE.md`

#### `03_sanity_check.py`
- **Objectif** : Verifier l'integrite des donnees ingerees
- **Sortie** : Rapport de verification (console)

---

### 2. Extraction (BRONZE → SILVER)

#### `04_extract.py`
- **Objectif** : Filtrer les logements du quartier Elysee
- **Entree** : `data/raw/tabular/listings.csv`
- **Sortie** : `data/processed/filtered_elysee.csv`
- **Filtre** : `neighbourhood_cleansed == 'Élysée'`
- **Colonnes extraites** : 15 colonnes pertinentes pour les 3 hypotheses
- **Documentation** : Voir `README_EXTRACT.md`

---

### 3. Transformation (SILVER)

#### `05_transform.py`
- **Objectif** : Nettoyer et enrichir les donnees avec IA
- **Entree** : `data/processed/filtered_elysee.csv`
- **Sortie** : `data/processed/transformed_elysee.csv`
- **Documentation** : Voir `README_TRANSFORM.md`

**Etape A - Nettoyage** :
- Gestion des valeurs manquantes (NaN)
- Detection et plafonnement des outliers (P99)
- Normalisation des types

**Etape B - Enrichissement IA** :
- **Mode production** (avec `GEMINI_API_KEY`) :
  - `Standardization_Score` : Classification visuelle des images (Hypothese C)
  - `Neighborhood_Impact` : Classification des commentaires (Hypothese B)
  
- **Mode degrade** (sans API) :
  - Generation de valeurs aleatoires `{1, -1, 0}` pour tester le pipeline
  - Seed fixe (42) pour reproductibilite

---

### 4. Chargement (SILVER → GOLD)

#### `06_load.py`
- **Objectif** : Charger les donnees dans PostgreSQL
- **Entree** : `data/processed/transformed_elysee.csv`
- **Sortie** : Table `elysee_listings_silver` dans `immovision_db`
- **Mode** : `if_exists='replace'` (idempotent)
- **Documentation** : Voir `README_LOAD.md`

---

## Execution du Pipeline Complet

### Prerequis

1. **Python 3.8+** avec environnement virtuel
2. **PostgreSQL** installe et demarre
3. **Fichiers sources** dans `data/raw/tabular/`
4. **Fichier .env** configure (copier depuis `.env.example`)

### Installation des dependances

```bash
# Creer l'environnement virtuel
python -m venv myenv

# Activer l'environnement
# Windows:
myenv\Scripts\activate
# Linux/Mac:
source myenv/bin/activate

# Installer les packages
pip install -r requirements.txt
```

### Execution sequentielle

```bash
# Etape 1 : Ingestion des images
python scripts/01_ingestion_images.py

# Etape 2 : Ingestion des textes (commentaires)
python scripts/02_ingestion_textes.py

# Etape 3 : Verification (optionnel)
python scripts/03_sanity_check.py

# Etape 4 : Extraction (filtrage Elysee)
python scripts/04_extract.py

# Etape 5 : Transformation (nettoyage + IA fictive)
python scripts/05_transform.py

# Etape 6 : Chargement PostgreSQL
python scripts/06_load.py
```

---

## Donnees Finales

### Statistiques

- **Zone** : Quartier Elysee (Paris 8e)
- **Lignes** : 2,625 logements
- **Colonnes** : 17 features

### Structure de la table PostgreSQL

```sql
-- Schema de elysee_listings_silver
CREATE TABLE elysee_listings_silver (
    id BIGINT PRIMARY KEY,
    name TEXT,
    neighbourhood_cleansed TEXT,
    latitude FLOAT,
    longitude FLOAT,
    calculated_host_listings_count INT,
    price FLOAT,
    property_type TEXT,
    room_type TEXT,
    availability_365 INT,
    host_response_time TEXT,
    host_response_rate FLOAT,
    number_of_reviews INT,
    review_scores_rating FLOAT,
    reviews_per_month FLOAT,
    Standardization_Score INT,      -- Valeurs fictives: 1, -1, 0
    Neighborhood_Impact INT          -- Valeurs fictives: 1, -1, 0
);
```

---

## Hypotheses de recherche

### Hypothese A - Monopolisation economique
**Colonnes** : `calculated_host_listings_count`, `price`, `property_type`, `room_type`, `availability_365`

### Hypothese B - Deshumanisation de l'accueil
**Colonnes** : `host_response_time`, `host_response_rate`, `Neighborhood_Impact` (IA)

### Hypothese C - Standardisation visuelle
**Colonnes** : `Standardization_Score` (IA)

---

## Mode degrade (valeurs fictives)

⚠️ **Etat actuel** : Les colonnes `Standardization_Score` et `Neighborhood_Impact` contiennent des valeurs aleatoires (1, -1, 0) generees sans utiliser l'API Gemini.

### Pourquoi ?
- Permet de tester l'ensemble du pipeline sans limitation de quota API
- Donnees reproductibles (seed=42)
- Structure identique aux vraies features futures

### Passage en mode production
Pour generer les vraies features IA :
1. Obtenir une cle API Google Gemini : [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Ajouter dans `.env` : `GEMINI_API_KEY=votre_cle`
3. Re-executer : `python scripts/05_transform.py`

---

## Fichiers de documentation

- `README.md` : Presentation generale du projet
- `README_DATALAKE.md` : Architecture du Data Lake et ingestion
- `README_EXTRACT.md` : Etape d'extraction et filtrage
- `README_TRANSFORM.md` : Etape de transformation et enrichissement IA
- `README_LOAD.md` : Etape de chargement PostgreSQL
- `PIPELINE_COMPLET.md` : Ce fichier (vue d'ensemble complete)

---

## Maintenance et evolution

### Mise a jour des donnees source
1. Telecharger les nouveaux fichiers Inside Airbnb
2. Remplacer `listings.csv` et `reviews.csv` dans `data/raw/tabular/`
3. Re-executer le pipeline depuis l'etape 1

### Ajout de nouvelles features
1. Modifier `04_extract.py` pour inclure de nouvelles colonnes
2. Adapter `05_transform.py` si nettoyage specifique necessaire
3. Re-executer depuis l'etape 4

### Changement de quartier
Modifier la ligne 18 de `04_extract.py` :
```python
TARGET_NEIGHBOURHOOD = "Votre_Quartier"
```

---

## Support

Pour toute question ou probleme :
1. Consulter la documentation detaillee dans les README
2. Verifier les logs de sortie de chaque script
3. Verifier la configuration `.env`
4. S'assurer que PostgreSQL est demarre

**Bon pipeline ! 🚀**
