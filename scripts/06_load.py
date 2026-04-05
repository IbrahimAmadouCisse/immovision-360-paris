"""
06_load.py - Injection PostgreSQL (SQLAlchemy)

Ce script charge les donnees transformees (zone Silver)
dans une base de donnees PostgreSQL via SQLAlchemy.

Idempotence : if_exists='replace' recree la table a chaque execution.

Entree : data/processed/transformed_elysee.csv
Table  : elysee_listings_silver
"""

import os
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# === Configuration ===
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "immovision_db")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
INPUT_FILE = os.path.join(PROCESSED_DIR, "transformed_elysee.csv")

TABLE_NAME = "elysee_listings_silver"


def load():
    """Injecte les donnees transformees dans PostgreSQL."""
    print("[06_load] Debut de l'injection PostgreSQL...")

    # 1. Lecture de la Zone Silver
    print(f"[06_load] Chargement de {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"[06_load] {len(df)} lignes chargees.")

    # 2. Creation du moteur de connexion
    try:
        from sqlalchemy import create_engine

        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)

        # Test de connexion
        with engine.connect() as conn:
            print(f"[06_load] [OK] Connexion a PostgreSQL etablie ({DB_HOST}:{DB_PORT}/{DB_NAME})")

    except ImportError:
        print("[06_load] [ERREUR] sqlalchemy non installe.")
        print("[06_load] Installez-le avec : pip install sqlalchemy psycopg2-binary")
        return
    except Exception as e:
        print(f"[06_load] [ERREUR] Impossible de se connecter a PostgreSQL : {e}")
        print("[06_load] Verifiez vos identifiants dans le fichier .env")
        return

    # 3. Injection (Load) - idempotent via if_exists='replace'
    print(f"[06_load] Injection dans la table '{TABLE_NAME}'...")
    df.to_sql(
        TABLE_NAME,
        engine,
        if_exists="replace",
        index=False,
    )

    print(f"[06_load] [OK] {len(df)} lignes injectees dans '{TABLE_NAME}'.")
    print(f"[06_load] Colonnes : {list(df.columns)}")
    print("[06_load] Donnees chargees avec succes dans le Data Warehouse.")


if __name__ == "__main__":
    load()
