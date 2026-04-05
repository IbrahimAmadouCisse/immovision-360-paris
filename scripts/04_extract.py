"""
04_extract.py - Filtrage & Selection metier (Pandas)

Ce script extrait et filtre les donnees brutes (zone Bronze)
pour produire un CSV filtre dans la zone Silver (data/processed/).

Strategie de selection basee sur 3 hypotheses :
  A. Economique  : concentration des biens (industrie hoteliere masquee ?)
  B. Sociale     : deshumanisation de l'accueil (lien social brise ?)
  C. Visuelle    : standardisation "Airbnb-style" (traitee en 05_transform)

Filtrage geographique : quartier de l'Elysee uniquement.

Entree  : data/raw/tabular/listings.csv
Sortie  : data/processed/filtered_elysee.csv
"""

import pandas as pd
import os
import re

# === Configuration ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "tabular")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

LISTINGS_FILE = os.path.join(RAW_DIR, "listings.csv")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "filtered_elysee.csv")

# Quartier cible
TARGET_NEIGHBOURHOOD = "Élysée"

# ============================================================
# COLS_TO_KEEP : selection strategique des features
# Chaque colonne est rattachee a une hypothese (A, B, C)
# ou a un besoin transversal (ID, GEO, EVAL).
# ============================================================
COLS_TO_KEEP = [
    # --- Identifiants (transversal) ---
    "id",                               # cle primaire
    "name",                             # nom de l'annonce (tracabilite)

    # --- Localisation (transversal / cartographie) ---
    "neighbourhood_cleansed",           # quartier normalise (filtre GEO)
    "latitude",                         # coordonnees GPS
    "longitude",                        # coordonnees GPS

    # --- Hypothese A : concentration economique ---
    "calculated_host_listings_count",   # A - detecteur de multiproprietes
    "price",                            # A - prix par nuitee
    "property_type",                    # A - type de bien (appartement, loft...)
    "room_type",                        # A - type de location (entier, chambre...)
    "availability_365",                 # A - disponibilite annuelle

    # --- Hypothese B : deshumanisation de l'accueil ---
    "host_response_time",               # B - delai de reponse (indicateur pro)
    "host_response_rate",               # B - taux de reponse (indicateur pro)

    # --- Evaluation (transversal / analyse qualite) ---
    "number_of_reviews",                # volume total de commentaires
    "review_scores_rating",             # note globale (sur 5)
    "reviews_per_month",                # frequence des avis
]


def clean_price(price_str):
    """Convertit le prix '$1,234.56' en float 1234.56."""
    if pd.isna(price_str):
        return None
    cleaned = re.sub(r"[^\d.]", "", str(price_str))
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract():
    """Filtre et selectionne les donnees metier depuis le CSV brut."""
    print("[04_extract] Debut du filtrage metier...")

    # Creer le dossier de sortie si necessaire
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 1. Chargement
    print(f"[04_extract] Chargement de {LISTINGS_FILE}...")
    df = pd.read_csv(LISTINGS_FILE, low_memory=False)
    print(f"[04_extract] {len(df)} lignes chargees au total.")

    # 2. Filtrage geographique sur le quartier Elysee
    df_filtered = df[df["neighbourhood_cleansed"] == TARGET_NEIGHBOURHOOD].copy()
    print(f"[04_extract] {len(df_filtered)} annonces dans le quartier Elysee.")

    # 3. Selection des colonnes metier
    available_columns = [col for col in COLS_TO_KEEP if col in df_filtered.columns]
    missing_columns = [col for col in COLS_TO_KEEP if col not in df_filtered.columns]
    if missing_columns:
        print(f"[04_extract] [WARNING] Colonnes absentes du CSV : {missing_columns}")

    df_filtered = df_filtered[available_columns].copy()

    # 4. Nettoyage basique
    # Prix : "$1,234.56" -> 1234.56
    if "price" in df_filtered.columns:
        df_filtered["price"] = df_filtered["price"].apply(clean_price)

    # host_response_rate : "95%" -> 95.0
    if "host_response_rate" in df_filtered.columns:
        df_filtered["host_response_rate"] = (
            df_filtered["host_response_rate"]
            .str.replace("%", "", regex=False)
            .apply(pd.to_numeric, errors="coerce")
        )

    # 5. Sauvegarde
    df_filtered.to_csv(OUTPUT_FILE, index=False)
    print(f"[04_extract] [OK] Fichier filtre sauvegarde : {OUTPUT_FILE}")
    print(f"[04_extract] {len(df_filtered)} lignes x {len(df_filtered.columns)} colonnes.")

    # Apercu rapide
    print("\n[04_extract] Apercu des 3 premieres lignes :")
    print(df_filtered.head(3).to_string(index=False))


if __name__ == "__main__":
    extract()
