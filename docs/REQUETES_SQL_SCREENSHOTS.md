# 📸 Requêtes SQL pour Screenshots - Copier/Coller Facile

> **Usage** : Copiez ces requêtes une par une et collez-les dans votre terminal PostgreSQL pour générer les screenshots demandés.

---

## Connexion à PostgreSQL

```bash
psql -U postgres -d immovision_db
```

---

## Screenshot 1 : Liste des tables

```sql
\dt
```

**Fichier** : `01_liste_tables.png`

---

## Screenshot 2 : Structure de la table

```sql
\d elysee_listings_silver
```

**Fichier** : `02_structure_table.png`

---

## Screenshot 3 : Nombre de lignes

```sql
SELECT COUNT(*) AS nombre_logements 
FROM elysee_listings_silver;
```

**Fichier** : `03_count_lignes.png`

---

## Screenshot 4 : Distribution Standardization_Score

```sql
SELECT 
    "Standardization_Score", 
    COUNT(*) as nombre
FROM elysee_listings_silver 
GROUP BY "Standardization_Score"
ORDER BY "Standardization_Score";
```

**Fichier** : `04_distribution_standardization.png`

---

## Screenshot 5 : Distribution Neighborhood_Impact

```sql
SELECT 
    "Neighborhood_Impact", 
    COUNT(*) as nombre
FROM elysee_listings_silver 
GROUP BY "Neighborhood_Impact"
ORDER BY "Neighborhood_Impact";
```

**Fichier** : `05_distribution_neighborhood.png`

---

## Screenshot 6 : Aperçu des données

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

**Fichier** : `06_apercu_donnees.png`

---

## Screenshot 7 : Statistiques globales

```sql
SELECT 
    COUNT(*) as total_logements,
    COUNT(DISTINCT neighbourhood_cleansed) as quartiers,
    ROUND(AVG(review_scores_rating), 2) as note_moyenne,
    COUNT(DISTINCT "Standardization_Score") as valeurs_std_uniques,
    COUNT(DISTINCT "Neighborhood_Impact") as valeurs_neigh_uniques
FROM elysee_listings_silver;
```

**Fichier** : `07_statistiques_globales.png`

---

## Requête BONUS : Vérification des valeurs fictives

```sql
-- Vérifier que les valeurs sont bien {-1, 0, 1}
SELECT 
    'Standardization_Score' as colonne,
    MIN("Standardization_Score") as min,
    MAX("Standardization_Score") as max,
    COUNT(DISTINCT "Standardization_Score") as valeurs_uniques
FROM elysee_listings_silver
UNION ALL
SELECT 
    'Neighborhood_Impact',
    MIN("Neighborhood_Impact"),
    MAX("Neighborhood_Impact"),
    COUNT(DISTINCT "Neighborhood_Impact")
FROM elysee_listings_silver;
```

**Fichier** : `08_verification_valeurs.png` (optionnel)

---

## Sortie de PostgreSQL

```sql
\q
```

---

## 🎯 Checklist Screenshots

- [ ] 01_liste_tables.png
- [ ] 02_structure_table.png
- [ ] 03_count_lignes.png
- [ ] 04_distribution_standardization.png
- [ ] 05_distribution_neighborhood.png
- [ ] 06_apercu_donnees.png
- [ ] 07_statistiques_globales.png

**Tous les screenshots doivent être placés dans** : `docs/screenshots/`
