import os
import csv
import requests
from PIL import Image
from io import BytesIO

# ==========================================
# CONFIGURATION DU PIPELINE D'INGESTION
# ==========================================
# Chemins basés sur l'emplacement du script, pas sur le répertoire de travail courant.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'tabular', 'listings.csv')
IMAGE_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'images')

# Paramètres de réduction (Big Data Management)
TARGET_NEIGHBOURHOOD = 'Élysée'
TARGET_SIZE = (320, 320)

def main():
    # 1. Sécurité : Création du dossier cible s'il a été effacé par erreur
    os.makedirs(IMAGE_DIR, exist_ok=True)
    print(f"🚀 Démarrage de l'ingestion pour le quartier : {TARGET_NEIGHBOURHOOD}")

    # Compteurs pour le monitoring dans le terminal
    stats = {"telechargees": 0, "existantes": 0, "erreurs": 0}

    # 2. Lecture du catalogue CSV
    try:
        with open(CSV_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # 3. Filtre de réduction métier (Quartier)
                neighbourhood = row.get('neighbourhood_cleansed', '')
                if TARGET_NEIGHBOURHOOD not in neighbourhood:
                    continue 
                
                # Extraction des cibles
                app_id = row.get('id')
                picture_url = row.get('picture_url')
                
                if not app_id or not picture_url:
                    continue
                
                # 4. Règle de nommage stricte
                image_filename = f"{app_id}.jpg"
                image_path = os.path.join(IMAGE_DIR, image_filename)
                
                # 5. Le Pilier d'Idempotence
                if os.path.exists(image_path):
                    print(f"⏭️ [SKIP] L'image {image_filename} existe déjà.")
                    stats["existantes"] += 1
                    continue
                
                # 6. Scraping et Gestion des Exceptions (Try/Except)
                try:
                    # Timeout de 10s pour éviter de figer le script sur un serveur lent
                    response = requests.get(picture_url, timeout=10)
                    response.raise_for_status() # Déclenche une erreur si le lien est 404, 500, etc.
                    
                    # Traitement de l'image en RAM (BytesIO) pour ne pas saturer le disque
                    img = Image.open(BytesIO(response.content))
                    
                    # Conversion en RGB (Crucial si l'image source est un PNG transparent)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                        
                    # Redimensionnement (Filtre technique)
                    img_resized = img.resize(TARGET_SIZE)
                    
                    # Sauvegarde finale
                    img_resized.save(image_path, 'JPEG', quality=85)
                    print(f"✅ [SUCCESS] {image_filename} téléchargée et redimensionnée.")
                    stats["telechargees"] += 1
                    
                except requests.exceptions.Timeout:
                    print(f"⚠️ [TIMEOUT] Délai expiré pour l'ID {app_id}")
                    stats["erreurs"] += 1
                except requests.exceptions.HTTPError as e:
                    print(f"❌ [ERREUR HTTP] Lien mort pour l'ID {app_id} : {e}")
                    stats["erreurs"] += 1
                except requests.exceptions.RequestException as e:
                    print(f"❌ [ERREUR RÉSEAU] Impossible de joindre l'hôte pour l'ID {app_id}")
                    stats["erreurs"] += 1
                except Exception as e:
                    print(f"⚠️ [ERREUR IMAGE] Donnée corrompue pour l'ID {app_id} : {e}")
                    stats["erreurs"] += 1

    except FileNotFoundError:
        print(f"🛑 [ERREUR CRITIQUE] Le fichier {CSV_PATH} est introuvable. Vérifiez vos dossiers.")
        return

    # Bilan de fin d'exécution
    print("\n" + "="*40)
    print("📊 BILAN DE L'INGESTION")
    print("="*40)
    print(f"Images téléchargées : {stats['telechargees']}")
    print(f"Images déjà existantes : {stats['existantes']}")
    print(f"Erreurs / Liens morts : {stats['erreurs']}")

if __name__ == "__main__":
    main()