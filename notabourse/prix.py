"""Prix comparé au secteur : le PER de la société face au PER de son secteur (demande de Mathys du 21/10/2026).

Indicateur AFFICHÉ À PART : il n'entre pas dans la note et ne change pas la formule C8. Calcul repris tel quel de la
recherche (Recherche_score/36_per_secteur.py, choix sourcés dans indicateur_per_secteur.md) :
  - PER = capitalisation / bénéfice net des 12 derniers mois ; bénéfice négatif ou nul : PER non calculable ;
  - PER du secteur = 1 / moyenne des (bénéfice / capitalisation) des membres bénéficiaires du S&P 500 du même secteur,
    soit la moyenne harmonique de leurs PER ; moins de 5 membres bénéficiaires : tout le groupe ;
  - écart = PER / PER du secteur - 1 ; -20 % ou moins : bon marché ; +25 % ou plus : chère ; sinon dans la norme.
La référence ne garde que le rapport bénéfice / capitalisation (colonne EP), jamais les montants.

Replis [M] 21/10/2026 (« toujours avoir quelque chose à dire », avec « valeur peu fiable » sur la fiche), pour la SEULE
société affichée : bénéfice du dernier exercice, bénéfice moyen des derniers exercices, PER donné par Yahoo, puis prix
rapporté aux ventes face au même rapport du secteur. Si la référence de la semaine n'a pas ces colonnes : moyennes des
secteurs gardées dans reference/prix_secteurs_secours.csv (construites par reference/construire_secours_prix.py).
"""
import math           # logarithme, pour placer le curseur sur la barre
from functools import lru_cache   # table de secours lue une seule fois
from pathlib import Path          # chemin de la table de secours

import pandas as pd   # tableaux de données

from notabourse.constantes import (PRIX_BON_MARCHE, PRIX_BORNE_BARRE, PRIX_CHERE, PRIX_MIN_PAIRS,
                                   PRIX_PER_MAX_REPLI)

SECOURS = Path(__file__).resolve().parents[1] / "reference" / "prix_secteurs_secours.csv"
REPLIS = ("exercice", "moyenne", "yahoo")   # origines de repli du bénéfice de la société (notabourse/ratios.py)


def _nombre(x):
    """Nombre décimal, ou None si la valeur manque."""
    return None if x is None or pd.isna(x) else float(x)


def position_barre(ratio):
    """Place du curseur sur la barre, de 0 (à gauche, chère) à 100 (à droite, bon marché).

    Échelle logarithmique : « 2 fois plus cher » et « 2 fois moins cher » sont à la même distance du milieu, et les deux
    seuils aussi (1,25 et 0,8 = 1 / 1,25). Au-delà de 2 fois, le curseur reste au bord."""
    if ratio is None or ratio <= 0:
        return None
    x = math.log(ratio) / math.log(PRIX_BORNE_BARRE)                          # -1 (2 fois moins cher) à +1 (2 fois plus)
    return 50.0 - 50.0 * max(-1.0, min(1.0, x))                               # plus cher = plus à gauche


def moyenne_secteur(ref, groupe, secteur, colonne):
    """Moyenne des valeurs positives d'une colonne (EP ou SP) chez les membres du même secteur, au moins 5, sinon tout
    le groupe. Renvoie (moyenne, nombre de membres, repli sur le groupe) ou (None, 0, False)."""
    if colonne not in ref.columns:
        return None, 0, False
    g = ref[ref["groupe"] == groupe]
    valeurs = g[colonne].where(g[colonne] > 0)                                # pertes : écartées
    pairs, repli = valeurs[g["secteur"] == secteur].dropna(), False          # même secteur (financières : « FIN »)
    if len(pairs) < PRIX_MIN_PAIRS:                                           # trop peu : tout le groupe
        pairs, repli = valeurs.dropna(), True
    return (float(pairs.mean()), int(len(pairs)), repli) if len(pairs) else (None, 0, False)


@lru_cache(maxsize=1)
def table_secours():
    """Moyennes des secteurs gardées à part (dernier recours), ou None si le fichier manque."""
    return pd.read_csv(SECOURS) if SECOURS.exists() else None


