# 📊 README — Analyse Exploratoire des Données (EDA)

## Objectif

Ce document décrit l'analyse exploratoire conduite sur la table `elysee_tabular` (2 626 annonces Airbnb du quartier Élysée) dans le cadre du projet ImmoVision 360.

L'EDA suit une démarche hypothético-déductive en 4 blocs :

| Bloc | Contenu | Livrable |
|------|---------|----------|
| **A** | Feuille de route (questions → variables → graphiques) | Tableau de cadrage |
| **B** | Analyse univariée (chaque variable décrite séparément) | Mini-rapports + graphiques |
| **C** | Croisements entre variables (réponse aux questions) | Graphiques commentés + tests |
| **D** | Analyses complémentaires (ACP, corrélation, clustering) | Visualisations avancées |

---

## Données utilisées

### Source : `DataWarehouse/postgres/elysee_tabular.csv`

| Colonne | Type | Nature | Description |
|---------|------|--------|-------------|
| `id` | BIGINT | Identifiant | ID unique de l'annonce |
| `calculated_host_listings_count` | INT | Quantitative | Nombre d'annonces du même hôte |
| `availability_365` | SMALLINT | Quantitative | Disponibilité annuelle (0-365 jours) |
| `host_response_rate_num` | NUMERIC | Quantitative | Taux de réponse (0-100%) |
| `room_type_code` | SMALLINT | Catégorielle | 0=Shared, 1=Private, 2=Entire, 3=Hotel |
| `host_response_time_code` | SMALLINT | Ordinale | 0=rapide → 3=lent ; -1=non dispo |
| `standardization_score` | SMALLINT | Ordinale | Score IA image : -1, 0, 1 |
| `neighborhood_impact_score` | SMALLINT | Ordinale | Score IA texte : -1, 0, 1 |

### Traitement des valeurs manquantes

- Les `NULL` / `NaN` sont remplacés par **-1** (= « information non disponible »)
- À distinguer des `0` métier (ex : `availability_365 = 0` = logement fermé à la réservation)

---

## Feuille de route (Bloc A)

| # | Question | Variable(s) | Graphique |
|---|----------|-------------|-----------|
| Q1 | Concentration de l'offre ? | `calculated_host_listings_count` | Histogramme + fréquences cumulées |
| Q2 | Multi-propriétaires = plus disponibles ? | `availability_365` × `calculated_host_listings_count` | Scatter plot |
| Q3 | Réactivité « service client » chez les gros hôtes ? | `host_response_time_code` × `calculated_host_listings_count` | Boxplot |
| Q4 | Logements standardisés = plus disponibles ? | `standardization_score` × `availability_365` | Boxplot par score |
| Q5 | Profil « hôtelier » = « catalogue » ? | `standardization_score` × `neighborhood_impact_score` | Tableau croisé + heatmap |

---

## Constats principaux

1. **Distribution très asymétrique** du nombre d'annonces par hôte : majorité de mono-propriétaires, mais quelques acteurs à >100 annonces
2. **Distribution bimodale** de la disponibilité : pic à 0 jours et pic >270 jours
3. **Dominance de logements entiers** (Entire home/apt) dans le quartier
4. **Réactivité rapide** corrélée au nombre d'annonces détenues
5. **Scores IA fictifs** : conclusions illustratives uniquement

---

## Limites

- **Prix absent** de `elysee_tabular` — impossible de tester la corrélation prix/concentration
- **Scores IA aléatoires** — les hypothèses B et C ne sont pas validées
- **Données Airbnb uniquement** — pas de comparaison avec le marché hôtelier classique
- **Corrélation ≠ causalité** — toutes les associations observées sont descriptives

---

## Fichiers associés

| Fichier | Description |
|---------|-------------|
| `EDA.ipynb` | Notebook Jupyter complet (Blocs A, B, C, D) |
| `07_generate_report.py` | Script de génération du rapport PDF |
| `rapport_final_Mairie.pdf` | Rapport PDF pour la Mairie (3-10 pages) |
| `docs/report_charts/` | Graphiques générés pour le rapport |

---

## Exécution

### Notebook EDA

```bash
# Dans VS Code ou Jupyter
jupyter notebook EDA.ipynb
```

### Générer le rapport PDF

```bash
pip install fpdf2 matplotlib seaborn scikit-learn scipy
python 07_generate_report.py
```

Le fichier `rapport_final_Mairie.pdf` sera créé à la racine du projet.
