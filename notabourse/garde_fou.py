"""Garde-fou noté de -1 à +1 et exclusions (formule C8), COPIÉS de Recherche_score/outils/garde_fou.py (19/10/2026).

Chaque voyant reçoit une note de -1 (très mauvais) à +1 (très bon) :
  rouge de -1 à -1/3, orange de -1/3 à +1/3, vert de +1/3 à +1.
note = -1/3 + (2/3) x (valeur - seuil rouge) / (seuil vert - seuil rouge), puis bornée à [-1, 1].
Garde-fou de l'action = moyenne des voyants calculables ; l'action est exclue si cette moyenne est orange ou rouge
(< +1/3), si son bénéfice est <= 0 sur l'un des deux derniers exercices, ou si ses fonds propres sont <= 0.
Seule différence avec la recherche : la recherche lisait ses ratios dans un fichier (garde_fou_note), le site les reçoit
directement ; le calcul est le même.
"""
import numpy as np   # calcul numérique
import pandas as pd  # tableaux de données

from notabourse.constantes import ROUGE, SEUILS_GARDE_FOU, VERT


def note_voyant(valeur, seuil_vert, seuil_rouge):
    """Note de -1 à +1 d'un voyant ; marche dans les deux sens (seuil vert au-dessus ou au-dessous du rouge)."""
    note = ROUGE + (VERT - ROUGE) * (valeur - seuil_rouge) / (seuil_vert - seuil_rouge)  # droite passant par les seuils
    return note.clip(-1, 1)                                                   # bornée à -1 et +1


def notes_garde_fou(r):
    """Notes des voyants à partir des ratios bruts r (une ligne par société). Renvoie un DataFrame.
    Industrie et foncières : trésorerie, endettement, intérêts. Financières : fonds propres / actif.
    Colonnes lues : groupe, CASH, CFO_TTM, TLMTA, EBITDA_TTM, INTERETS_TTM, E_FP."""
    nf = r["groupe"] != "FIN"                                                 # vrai pour l'industrie et les foncières
    # Trésorerie : seulement si le flux d'exploitation est négatif (années de trésorerie) ; sinon la société
    # finance son activité elle-même : +1
    autonomie = r["CASH"] / (-r["CFO_TTM"])                                   # années de trésorerie
    tresorerie = note_voyant(autonomie, *SEUILS_GARDE_FOU["trésorerie"]).where(r["CFO_TTM"] < 0, 1.0).where(
        r["CFO_TTM"].notna())                                                 # +1 si flux positif, rien si inconnu
    # Endettement : TLMTA = dettes / (dettes + capitalisation), plus bas = mieux
    endettement = note_voyant(r["TLMTA"], *SEUILS_GARDE_FOU["endettement"])
    # Intérêts : EBITDA / intérêts ; EBITDA négatif avec des intérêts : -1 ; pas d'intérêts : +1
    couverture = note_voyant(r["EBITDA_TTM"] / r["INTERETS_TTM"], *SEUILS_GARDE_FOU["intérêts"])
    couverture = couverture.where(~((r["EBITDA_TTM"] <= 0) & (r["INTERETS_TTM"] > 0)), -1.0)
    couverture = couverture.where(~(r["INTERETS_TTM"] <= 0), 1.0)
    # Financières : fonds propres / actif (banques : tangibles et économiques), vert 5 %, rouge 4 %
    fonds_propres = note_voyant(r["E_FP"], *SEUILS_GARDE_FOU["fonds propres / actif"])
    return pd.DataFrame({"trésorerie": tresorerie.where(nf), "endettement": endettement.where(nf),
                         "intérêts": couverture.where(nf), "fonds propres / actif": fonds_propres.where(~nf)},
                        index=r.index)


def couleur(note):
    """Couleur d'une note de -1 à +1."""
    return np.where(note >= VERT, "vert", np.where(note > ROUGE, "orange", "rouge"))


def exclusions(r):
    """Conditions d'exclusion de C8 pour chaque ligne de r (copie de exclusion_c8, données reçues directement).
    Colonnes lues : celles de notes_garde_fou, plus NI_FY0, NI_FY1 (bénéfice des deux derniers exercices), SE_EXCLUSION
    (fonds propres, avec le repli actif - passif - minoritaires de la recherche).
    Renvoie un DataFrame : garde_fou (moyenne), une colonne vrai/faux par condition remplie, et « gardee »."""
    g = notes_garde_fou(r).mean(axis=1)                                       # moyenne des voyants calculables
    sortie = pd.DataFrame(index=r.index)
    sortie["garde_fou"] = g                                                   # de -1 à +1, vide si aucun voyant
    sortie["garde_fou_ok"] = g.isna() | (g >= VERT)                           # vert, ou incalculable : pas d'exclusion
    sortie["benefices_ok"] = (r["NI_FY0"] > 0) & (r["NI_FY1"] > 0)            # bénéfice > 0 sur les deux exercices
    sortie["fonds_propres_ok"] = r["SE_EXCLUSION"] > 0                        # fonds propres > 0
    sortie["gardee"] = sortie["garde_fou_ok"] & sortie["benefices_ok"] & sortie["fonds_propres_ok"]
    return sortie
