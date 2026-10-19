"""Groupe (industrie NF, financières FIN, foncières REIT), secteur et sous-secteur d'une société.

Règle [M] 19/10/2026 : code SIC de la SEC quand la société y dépose, avec les fonctions de la recherche
(Recherche_score/08_panel_point_in_time.py : groupe_de, secteur_de ; 09_composantes.py : sous-secteur).
Sinon : table « industrie Yahoo -> groupe, secteur, sous-secteur » (reference/correspondance_yahoo.csv, étape b).
"""
from pathlib import Path  # chemins de fichiers

import pandas as pd  # tableaux de données

DOSSIER_REFERENCE = Path(__file__).resolve().parents[1] / "reference"     # dossier site/reference
FF12 = pd.read_csv(DOSSIER_REFERENCE / "ff12_sic.csv")                     # 12 industries de Fama-French (table de K. French)


def groupe_de(sic):
    """Groupe de comparaison (conception §2.1) : FIN, REIT ou NF. Copie de la recherche."""
    if pd.isna(sic):                                                       # pas de SIC : industrie
        return "NF"
    sic = int(sic)
    if sic == 6798:                                                        # 6798 = foncières cotées (REIT)
        return "REIT"
    if 6000 <= sic <= 6399 or 6700 <= sic <= 6791 or sic == 6799:          # banques, crédit, courtage, assurance...
        return "FIN"
    return "NF"


def secteur_de(sic, groupe):
    """Secteur Fama-French 12 ; « Money » remplacé par FIN et REIT, le reste de Money va dans « Other ».
    Copie de la recherche."""
    if groupe in ("FIN", "REIT"):                                          # financières et foncières : leur propre secteur
        return groupe
    if pd.isna(sic):
        return "Other"
    ligne = FF12[(FF12["sic_min"] <= sic) & (FF12["sic_max"] >= sic)]      # intervalle SIC qui contient ce code
    nom = ligne["industrie"].iloc[0] if len(ligne) else "Other"            # hors de tous les intervalles : Other
    return "Other" if nom == "Money" else nom


def sous_secteur_de(sic, groupe, secteur):
    """Sous-secteur des financières : banques (SIC 6000-6199), assurances (6300-6399), autres.
    Pour les autres groupes, le sous-secteur est le secteur (comme 09_composantes.py)."""
    if groupe != "FIN":
        return secteur
    if pd.notna(sic) and 6000 <= sic <= 6199:
        return "banques"
    if pd.notna(sic) and 6300 <= sic <= 6399:
        return "assurances"
    return "autres"


def classer_par_sic(sic):
    """(groupe, secteur, sous-secteur) d'après le code SIC."""
    groupe = groupe_de(sic)                                                # NF, FIN ou REIT
    secteur = secteur_de(sic, groupe)                                      # l'un des 12 secteurs
    return groupe, secteur, sous_secteur_de(sic, groupe, secteur)


def classer_par_yahoo(industrie, table):
    """(groupe, secteur, sous-secteur) d'après l'industrie Yahoo, avec la table construite à l'étape b.
    Renvoie None si l'industrie n'est pas dans la table."""
    if table is None or industrie is None:
        return None
    ligne = table[table["industrie_yahoo"] == industrie]                   # ligne de cette industrie
    if ligne.empty:
        return None
    l = ligne.iloc[0]
    return l["groupe"], l["secteur"], l["sous_secteur"]


def charger_correspondance_yahoo():
    """Table industrie Yahoo -> groupe, secteur, sous-secteur (None tant qu'elle n'existe pas)."""
    chemin = DOSSIER_REFERENCE / "correspondance_yahoo.csv"
    return pd.read_csv(chemin) if chemin.exists() else None
