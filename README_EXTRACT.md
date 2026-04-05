# README - Extraction (04_extract.py)

## Strategie de selection des donnees

### Contexte

Le fichier `listings.csv` contient plus de **70 colonnes**. Stocker l'integralite serait une erreur strategique : cela ralentit les calculs, sature la memoire et brouille l'analyse. Ce script selectionne uniquement les colonnes qui servent de carburant aux **3 hypotheses majeures** pour la Maire de Paris.

### Les 3 hypotheses

#### A. Hypothese economique : la concentration des biens

> **Question** : est-ce une economie de partage ou une industrie hoteliere masquee ?

**Indice de preuve** : si 5% des hotes controlent 60% des biens du quartier, on prouve une gestion industrielle.

#### B. Hypothese sociale : la deshumanisation de l'accueil

> **Question** : le lien social se brise-t-il au profit de processus automatises ?

Les agences professionnelles ont souvent des taux de reponse proches de 100% avec des delais tres courts, ce qui tranche avec un hote "resident" plus irregulier. La preuve complete viendra du NLP sur les commentaires en phase Transform.

#### C. Hypothese visuelle : la standardisation "Airbnb-style"

> **Question** : les logements sont-ils devenus des produits financiers steriles ?

Aucune feature CSV n'est pertinente ici : l'analyse se fait via les images en `05_transform.py` (IA Gemini).

---

### Features retenues et mapping hypotheses

| Feature | Type | Hypothese | Justification |
|---|---|---|---|
| `id` | int | Transversal | Cle primaire, jointure avec images/textes |
| `name` | str | Transversal | Nom de l'annonce, tracabilite |
| `neighbourhood_cleansed` | str | GEO | Quartier normalise (filtre Elysee) |
| `latitude` | float | GEO | Coordonnees GPS pour cartographie |
| `longitude` | float | GEO | Coordonnees GPS pour cartographie |
| `calculated_host_listings_count` | int | **A** | Detecteur de multiproprietes (industrialisation) |
| `price` | str→float | **A** | Prix par nuitee (economie de partage vs hotel) |
| `property_type` | str | **A** | Type de bien (appartement, loft, etc.) |
| `room_type` | str | **A** | Type de location (entier, chambre, partage) |
| `availability_365` | int | **A** | Disponibilite annuelle (location permanente ?) |
| `host_response_time` | str | **B** | Delai de reponse (indicateur de professionnalisation) |
| `host_response_rate` | str→float | **B** | Taux de reponse (gestion pro vs humaine) |
| `number_of_reviews` | int | Evaluation | Volume total de commentaires |
| `review_scores_rating` | float | Evaluation | Note globale (sur 5) |
| `reviews_per_month` | float | Evaluation | Frequence des avis (activite du logement) |

### Criteres de filtrage

- **Filtre geographique** : `neighbourhood_cleansed == "Elysee"`
- **Resultat** : ~2625 annonces sur 81 853 au total (3.2% du dataset)

### Nettoyage applique (pre-transform)

| Operation | Colonne | Methode |
|---|---|---|
| Conversion prix | `price` | `"$1,234.56"` → `1234.56` (float) |
| Conversion taux | `host_response_rate` | `"95%"` → `95.0` (float) |