def _moyenne_ou_secours(ref, groupe, secteur, colonne):
    """Moyenne du secteur dans la référence, sinon dans la table de secours (avec sa date)."""
    moyenne, nb, repli = moyenne_secteur(ref, groupe, secteur, colonne)
    if moyenne is not None:
        return moyenne, nb, repli, None
    s = table_secours()
    if s is None or colonne not in s.columns:
        return None, 0, False, None
    ligne = s[(s["groupe"] == groupe) & (s["secteur"] == secteur)]
    if not len(ligne) or pd.isna(ligne[colonne].iloc[0]):
        return None, 0, False, None
    l = ligne.iloc[0]
    return float(l[colonne]), int(l["nb_" + colonne]), bool(l["repli_" + colonne]), str(l["date"])


def prix_secteur(ligne, ref):
    """Prix de la société comparé à son secteur, parmi les membres du S&P 500 de la référence.

    ligne : ratios de la société (EP = bénéfice / capitalisation ; replis EP_AFF, EP_ORIGINE, SP) ; ref : référence.
    Renvoie un dictionnaire : mesure (« per » ou « ventes »), multiple de la société et du secteur, rapport, écart,
    verdict, origine du chiffre, fiabilité, nombre de membres, repli sur le groupe, place du curseur sur la barre."""
    sortie = {"mesure": "per", "per": None, "per_secteur": None, "ep": None, "ep_moyen": None, "ratio": None,
              "ecart": None, "verdict": "manquant", "nb_pairs": 0, "repli_groupe": False, "position": None,
              "origine": None, "nb_exercices": None, "fiable": False, "secours": None, "perte": False}
    groupe, secteur = ligne["groupe"], ligne["secteur"]
    ep12 = _nombre(ligne.get("EP"))                                           # 12 derniers mois (formule de recherche)
    ep_aff, origine = _nombre(ligne.get("EP_AFF")), ligne.get("EP_ORIGINE")
    sortie["perte"] = ep12 is not None and ep12 <= 0
    # 1. Rapport utilisé pour la société : bénéfice (12 mois, sinon repli), sinon ventes
    if ep12 is not None and ep12 > 0:
        mesure, valeur, sortie["origine"] = "per", ep12, "12_mois"
    elif ep_aff is not None and ep_aff >= 1 / PRIX_PER_MAX_REPLI and origine in REPLIS:   # bénéfice quasi nul : ventes
        mesure, valeur, sortie["origine"] = "per", ep_aff, origine
        nb = _nombre(ligne.get("EP_NB_EXERCICES"))
        sortie["nb_exercices"] = int(nb) if nb else None
    elif _nombre(ligne.get("SP")) is not None and _nombre(ligne.get("SP")) > 0:
        mesure, valeur, sortie["origine"] = "ventes", _nombre(ligne.get("SP")), "ventes"
    else:
        mesure, valeur = "per", None
    sortie["mesure"], sortie["ep"] = mesure, valeur
    # 2. Même rapport pour le secteur (moyenne des rapports = moyenne harmonique des multiples)
    colonne = "EP" if mesure == "per" else "SP"
    moyenne, nb, repli, date_secours = _moyenne_ou_secours(ref, groupe, secteur, colonne)
    if moyenne is None:                                                       # rien, même dans la table de secours
        sortie["verdict"] = "reference_ancienne" if colonne not in ref.columns else "manquant"
        return sortie
    sortie.update({"ep_moyen": moyenne, "nb_pairs": nb, "repli_groupe": repli, "secours": date_secours,
                   "per_secteur": 1.0 / moyenne})
    if valeur is None:                                                        # perte sans repli possible, ou rien
        sortie["verdict"] = "pertes" if sortie["perte"] else "manquant"
        return sortie
    sortie["per"] = 1.0 / valeur                                              # PER, ou prix / ventes
    sortie["ratio"] = sortie["per"] / sortie["per_secteur"]
    sortie["ecart"] = sortie["ratio"] - 1.0
    sortie["verdict"] = ("bon_marche" if sortie["ratio"] <= PRIX_BON_MARCHE else
                         "chere" if sortie["ratio"] >= PRIX_CHERE else "norme")
    sortie["position"] = position_barre(sortie["ratio"])
    sortie["fiable"] = sortie["origine"] == "12_mois" and date_secours is None
    return sortie
