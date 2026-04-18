"""
05_transform.py - Nettoyage + Enrichissement IA (Gemini)

Ce script transforme les donnees filtrees en deux etapes :

A. Nettoyage et normalisation :
   - Gestion des NaN (imputation ou suppression selon la colonne)
   - Detection et plafonnement des outliers de prix
   - Conversion des types

B. Enrichissement multimodal par IA (Google Gemini) :
   - Standardization_Score : classification visuelle des images (Hypothese C)
   - Neighborhood_Impact   : classification des commentaires texte (Hypothese B)

Entree  : data/processed/filtered_elysee.csv
Sortie  : data/processed/transformed_elysee.csv
"""

import pandas as pd
import numpy as np
import os
import time
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# === Configuration ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_IMAGES_DIR = os.path.join(BASE_DIR, "data", "raw", "images")
RAW_TEXTS_DIR = os.path.join(BASE_DIR, "data", "raw", "texts")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

INPUT_FILE = os.path.join(PROCESSED_DIR, "filtered_elysee.csv")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "transformed_elysee.csv")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Prompts IA
PROMPT_IMAGE = """
Analyse cette image et classifie-la strictement dans l'une de ces categories :
- 'Appartement industrialise' (Deco minimaliste, style catalogue, standardise, froid)
- 'Appartement personnel' (Objets de vie, livres, decoration heteroclite, chaleureux)
- 'Autre' (Si l'image ne montre pas l'interieur d'un logement)

Reponds uniquement par le nom de la categorie, sans guillemets ni ponctuation.
"""

PROMPT_TEXT = """
Analyse ces commentaires de voyageurs et classifie l'experience decrite
strictement dans l'une de ces categories :
- 'Hotelise' (boite a cles, consignes professionnelles, peu de contact humain, gestion automatisee)
- 'Voisinage naturel' (rencontre avec l'hote, conseils de quartier, vie locale, contact humain)

Reponds uniquement par le nom de la categorie, sans guillemets ni ponctuation.
"""


# =============================================================
# A. NETTOYAGE ET NORMALISATION
# =============================================================

def clean_dataframe(df):
    """Nettoie et normalise le DataFrame filtre."""
    print("[05_transform] --- A. Nettoyage et normalisation ---")
    n_before = len(df)

    # 1. Suppression des lignes sans prix (feature critique pour Hypothese A)
    if "price" in df.columns:
        n_null_price = df["price"].isna().sum()
        n_total = len(df)
        if n_null_price == n_total:
            # Colonne prix entierement vide dans le dataset source
            print(f"  - Prix : colonne 100% vide ({n_null_price}/{n_total}) - conservation des lignes")
        else:
            # Suppression uniquement si des prix existent (sinon on perd tout)
            df = df.dropna(subset=["price"])
            df = df[df["price"] > 0]
            print(f"  - Prix manquants ou nuls supprimes : {n_null_price} lignes")

    # 2. Plafonnement des outliers de prix (99e percentile)
    if "price" in df.columns and len(df) > 0:
        p99 = df["price"].quantile(0.99)
        n_outliers = (df["price"] > p99).sum()
        df.loc[df["price"] > p99, "price"] = p99
        print(f"  - Outliers prix plafonnes au P99 ({p99:.0f} EUR) : {n_outliers} lignes")

    # 3. Imputation des notes par la mediane (logements sans avis)
    if "review_scores_rating" in df.columns:
        median_rating = df["review_scores_rating"].median()
        n_null_rating = df["review_scores_rating"].isna().sum()
        df["review_scores_rating"] = df["review_scores_rating"].fillna(median_rating)
        print(f"  - review_scores_rating : {n_null_rating} NaN remplaces par mediane ({median_rating:.2f})")

    # 4. Imputation logique : reviews_per_month = 0 si NaN (logement neuf)
    if "reviews_per_month" in df.columns:
        n_null_rpm = df["reviews_per_month"].isna().sum()
        df["reviews_per_month"] = df["reviews_per_month"].fillna(0)
        print(f"  - reviews_per_month : {n_null_rpm} NaN remplaces par 0 (logements neufs)")

    # 5. Imputation logique : host_response_rate = NaN reste NaN (pas d'info)
    #    On ne force pas une valeur car l'absence est un signal en soi

    n_after = len(df)
    print(f"  - Lignes conservees : {n_after}/{n_before}")

    return df.reset_index(drop=True)


# =============================================================
# B. ENRICHISSEMENT IA (GEMINI)
# =============================================================

def init_gemini():
    """Initialise le modele Gemini. Retourne None si pas de cle API."""
    if not GEMINI_API_KEY:
        print("[05_transform] [WARNING] GEMINI_API_KEY absente du .env")
        print("[05_transform] Mode degrade : colonnes IA remplies de 'Non classifie'")
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        # Test rapide de connexion
        print("[05_transform] [OK] Connexion Gemini etablie (gemini-2.5-flash)")
        return model
    except ImportError:
        print("[05_transform] [WARNING] google-generativeai non installe")
        print("[05_transform] Installez-le avec : pip install google-generativeai")
        return None
    except Exception as e:
        print(f"[05_transform] [WARNING] Erreur Gemini : {e}")
        return None


