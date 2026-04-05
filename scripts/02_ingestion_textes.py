import os
import csv
import json
import re

# ==========================================
# CONFIGURATION DU PIPELINE TEXTUEL
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '..', 'data', 'raw', 'tabular', 'listings.csv')
TEXT_DIR = os.path.join(BASE_DIR, '..', 'data', 'raw', 'texts')

def clean_html_and_spaces(raw_text):
    """Fonction utilitaire pour nettoyer le texte brut."""
    if not raw_text:
        return ""
    # 1. Supprimer les balises HTML (ex: <br/>, <b>)
    clean_text = re.sub(r'<[^>]+>', ' ', raw_text)
    # 2. Remplacer les retours à la ligne et espaces multiples par un seul espace
    clean_text = re.sub(r'\s+', ' ', clean_text)
    # 3. Supprimer les espaces aux extrémités
    return clean_text.strip()

def main():
    # Création du dossier de destination s'il n'existe pas (Sécurité)
    os.makedirs(TEXT_DIR, exist_ok=True)
    print("Début de l'extraction et du nettoyage des textes...")

    # Compteurs pour le suivi
    processed = 0
    skipped = 0

    try:
        with open(CSV_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                app_id = row.get('id')
                if not app_id:
                    continue
                
                # Règle de nommage : Un fichier TXT par ID d'appartement
                text_filename = f"{app_id}.txt"
                text_path = os.path.join(TEXT_DIR, text_filename)
                
                # Le Pilier d'Idempotence
                if os.path.exists(text_path):
                    skipped += 1
                    continue
                
                # Extraction et Nettoyage des colonnes textuelles stratégiques
                # (Adapté aux colonnes classiques d'un dataset type Airbnb)
                document = {
                    "titre": clean_html_and_spaces(row.get('name', '')),
                    "description": clean_html_and_spaces(row.get('description', '')),
                    "quartier_overview": clean_html_and_spaces(row.get('neighborhood_overview', '')),
                    "hote_a_propos": clean_html_and_spaces(row.get('host_about', ''))
                }
                
                # Sauvegarde au format TXT
                text_content = "\n\n".join(
                    section for section in [
                        document["titre"],
                        document["description"],
                        document["quartier_overview"],
                        document["hote_a_propos"]
                    ] if section
                )
                with open(text_path, mode='w', encoding='utf-8') as f:
                    f.write(text_content)
                
                processed += 1

        print(f"\n[TERMINÉ] Bilan de l'ingestion textuelle :")
        print(f"- Nouveaux textes traités et sauvegardés : {processed}")
        print(f"- Textes ignorés (déjà existants) : {skipped}")

    except FileNotFoundError:
        print(f"[ERREUR CRITIQUE] Le fichier {CSV_PATH} est introuvable.")
        print("Avez-vous bien placé votre 'listings.csv' dans 'data/raw/tabular/' ?")
    except Exception as e:
        print(f"[ERREUR] Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    main()