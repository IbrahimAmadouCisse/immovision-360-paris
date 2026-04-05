# README - Data Lake

## Description du Data Lake

Ce Data Lake suit une architecture **Medallion** à deux zones :

### Zone Bronze (`data/raw/`)
Données brutes, ingérées telles quelles depuis les sources externes. Aucune transformation n'est appliquée.

| Sous-dossier | Contenu | Format |
|---|---|---|
| `tabular/` | Données tabulaires (listings, reviews) | `.csv` |
| `images/` | Images des annonces | `.jpg` (nommées par ID) |
| `texts/` | Textes des descriptions | `.txt` (nommés par ID) |

### Zone Silver (`data/processed/`)
Données filtrées et transformées, prêtes pour l'analyse ou l'injection en base.

| Fichier | Description | Généré par |
|---|---|---|
| `filtered_elysee.csv` | Données filtrées selon les critères métier | `04_extract.py` |
| `transformed_elysee.csv` | Données enrichies par IA (features images + textes) | `05_transform.py` |

## Conventions

- Les fichiers bruts ne sont **jamais modifiés** dans la zone Bronze.
- Les fichiers de la zone Silver sont **régénérés** à chaque exécution du pipeline.
- Les données brutes volumineuses (CSV, images, textes) sont exclues du dépôt Git via `.gitignore`.
