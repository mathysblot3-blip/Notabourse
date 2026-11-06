"""Indices boursiers d'une société (06/11/2026) : Nikkei 225, CAC 40, DAX... affichés sur la fiche et dans le classement.

La table reference/indices.csv est faite par reference/construire_indices.py (listes de Wikipédia, refaites chaque
samedi). Une société est reconnue par son symbole, ou par son nom simplifié si sa cotation est une autre que celle de
la liste (Allianz : ALV.DE dans l'indice, ALV.VI dans le classement). Affichage seulement : la note ne change pas.
Le S&P 500 n'y figure pas : il vient de la référence (membres_sp500.csv).
"""
import re                        # nettoyage des noms de sociétés
from functools import lru_cache  # table lue une seule fois
from pathlib import Path         # chemins de fichiers

import pandas as pd              # tableaux de données

FICHIER = Path(__file__).resolve().parents[1] / "reference" / "indices.csv"
# Ordre d'affichage : indices des grands pays d'abord, l'indice européen ensuite
INDICES = ["Nikkei 225", "CAC 40", "DAX", "FTSE 100", "Euro Stoxx 50", "SMI", "AEX", "IBEX 35", "FTSE MIB", "OMXS30",
           "Hang Seng", "CSI 300", "KOSPI 200", "Nifty 50", "S&P/ASX 50", "S&P/TSX 60"]


def cle_nom(nom):
    """Nom simplifié pour repérer une même société cotée deux fois : « ASML Holding N.V. » -> « asml »."""
    nom = re.sub(r"[^a-z0-9 ]", "", str(nom).lower().replace("-", " "))      # « N.V. » -> « nv », sans ponctuation
    nom = re.sub(r"\b(inc|corp|corporation|plc|ltd|limited|sa|se|nv|ag|co|company|holdings?|group|the)\b", "", nom)
    return nom.replace(" ", "")                                               # mots juridiques retirés, puis collé


@lru_cache(maxsize=1)
def table_indices():
    """(symbole -> indices, nom simplifié -> indices), lus dans reference/indices.csv ; vides si le fichier manque."""
    if not FICHIER.exists():
        return {}, {}
    t = pd.read_csv(FICHIER, dtype=str)
    return (t.groupby("symbole")["indice"].apply(set).to_dict(), t.groupby("cle")["indice"].apply(set).to_dict())


def indices_de(symbole, nom):
    """Indices d'une société, dans l'ordre d'affichage (liste vide si aucun)."""
    par_symbole, par_nom = table_indices()
    trouves = par_symbole.get(symbole, set()) | par_nom.get(cle_nom(nom), set())
    return [i for i in INDICES if i in trouves]
