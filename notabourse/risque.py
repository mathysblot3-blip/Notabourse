"""Barre du risque de faillite de la fiche : AFFICHAGE SEULEMENT (demande de Mathys du 21/10/2026).

Ni la note ni l'exclusion ne changent : le curseur montre, sans chiffre, l'état que la fiche affiche déjà.
  - zone rouge « risqué » : société exclue de la sélection par la formule ;
  - zone orange « à surveiller » : gardée, mais un point de vigilance (seuils d'affichage de Mathys) ;
  - zone verte « peu risqué » : aucun signal.
Dans sa zone, le curseur suit le voyant le plus faible, noté de -1 à +1 comme dans la formule, mais avec les seuils
d'affichage du site pour le vert (60 % de dettes, 4 fois les intérêts, 6 % de fonds propres pour une financière, et
jamais vert si l'activité consomme de l'argent).
"""
import pandas as pd   # valeurs manquantes

from notabourse.constantes import ROUGE, SEUILS_GARDE_FOU, SEUILS_VIGILANCE, VERT
from notabourse.phrases import sante

# Place de chaque état sur la barre (en % de la largeur) : rouge à gauche, vert à droite, comme le prix [M]
ZONES = {"exclue": (0.0, 100 / 3), "vigilance": (100 / 3, 200 / 3), "bonne": (200 / 3, 100.0)}
MARGE = 1.5           # le curseur reste un peu à l'intérieur de sa zone, pour qu'on voie bien laquelle [P]


def _note(valeur, vert, rouge):
    """Note de -1 à +1 d'une valeur, même forme que la formule (outils/garde_fou.py) : +1/3 au seuil vert, -1/3 au
    seuil rouge, bornée."""
    n = ROUGE + (VERT - ROUGE) * (valeur - rouge) / (vert - rouge)
    return max(-1.0, min(1.0, n))


def _connu(x):
    """Vrai si la valeur existe."""
    return x is not None and not pd.isna(x)


def note_affichee(v):
    """Note d'un voyant avec les seuils d'affichage du site pour le vert (le rouge reste celui de la formule)."""
    if v["note"] is None:
        return None                                                           # voyant incalculable
    m, nom = v["mesure"] or {}, v["voyant"]
    if nom == "trésorerie":
        if m.get("flux_positif"):
            return 1.0                                                        # l'activité rapporte de l'argent
        if _connu(m.get("annees")):
            vert, rouge = SEUILS_GARDE_FOU["trésorerie"]
            return min(_note(m["annees"], vert, rouge), VERT - 0.01)          # flux négatif : jamais vert
    if nom == "endettement" and _connu(m.get("tlmta")):
        return _note(m["tlmta"], SEUILS_VIGILANCE["endettement"], SEUILS_GARDE_FOU["endettement"][1])
    if nom == "intérêts":
        if m.get("sans_interets"):
            return 1.0                                                        # aucun intérêt à payer
        if m.get("ebitda_negatif"):
            return -1.0                                                       # résultats négatifs, intérêts à payer
        if _connu(m.get("couverture")):
            return _note(m["couverture"], SEUILS_VIGILANCE["intérêts"], SEUILS_GARDE_FOU["intérêts"][1])
    if nom == "fonds propres / actif" and _connu(m.get("ratio")):
        return _note(m["ratio"], SEUILS_VIGILANCE["fonds propres / actif"], SEUILS_GARDE_FOU["fonds propres / actif"][1])
    return v["note"]                                                          # repli : note de la formule


def position_risque(f):
    """Place du curseur (0 à 100, à gauche le plus risqué) et état montré (« exclue », « vigilance », « bonne »).
    Renvoie (None, état) si l'état est inconnu : pas de barre."""
    statut = sante(f)["statut"]
    if statut not in ZONES:
        return None, statut
    gf = f["garde_fou"]
    notes = [n for n in (note_affichee(v) for v in gf["voyants"]) if _connu(n)]
    if _connu(gf.get("moyenne")):
        notes.append(gf["moyenne"])                                           # la moyenne de la formule compte aussi
    base = min(notes) if notes else 0.0                                       # le point le plus faible
    bas, haut = ZONES[statut]
    return min(max(50.0 + 50.0 * base, bas + MARGE), haut - MARGE), statut   # toujours dans la zone de l'état
