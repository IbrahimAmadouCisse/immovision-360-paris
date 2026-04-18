"""
07_generate_report.py — Génération du rapport PDF pour la Mairie de Paris

Ce script génère automatiquement le fichier `rapport_final_Mairie.pdf`
à partir des données de la table `elysee_tabular`.

Il produit :
  1. Les graphiques clés de l'EDA
  2. Le rapport PDF structuré (3-10 pages)

Dépendances : pip install matplotlib seaborn pandas numpy fpdf2 scikit-learn scipy

Entrée  : DataWarehouse/postgres/elysee_tabular.csv
Sortie  : rapport_final_Mairie.pdf
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Mode non-interactif
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# === Configuration ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "DataWarehouse", "postgres", "elysee_tabular.csv")
OUTPUT_PDF = os.path.join(BASE_DIR, "rapport_final_Mairie.pdf")
CHARTS_DIR = os.path.join(BASE_DIR, "docs", "report_charts")

# Style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('Set2')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11


def ensure_dirs():
    """Crée les dossiers nécessaires."""
    os.makedirs(CHARTS_DIR, exist_ok=True)


def load_data():
    """Charge les donnees depuis PostgreSQL (prioritaire) ou CSV (fallback)."""
    print("[rapport] Chargement des donnees...")

    # Tentative PostgreSQL
    try:
        from sqlalchemy import create_engine
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, '.env'))

        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'immovision')

        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        df = pd.read_sql('SELECT * FROM elysee_tabular', engine)
        df = df.fillna(-1)
        print(f"[rapport] [OK] {len(df)} lignes chargees depuis PostgreSQL ({DB_NAME})")
        return df
    except Exception as e:
        print(f"[rapport] [WARN] PostgreSQL non disponible : {e}")
        print("[rapport] [WARN] Fallback vers le CSV...")

    # Fallback CSV
    df = pd.read_csv(CSV_PATH)
    df = df.fillna(-1)
    print(f"[rapport] [OK] {len(df)} lignes chargees depuis CSV.")
    return df


def generate_charts(df):
    """Génère tous les graphiques du rapport."""
    charts = {}
    print("[rapport] Génération des graphiques...")

    # --- Chart 1 : Distribution du nombre d'annonces par hôte ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].hist(df['calculated_host_listings_count'], bins=50,
                 color='#2196F3', edgecolor='white', alpha=0.85)
    axes[0].set_title('Distribution du nombre d\'annonces par hôte', fontsize=12)
    axes[0].set_xlabel('Nombre d\'annonces')
    axes[0].set_ylabel('Fréquence')
    axes[0].axvline(df['calculated_host_listings_count'].median(),
                    color='red', linestyle='--',
                    label=f'Médiane = {df["calculated_host_listings_count"].median():.0f}')
    axes[0].legend()

    # Proportions
    mono = (df['calculated_host_listings_count'] == 1).sum()
    multi = (df['calculated_host_listings_count'] > 1).sum()
    gros = (df['calculated_host_listings_count'] >= 10).sum()
    axes[1].bar(['1 annonce\n(particulier)', '>1 annonce\n(multi)', '≥10 annonces\n(professionnel)'],
                [mono, multi, gros],
                color=['#4CAF50', '#FFC107', '#F44336'], edgecolor='white')
    axes[1].set_title('Profils des hôtes', fontsize=12)
    axes[1].set_ylabel('Nombre d\'hôtes')
    for i, v in enumerate([mono, multi, gros]):
        axes[1].text(i, v + 15, f'{v}\n({v/len(df)*100:.0f}%)', ha='center', fontsize=10)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "01_concentration.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    charts['concentration'] = path

    # --- Chart 2 : Disponibilité annuelle ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df['availability_365'], bins=40, color='#4CAF50', edgecolor='white', alpha=0.85)
    ax.set_title('Distribution de la disponibilité annuelle', fontsize=12)
    ax.set_xlabel('Jours de disponibilité (0-365)')
    ax.set_ylabel('Fréquence')
    ax.axvline(df['availability_365'].mean(), color='red', linestyle='--',
               label=f'Moyenne = {df["availability_365"].mean():.0f} jours')
    ax.legend()

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "02_disponibilite.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    charts['disponibilite'] = path

    # --- Chart 3 : Type de logement ---
    fig, ax = plt.subplots(figsize=(8, 5))
    room_labels = {0: 'Chambre\npartagée', 1: 'Chambre\nprivée',
                   2: 'Logement\nentier', 3: 'Chambre\nd\'hôtel'}
    room_keys = sorted(df['room_type_code'].unique())
    counts = [(df['room_type_code'] == k).sum() for k in room_keys]
    labels = [room_labels.get(k, str(k)) for k in room_keys]
    colors = ['#FF9800', '#03A9F4', '#4CAF50', '#E91E63']
    bars = ax.bar(labels, counts, color=colors[:len(room_keys)], edgecolor='white')
    ax.set_title('Répartition des types de logement', fontsize=12)
    ax.set_ylabel('Nombre d\'annonces')
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                f'{count}\n({count/len(df)*100:.0f}%)', ha='center', fontsize=10)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "03_types_logement.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    charts['types'] = path

    # --- Chart 4 : Scatter disponibilité vs nb annonces ---
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['calculated_host_listings_count'], df['availability_365'],
               alpha=0.3, s=15, color='#2196F3', edgecolors='none')
    ax.set_xlabel('Nombre d\'annonces par hôte')
    ax.set_ylabel('Disponibilité annuelle (jours)')
    ax.set_title('Disponibilité vs Concentration des hôtes', fontsize=12)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "04_scatter_concentration.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    charts['scatter'] = path

    # --- Chart 5 : Boxplot réactivité ---
    df_resp = df[df['host_response_time_code'] != -1].copy()
    if len(df_resp) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        time_labels = {0: 'Dans\nl\'heure', 1: 'Quelques\nheures',
                       2: 'Dans la\njournée', 3: 'Quelques\njours+'}
        bp_data = [df_resp[df_resp['host_response_time_code'] == k]['calculated_host_listings_count']
                   for k in [0, 1, 2, 3]]
        bp = ax.boxplot(bp_data, labels=[time_labels[k] for k in [0, 1, 2, 3]],
                        patch_artist=True)
        colors_bp = ['#4CAF50', '#8BC34A', '#FFC107', '#F44336']
        for patch, color in zip(bp['boxes'], colors_bp):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_title('Nombre d\'annonces par délai de réponse', fontsize=12)
        ax.set_xlabel('Délai de réponse')
        ax.set_ylabel('Nombre d\'annonces par hôte')

        plt.tight_layout()
        path = os.path.join(CHARTS_DIR, "05_boxplot_reactivite.png")
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        charts['reactivite'] = path

    # --- Chart 6 : Heatmap scores croisés ---
    fig, ax = plt.subplots(figsize=(8, 6))
    ct = pd.crosstab(df['standardization_score'], df['neighborhood_impact_score'])
    sns.heatmap(ct, annot=True, fmt='d', cmap='YlOrRd', ax=ax,
                xticklabels=['Indét. (-1)', 'Neutre (0)', 'Hôtélisé (1)'],
                yticklabels=['Indét. (-1)', 'Neutre (0)', 'Standard. (1)'])
    ax.set_title('Croisement : standardisation image × impact voisinage', fontsize=12)
    ax.set_xlabel('Score d\'impact voisinage (texte)')
    ax.set_ylabel('Score de standardisation (image)')

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "06_heatmap_scores.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    charts['heatmap'] = path

    # --- Chart 7 : Matrice de corrélation ---
    fig, ax = plt.subplots(figsize=(9, 7))
    numeric_cols = ['calculated_host_listings_count', 'availability_365',
                    'host_response_rate_num', 'room_type_code',
                    'host_response_time_code', 'standardization_score',
                    'neighborhood_impact_score']
    corr = df[numeric_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, square=True, linewidths=1, ax=ax, vmin=-1, vmax=1)
    ax.set_title('Matrice de corrélation de Pearson', fontsize=12)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "07_correlation.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    charts['correlation'] = path

    print(f"[rapport] {len(charts)} graphiques générés dans {CHARTS_DIR}")
    return charts


def generate_pdf(df, charts):
    """Génère le rapport PDF pour la Mairie."""
    print("[rapport] Génération du PDF...")

    try:
        from fpdf import FPDF
    except ImportError:
        print("[rapport] [ERREUR] fpdf2 non installé.")
        print("[rapport] Installez-le avec : pip install fpdf2")
        print("[rapport] Puis relancez ce script.")
        sys.exit(1)

    class PDF(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, 'ImmoVision 360 - Rapport pour la Mairie de Paris', align='C')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

        def chapter_title(self, title):
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(33, 37, 41)
            self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(33, 150, 243)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

        def body_text(self, text):
            self.set_font('Helvetica', '', 10)
            self.set_text_color(50, 50, 50)
            self.multi_cell(0, 5, text)
            self.ln(3)

        def key_stat(self, label, value):
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(33, 37, 41)
            self.cell(80, 6, f"  {label} : ", new_x="END")
            self.set_font('Helvetica', '', 10)
            self.set_text_color(33, 150, 243)
            self.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ============================
    # PAGE 1 : Couverture
    # ============================
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 15, 'ImmoVision 360', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Diagnostic de l'impact d'Airbnb", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "sur le quartier de l'Elysee (Paris)", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Rapport pour la Mairie de Paris', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, 'Avril 2026', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, 'Donnees : Inside Airbnb (listings.csv) - 2 626 annonces', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, 'Perimetre : Quartier de l\'Elysee (8e arrondissement)', align='C', new_x="LMARGIN", new_y="NEXT")

    # ============================
    # PAGE 2 : Rappel du probleme
    # ============================
    pdf.add_page()
    pdf.chapter_title('1. Rappel du probleme')
    pdf.body_text(
        "La Mairie de Paris souhaite comprendre l'impact des locations de courte duree "
        "(type Airbnb) sur le quartier de l'Elysee. La question centrale : l'economie "
        "de partage s'est-elle transformee en industrie hoteliere masquee, au detriment "
        "du tissu social et de l'equilibre du quartier ?\n\n"
        "Ce rapport analyse 2 626 annonces Airbnb du quartier de l'Elysee autour de "
        "trois hypotheses :"
    )

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(33, 37, 41)

    pdf.cell(0, 7, "  Hypothese A (Economique) :", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "    Est-ce une economie de partage ou une industrie hoteliere masquee ?", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 7, "  Hypothese B (Sociale) :", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "    Le lien social se brise-t-il au profit de processus automatises ?", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 7, "  Hypothese C (Visuelle) :", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, "    Les logements sont-ils devenus des produits financiers steriles ?", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.chapter_title("2. Donnees et chaine de traitement")
    pdf.body_text(
        "Les donnees proviennent d'Inside Airbnb (listings.csv), un referentiel open data "
        "de 81 853 annonces parisiennes. Apres filtrage sur le quartier \"Elysee\" et "
        "selection des colonnes pertinentes, le pipeline ETL produit un jeu de 2 626 "
        "annonces avec 8 variables :\n\n"
        "  - id : identifiant de l'annonce\n"
        "  - calculated_host_listings_count : nb d'annonces par hote\n"
        "  - availability_365 : disponibilite annuelle (0-365 jours)\n"
        "  - host_response_rate_num : taux de reponse (0-100%)\n"
        "  - room_type_code : type de logement (0=partage, 1=prive, 2=entier, 3=hotel)\n"
        "  - host_response_time_code : delai de reponse (0=rapide, 3=lent)\n"
        "  - standardization_score : classification visuelle IA (-1, 0, 1)\n"
        "  - neighborhood_impact_score : classification textuelle IA (-1, 0, 1)\n\n"
        "Le pipeline complet suit une architecture Medallion (Bronze/Silver/Gold) "
        "avec enrichissement IA par Google Gemini pour les scores visuels et textuels."
    )

    # ============================
    # PAGES 3-5 : Résultats
    # ============================
    pdf.add_page()
    pdf.chapter_title("3. Resultats de l'analyse exploratoire")

    # --- Résultat 1 : Concentration ---
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "3.1 Concentration de l'offre (Hypothese A)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    mono = (df['calculated_host_listings_count'] == 1).sum()
    multi = (df['calculated_host_listings_count'] > 1).sum()
    gros = (df['calculated_host_listings_count'] >= 10).sum()

    pdf.key_stat("Mono-proprietaires (1 annonce)", f"{mono} ({mono/len(df)*100:.1f}%)")
    pdf.key_stat("Multi-proprietaires (>1)", f"{multi} ({multi/len(df)*100:.1f}%)")
    pdf.key_stat("Gros acteurs (>=10 annonces)", f"{gros} ({gros/len(df)*100:.1f}%)")
    pdf.key_stat("Maximum d'annonces par hote", f"{df['calculated_host_listings_count'].max()}")
    pdf.ln(2)

    if 'concentration' in charts:
        pdf.image(charts['concentration'], x=10, w=190)
        pdf.ln(3)

    pdf.body_text(
        "La grande majorite des hotes (mono-proprietaires) ne possede qu'une seule annonce. "
        "Cependant, quelques acteurs detiennent des dizaines voire des centaines de biens, "
        "ce qui revele une structure de marche duale : economie de partage d'un cote, et "
        "industrie hoteliere masquee de l'autre."
    )

    # --- Résultat 2 : Disponibilité ---
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "3.2 Disponibilite annuelle", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    zero = (df['availability_365'] == 0).sum()
    high = (df['availability_365'] > 270).sum()
    pdf.key_stat("Logements fermes (0 jours)", f"{zero} ({zero/len(df)*100:.1f}%)")
    pdf.key_stat("Quasi plein temps (>270 jours)", f"{high} ({high/len(df)*100:.1f}%)")
    pdf.key_stat("Moyenne", f"{df['availability_365'].mean():.0f} jours")
    pdf.ln(2)

    if 'disponibilite' in charts:
        pdf.image(charts['disponibilite'], x=15, w=180)
        pdf.ln(3)

    pdf.body_text(
        "La distribution de la disponibilite est bimodale : un pic a 0 jour (logements "
        "non ouverts a la reservation) et un second pic au-dessus de 270 jours. "
        "Ce second groupe represente des biens quasiment disponibles toute l'annee, "
        "ce qui s'apparente a de la location professionnelle continue."
    )

    # --- Résultat 3 : Types de logement ---
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "3.3 Types de logement", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    if 'types' in charts:
        pdf.image(charts['types'], x=25, w=160)
        pdf.ln(3)

    entire = (df['room_type_code'] == 2).sum()
    pdf.body_text(
        f"Les logements entiers (Entire home/apt) representent la majorite de l'offre "
        f"({entire/len(df)*100:.0f}%). Cette predominance confirme que le quartier de "
        f"l'Elysee est un marche de location de residence complete plutot que "
        f"d'hebergement chez l'habitant."
    )

    # --- Résultat 4 : Réactivité professionnelle ---
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "3.4 Reactivite et professionnalisation (Hypothese B)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    if 'reactivite' in charts:
        pdf.image(charts['reactivite'], x=15, w=180)
        pdf.ln(3)

    pdf.body_text(
        "Les hotes repondant 'dans l'heure' tendent a detenir plus d'annonces en moyenne. "
        "Ce profil de reactivite rapide, typique d'un service client professionnel, "
        "renforce l'hypothese d'une gestion automatisee chez les gros acteurs. "
        "La forte proportion d'hotes sans information de delai (-1) nuance toutefois "
        "cette observation."
    )

    # --- Résultat 5 : Scores croisés ---
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 8, "3.5 Croisement image x texte (Hypotheses B et C)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    if 'heatmap' in charts:
        pdf.image(charts['heatmap'], x=25, w=155)
        pdf.ln(3)

    pdf.body_text(
        "Le tableau croise des scores de standardisation visuelle (image) et d'impact "
        "sur le voisinage (texte) montre une tendance a la coincidence sur la diagonale. "
        "ATTENTION : les scores utilises dans cette version sont des valeurs fictives "
        "(aleatoires). Avec de vraies classifications IA (Google Gemini), cette analyse "
        "prendrait tout son sens pour confirmer ou infirmer le lien entre "
        "industrialisation visuelle et deshumanisation de l'accueil."
    )

    # --- Corrélation ---
    if 'correlation' in charts:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(33, 37, 41)
        pdf.cell(0, 8, "3.6 Vue d'ensemble : matrice de correlation", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.image(charts['correlation'], x=20, w=170)
        pdf.ln(3)
        pdf.body_text(
            "La matrice de correlation de Pearson resume les liaisons lineaires entre "
            "les 7 variables numeriques. Les correlations faibles avec les scores IA "
            "sont attendues (valeurs fictives). Les variables economiques "
            "(nombre d'annonces, disponibilite) montrent des associations plus "
            "significatives entre elles."
        )

    # ============================
    # PAGE : Limites
    # ============================
    pdf.add_page()
    pdf.chapter_title("4. Limites de l'etude")
    pdf.body_text(
        "Cette analyse presente plusieurs limites qu'il est essentiel de souligner :\n\n"
        "1. Donnees Airbnb uniquement : nous n'avons pas de donnees comparatives "
        "sur les hotels classiques ou le marche locatif traditionnel. Il est donc "
        "impossible de mesurer la part relative d'Airbnb dans la dynamique du quartier.\n\n"
        "2. Prix absent : la variable de prix n'est pas disponible dans le jeu "
        "de donnees nettoyees (elysee_tabular). L'hypothese de la 'Machine a Cash' "
        "ne peut donc pas etre testee directement par une correlation prix/concentration.\n\n"
        "3. Scores IA fictifs : les colonnes standardization_score et "
        "neighborhood_impact_score contiennent des valeurs aleatoires generees pour "
        "assurer le fonctionnement du pipeline. Les conclusions sur les hypotheses B "
        "(deshumanisation) et C (standardisation) sont donc illustratives.\n\n"
        "4. Correlation et causalite : toutes les associations observees dans ce rapport "
        "sont des correlations statistiques. Elles ne prouvent pas de relation de "
        "cause a effet. Des facteurs tiers (saisonnalite, legislation, type de quartier) "
        "pourraient expliquer les co-variations observees.\n\n"
        "5. Generalisation : les resultats portent uniquement sur le quartier de "
        "l'Elysee. Toute extension a d'autres quartiers parisiens necessiterait "
        "une analyse distincte.\n\n"
        "6. Valeurs manquantes : les champs non renseignes (codes -1 apres traitement) "
        "representent une part significative pour certaines variables (taux de reponse, "
        "delai de reponse). L'absence d'information est elle-meme un signal a interpreter "
        "avec prudence."
    )

    # ============================
    # PAGE : Conclusion
    # ============================
    pdf.chapter_title("5. Conclusion et recommandations")
    pdf.body_text(
        "L'analyse exploratoire du quartier de l'Elysee revele un marche Airbnb "
        "caracterise par :\n\n"
        "- Une forte concentration de l'offre : quelques acteurs detiennent des "
        "dizaines voire des centaines d'annonces, ce qui s'apparente davantage "
        "a une industrie hoteliere qu'a une economie de partage.\n\n"
        "- Deux profils de disponibilite : logements fermes (0 jours) vs logements "
        "quasi-permanents (>270 jours), suggerant une segmentation entre "
        "residence occasionnelle et location professionnelle.\n\n"
        "- Une predominance de logements entiers : le quartier offre principalement "
        "des residences completes, confirmant que l'offre s'eloigne du partage "
        "de chambre chez l'habitant.\n\n"
        "- Des indices de professionnalisation : la reactivite rapide des gros "
        "hotes evoque une gestion automatisee de type hoteliere.\n\n"
        "Ces resultats, bien que soumis aux limites enoncees, fournissent une base "
        "factuelle pour orienter la politique de regulation. Nous recommandons :\n\n"
        "  1. Un enrichissement des donnees avec les vrais scores IA (Gemini) "
        "pour valider les hypotheses B et C.\n"
        "  2. Une integration des donnees de prix pour tester l'hypothese A "
        "de maniere complete.\n"
        "  3. Une extension de l'analyse a d'autres quartiers parisiens pour "
        "comparer les dynamiques."
    )

    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "Rapport genere automatiquement par le pipeline ImmoVision 360.", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Donnees : Inside Airbnb - Analyse : Python (Pandas, Matplotlib, Seaborn, Scikit-learn).", align='C', new_x="LMARGIN", new_y="NEXT")

    # Sauvegarde
    pdf.output(OUTPUT_PDF)
    print(f"[rapport] [OK] PDF genere : {OUTPUT_PDF}")
    print(f"[rapport] Nombre de pages : {pdf.page_no()}")


def main():
    """Pipeline principal."""
    print("=" * 60)
    print("GENERATION DU RAPPORT PDF POUR LA MAIRIE DE PARIS")
    print("=" * 60)

    ensure_dirs()
    df = load_data()
    charts = generate_charts(df)
    generate_pdf(df, charts)

    print("\n" + "=" * 60)
    print(f"Rapport disponible : {OUTPUT_PDF}")
    print("=" * 60)


if __name__ == "__main__":
    main()
