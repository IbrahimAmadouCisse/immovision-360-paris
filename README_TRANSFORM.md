# README - Transformations (05_transform.py)

## Vue d'ensemble

Le script `05_transform.py` transforme les donnees filtrees (`filtered_elysee.csv`) en un dataset enrichi et nettoye (`transformed_elysee.csv`). Il opere en deux etapes : **nettoyage** puis **enrichissement IA**.

---

## A. Nettoyage et normalisation

### Strategie face aux valeurs manquantes (NaN)

| Colonne | Strategie | Justification |
|---|---|---|
| `price` | **Suppression** (drop) | Feature critique pour l'Hypothese A — une ligne sans prix est inutilisable |
| `review_scores_rating` | **Imputation mediane** | Logements sans avis : on utilise la mediane pour ne pas fausser la distribution |
| `reviews_per_month` | **Imputation logique (0)** | Un logement neuf sans avis a naturellement 0 avis/mois |
| `host_response_rate` | **Conservation du NaN** | L'absence de donnee est un signal en soi (hote inactif ou non mesure) |

### Gestion des outliers

| Operation | Methode | Seuil |
|---|---|---|
| Plafonnement du prix | Percentile 99 (P99) | Les prix au-dessus du P99 sont remplaces par la valeur du P99 |
| Suppression prix <= 0 | Filtre | Les prix nuls ou negatifs sont supprimes |

---

## B. Enrichissement multimodal par IA (Google Gemini)

Le modele utilise est **gemini-1.5-flash** via l'API Google AI Studio (`google-generativeai`).

### Feature 1 — `Standardization_Score` (Image → Texte)

> **Hypothese C** : la standardisation "Airbnb-style"

| Propriete | Valeur |
|---|---|
| **Source** | Image `.jpg` dans `data/raw/images/{id}.jpg` |
| **Modele** | `gemini-1.5-flash` |
| **Methode** | Envoi de l'image + prompt de classification |
| **Categories** | `Appartement industrialise` / `Appartement personnel` / `Autre` |

**Prompt utilise :**
```
Analyse cette image et classifie-la strictement dans l'une de ces categories :
- 'Appartement industrialise' (Deco minimaliste, style catalogue, standardise, froid)
- 'Appartement personnel' (Objets de vie, livres, decoration heteroclite, chaleureux)
- 'Autre' (Si l'image ne montre pas l'interieur d'un logement)
```

### Feature 2 — `Neighborhood_Impact` (Texte → Texte)

> **Hypothese B** : la deshumanisation de l'accueil

| Propriete | Valeur |
|---|---|
| **Source** | Fichier `.txt` dans `data/raw/texts/{id}.txt` (commentaires agreges) |
| **Modele** | `gemini-1.5-flash` |
| **Methode** | Envoi du texte (tronque a 3000 car.) + prompt de classification |
| **Categories** | `Hotelise` / `Voisinage naturel` |

**Prompt utilise :**
```
Analyse ces commentaires de voyageurs et classifie l'experience decrite :
- 'Hotelise' (boite a cles, consignes professionnelles, peu de contact humain)
- 'Voisinage naturel' (rencontre avec l'hote, conseils de quartier, vie locale)
```

### Mode degrade

Si la cle API Gemini est absente (`GEMINI_API_KEY` non definie dans `.env`), le script fonctionne en mode degrade :
- Les colonnes `Standardization_Score` et `Neighborhood_Impact` sont creees
- Elles sont remplies avec des valeurs aleatoires parmi `{1, -1, 0}` (donnees fictives)
- Le reste du pipeline (nettoyage) fonctionne normalement
- Note : seed aleatoire fixe (42) pour la reproductibilite

---

## Format de sortie

Le fichier `transformed_elysee.csv` combine :

| Groupe | Colonnes |
|---|---|
| Identifiants | `id`, `name` |
| Localisation | `neighbourhood_cleansed`, `latitude`, `longitude` |
| Hypothese A (economique) | `calculated_host_listings_count`, `price`, `property_type`, `room_type`, `availability_365` |
| Hypothese B (sociale) | `host_response_time`, `host_response_rate`, **`Neighborhood_Impact`** (IA) |
| Hypothese C (visuelle) | **`Standardization_Score`** (IA) |
| Evaluation | `number_of_reviews`, `review_scores_rating`, `reviews_per_month` |