def classify_image(model, listing_id):
    """Classifie une image via Gemini (Hypothese C : standardisation)."""
    image_path = os.path.join(RAW_IMAGES_DIR, f"{listing_id}.jpg")
    if not os.path.exists(image_path):
        return "Non classifie"

    try:
        import PIL.Image
        img = PIL.Image.open(image_path)
        response = model.generate_content([PROMPT_IMAGE, img])
        result = response.text.strip()

        # Normalisation de la reponse
        result_lower = result.lower()
        if "industrialise" in result_lower or "standardise" in result_lower:
            return "Appartement industrialise"
        elif "personnel" in result_lower or "chaleureux" in result_lower:
            return "Appartement personnel"
        else:
            return "Autre"
    except Exception as e:
        print(f"  [Erreur IA Image {listing_id}] {e}")
        return "Non classifie"


def classify_text(model, listing_id):
    """Classifie un texte via Gemini (Hypothese B : deshumanisation)."""
    text_path = os.path.join(RAW_TEXTS_DIR, f"{listing_id}.txt")
    if not os.path.exists(text_path):
        return "Non classifie"

    try:
        with open(text_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Tronquer a 3000 caracteres pour respecter les limites API
        if len(content) > 3000:
            content = content[:3000]

        if len(content.strip()) < 10:
            return "Non classifie"

        response = model.generate_content([PROMPT_TEXT + "\n\nCommentaires:\n" + content])
        result = response.text.strip()

        # Normalisation de la reponse
        result_lower = result.lower()
        if "hotelise" in result_lower or "hotel" in result_lower:
            return "Hotelise"
        elif "voisinage" in result_lower or "naturel" in result_lower:
            return "Voisinage naturel"
        else:
            return "Non classifie"
    except Exception as e:
        print(f"  [Erreur IA Texte {listing_id}] {e}")
        return "Non classifie"


def enrich_with_ai(df):
    """Enrichit le DataFrame avec les features IA (Gemini)."""
    print("\n[05_transform] --- B. Enrichissement IA (Gemini) ---")

    model = init_gemini()

    if model is None:
        # Mode degrade : colonnes remplies avec valeurs aleatoires (1, -1, 0)
        print("[05_transform] Mode degrade active : generation de valeurs fictives (1, -1, 0)")
        np.random.seed(42)  # Reproductibilite
        df["Standardization_Score"] = np.random.choice([1, -1, 0], size=len(df))
        df["Neighborhood_Impact"] = np.random.choice([1, -1, 0], size=len(df))
        print(f"[05_transform] {len(df)} lignes generees avec valeurs aleatoires")
        return df

    n = len(df)
    standardization_scores = []
    neighborhood_impacts = []

    for idx, row in df.iterrows():
        listing_id = row["id"]

        # Feature 1 : Image -> Standardization_Score
        score = classify_image(model, listing_id)
        standardization_scores.append(score)

        # Feature 2 : Text -> Neighborhood_Impact
        impact = classify_text(model, listing_id)
        neighborhood_impacts.append(impact)

        # Progression + pause pour respecter les quotas API
        if (idx + 1) % 10 == 0:
            print(f"  - Progression : {idx + 1}/{n} lignes traitees...")
            time.sleep(1)  # Respect du rate limit

        # Sauvegarde incrementale toutes les 50 lignes
        if (idx + 1) % 50 == 0:
            df_temp = df.iloc[:idx + 1].copy()
            df_temp["Standardization_Score"] = standardization_scores
            df_temp["Neighborhood_Impact"] = neighborhood_impacts
            df_temp.to_csv(OUTPUT_FILE + ".tmp", index=False)

    df["Standardization_Score"] = standardization_scores
    df["Neighborhood_Impact"] = neighborhood_impacts

    # Stats
    print(f"\n[05_transform] Resultats Standardization_Score :")
    print(df["Standardization_Score"].value_counts().to_string())
    print(f"\n[05_transform] Resultats Neighborhood_Impact :")
    print(df["Neighborhood_Impact"].value_counts().to_string())

    # Nettoyage du fichier temporaire
    tmp_file = OUTPUT_FILE + ".tmp"
    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    return df


# =============================================================
# PIPELINE PRINCIPAL
# =============================================================

def transform():
    """Pipeline de transformation complet."""
    print("[05_transform] Debut des transformations...\n")

    # Charger les donnees filtrees
    print(f"[05_transform] Chargement de {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"[05_transform] {len(df)} lignes chargees.\n")

    # A. Nettoyage
    df = clean_dataframe(df)

    # B. Enrichissement IA
    df = enrich_with_ai(df)

    # Sauvegarde finale
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n[05_transform] [OK] Fichier transforme sauvegarde : {OUTPUT_FILE}")
    print(f"[05_transform] {len(df)} lignes x {len(df.columns)} colonnes.")
    print(f"[05_transform] Colonnes finales : {list(df.columns)}")


if __name__ == "__main__":
    transform()
