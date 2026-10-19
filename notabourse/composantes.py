"""Fonctions de calcul des composantes, COPIÉES de la recherche (Recherche_score/outils/composantes.py, 19/10/2026).

Règle du site : la formule n'est pas modifiée. Chaque fonction ci-dessous reprend la fonction de recherche ligne à ligne.
Deux fonctions de recherche sont seulement COUPÉES EN DEUX, sans changer leur calcul, pour que la référence publique
contienne des croissances (ratios) et non des montants bruts :
  - pers()   = croissances_pers()  (calcul par société)  + pers_depuis_croissances()  (calcul par groupe) ;
  - gs_lsv() = croissances_gs()    (calcul par société)  + gs_depuis_croissances()    (calcul par groupe).
Les paramètres de durée (trimestres ou années) sont passés en arguments : avec les paramètres trimestriels de la
recherche, le résultat est identique à la recherche (vérifié par Recherche_score/33_equivalence_site.py).
Vocabulaire : « cik » désigne l'identifiant d'une société (numéro SEC dans la recherche, symbole boursier sur le site).
"""
import numpy as np   # calcul numérique (tableaux de nombres, racine carrée, logarithme)
import pandas as pd  # tableaux de données (lignes et colonnes, comme une feuille Excel)

from notabourse.constantes import (JOURS_COURS_RECENT, JOURS_FENETRE_DEBUT, JOURS_FENETRE_FIN, MIN_SEMAINES_M1,
                                   MOIS_RECENCE, PERS_BAS, PERS_HAUT, POIDS_PERS)


# --- 1. Cours : dynamique M1 en version « action - marché » (W1) ---------------------------------------------------
def hebdomadaire(serie):
    """Clôtures de fin de semaine (vendredi). Copie de la recherche."""
    return serie.resample("W-FRI").last()                                     # dernière clôture de chaque semaine


def tente(a):
    """Transformation de M1 (conception §4.1) : hausses extrêmes neutralisées, baisses extrêmes plafonnées.
    Renvoie la moyenne, l'écart-type et le nombre de semaines du rendement résiduel transformé. Copie de la recherche."""
    a = np.asarray(a, dtype=float)                                            # liste de rendements -> tableau de nombres
    med = np.median(a)                                                        # médiane des semaines du titre
    s = 1.4826 * np.median(np.abs(a - med))                                   # écart robuste (MAD)
    T = med + 2 * s                                                           # début de la zone de hausse extrême
    a = np.where(a <= T, a, np.maximum(2 * T - a, med))                       # au-delà de T : décroît jusqu'à la médiane
    a = np.maximum(a, med - 3 * s)                                            # baisse extrême : plafonnée
    return {"m1_moyenne": a.mean(), "m1_ecart_type": a.std(ddof=1), "m1_n": len(a)}


def m1_final(moyenne, ecart_type, n, s_med):
    """M1 = t de Student si le titre est en avance ; sinon ampleur du retard rapportée à s_med (médiane du groupe).
    Copie de la recherche."""
    t = moyenne / ecart_type * np.sqrt(n)                                     # avance : t de Student
    retard = moyenne / s_med * np.sqrt(n)                                     # retard : rapporté à l'écart-type médian
    return np.where(moyenne > 0, t, retard)                                   # l'un ou l'autre selon le signe


def dynamique_w1(cours, marche_hebdo, D):
    """Éléments de M1 « action - marché » (variante W1) d'un titre à la date D, et date de son premier cours.

    Reprise exacte de la partie W1 de caracteristiques_cours() de la recherche, pour UNE date.
    cours : DataFrame (date, adj_close) en dollars ; marche_hebdo : clôtures hebdomadaires du S&P 500 TR.
    Renvoie un dict (premier_cours, m1w1_moyenne, m1w1_ecart_type, m1w1_n), vide si aucun cours récent."""
    c = cours.dropna(subset=["adj_close"]).set_index("date").sort_index()     # cours valides, rangés par date
    hebdo = np.log(hebdomadaire(c["adj_close"])).diff()                       # log-rendement hebdomadaire du titre
    m = np.log(marche_hebdo).diff().reindex(hebdo.index)                      # même semaine pour le marché
    paire = pd.DataFrame({"r": hebdo, "m": m}).dropna()                       # semaines où les deux existent
    jours = c.index.values                                                    # jours de bourse du titre
    veille = D - pd.Timedelta(days=1)                                         # on ne lit que jusqu'à la veille de D
    L = np.searchsorted(jours, np.datetime64(veille), side="right") - 1       # position du dernier jour <= D - 1
    ligne = {}
    if L < 0 or (veille - c.index[L]).days > JOURS_COURS_RECENT:              # pas de cours récent : rien
        return ligne
    ligne["premier_cours"] = c.index[0]                                       # premier cours connu (ancienneté)
    if L - JOURS_FENETRE_DEBUT >= 0:                                          # au moins 252 jours de bourse
        debut, fin = c.index[L - JOURS_FENETRE_DEBUT], c.index[L - JOURS_FENETRE_FIN]  # du 252e au 22e jour avant D
        fenetre = paire[(paire.index >= debut) & (paire.index <= fin)]        # semaines de la fenêtre
        if len(fenetre) >= MIN_SEMAINES_M1:                                   # au moins 40 semaines
            ligne.update({k.replace("m1_", "m1w1_"): v                        # noms « m1w1_ » comme la recherche
                          for k, v in tente((fenetre["r"] - fenetre["m"]).values).items()})
    return ligne


# --- 2. Croissance -------------------------------------------------------------------------------------------------
def croissance_symetrique(x, x4):
    """d = (X_q - X_q-4) / ((|X_q| + |X_q-4|) / 2), 0 si les deux sont nuls : valable avec des pertes.
    Copie de la recherche."""
    x, x4 = np.asarray(x, dtype=float), np.asarray(x4, dtype=float)           # en tableaux de nombres
    base = (np.abs(x) + np.abs(x4)) / 2                                       # moyenne des valeurs absolues
    with np.errstate(divide="ignore", invalid="ignore"):                      # division par zéro : pas d'alerte
        d = np.where(base == 0, 0.0, (x - x4) / base)                         # 0 si les deux valeurs sont nulles
    return d


def croissances_pers(table, colonne, colonne_prec, D, mois_fenetre):
    """Première moitié de pers() de la recherche : taux symétriques d de chaque société, dans la fenêtre.
    table : une ligne par (cik, fin) avec la valeur X de la période (colonne) et celle de la période comparable
    précédente (colonne_prec). Renvoie (cik, fin, d)."""
    t = table[["cik", "fin", colonne, colonne_prec]].dropna().copy()          # périodes où les deux valeurs existent
    t = t[t["fin"] >= D - pd.DateOffset(months=mois_fenetre)]                 # fenêtre (et marge de décalage)
    t["d"] = croissance_symetrique(t[colonne], t[colonne_prec])               # taux de croissance symétrique
    return t[["cik", "fin", "d"]]


def pers_depuis_croissances(t, groupe_de_cik, D, nb, minimum, jours_periode, taille_bloc, frequence_civile,
                            decalage_civil_mois):
    """Seconde moitié de pers() de la recherche : correction par la médiane du groupe, bornes, poids, moyenne.
    t : (cik, fin, d) ; groupe_de_cik : groupe de chaque cik. Paramètres trimestriels de la recherche :
    nb=20, minimum=4, jours_periode=91.31, taille_bloc=4, frequence_civile='Q', decalage_civil_mois=0."""
    t = t.reset_index(drop=True)                                              # lignes numérotées 0, 1, 2... (sans doublon)
    t["groupe"] = t["cik"].map(groupe_de_cik)                                 # groupe (NF, FIN, REIT) de la société
    t = t.dropna(subset=["groupe"])                                           # société sans groupe : ignorée
    t["civil"] = (t["fin"] - pd.DateOffset(months=decalage_civil_mois)).dt.to_period(frequence_civile)  # période civile
    t["d_corrige"] = t["d"] - t.groupby(["groupe", "civil"])["d"].transform("median")  # moins la médiane du groupe
    t["s"] = t["d_corrige"].clip(PERS_BAS, PERS_HAUT) / PERS_HAUT              # de -3 à +1
    # q = rang de la période depuis la plus récente de la société (1 = la plus récente), nb au plus
    t = t.sort_values(["cik", "fin"], ascending=[True, False])                # plus récente d'abord
    plus_recent = t.groupby("cik")["fin"].transform("max")                    # dernière période de chaque société
    t["q"] = ((plus_recent - t["fin"]).dt.days / jours_periode).round().astype(int) + 1  # 1, 2, 3...
    t = t[t["q"] <= nb]                                                       # nb périodes au plus
    t = t[plus_recent[t.index] >= D - pd.DateOffset(months=MOIS_RECENCE)]     # dernière période récente
    t["w"] = ((t["q"] - 1) // taille_bloc + 1).map(POIDS_PERS)                # poids 5, 4, 3, 2, 1 par bloc
    g = t.assign(ws=t["w"] * t["s"]).groupby("cik")                           # par société
    resultat = g["ws"].sum() / g["w"].sum()                                   # moyenne pondérée
    return resultat.where(g.size() >= minimum)                                # assez de périodes, sinon manquant


def pers(trim, colonne, colonne_4, groupe_de_cik, D, nb=20, minimum=4, jours_periode=91.31, taille_bloc=4,
         frequence_civile="Q", decalage_civil_mois=0, mois_fenetre=None):
    """Régularité de la croissance (conception §4.2). Avec les valeurs par défaut : identique à pers() de la recherche
    (trim a les colonnes cik, fin_trimestre, X, X_q-4). Le site l'appelle avec les paramètres annuels (constantes.py)."""
    mois_fenetre = nb * 3 + 6 if mois_fenetre is None else mois_fenetre       # recherche : 20 trimestres + 6 mois
    table = trim.rename(columns={"fin_trimestre": "fin"})                     # nom de colonne commun
    t = croissances_pers(table, colonne, colonne_4, D, mois_fenetre)          # étape par société
    return pers_depuis_croissances(t, groupe_de_cik, D, nb, minimum, jours_periode, taille_bloc, frequence_civile,
                                   decalage_civil_mois)                       # étape par groupe


def croissances_gs(exo, colonne, me_de_cik, D, nb):
    """Première moitié de gs_lsv() de la recherche : croissance g de chaque exercice j et clé de classement des bases
    négatives (variation / capitalisation). exo : une ligne par (cik, fy_fin). Renvoie (cik, j, g, cle_ckl)."""
    e = exo[exo["fy_fin"] < D].dropna(subset=[colonne]).sort_values("fy_fin")  # exercices connus, série présente
    e = e[e["fy_fin"] >= D - pd.DateOffset(years=nb + 2)]                     # exercices récents seulement
    e["prec"] = e.groupby("cik")[colonne].shift(1)                            # exercice précédent de la même société
    e["j"] = e.groupby("cik").cumcount(ascending=False) + 1                   # 1 = dernier exercice connu
    e = e[(e["j"] <= nb) & e["prec"].notna()].copy()                          # nb croissances au plus
    e["me"] = e["cik"].map(me_de_cik)                                         # capitalisation de la société
    e["g"] = (e[colonne] / e["prec"] - 1).where(e["prec"] > 0)                # croissance simple si la base est positive
    e["cle_ckl"] = (e[colonne] - e["prec"]) / e["me"]                         # variation rapportée à la capitalisation
    return e[["cik", "j", "g", "cle_ckl"]]


def gs_depuis_croissances(e, groupe_de_cik, minimum):
    """Seconde moitié de gs_lsv() de la recherche : bases négatives remplacées par la moyenne des deux voisins,
    centile dans le groupe pour chaque j, moyenne pondérée par (6 - j), au moins `minimum` exercices."""
    e = e.reset_index(drop=True)                                              # lignes numérotées 0, 1, 2... (sans doublon)
    e["groupe"] = e["cik"].map(groupe_de_cik)                                 # groupe de la société
    e = e.dropna(subset=["groupe"])                                           # société sans groupe : ignorée
    morceaux = []
    for _, x in e.groupby(["groupe", "j"]):                                   # un groupe et un exercice j à la fois
        x = x.sort_values("cle_ckl")                                          # classés par variation / capitalisation
        voisin_avant, voisin_apres = x["g"].ffill().shift(1), x["g"].bfill().shift(-1)  # croissances des voisins
        x["g"] = x["g"].fillna(pd.concat([voisin_avant, voisin_apres], axis=1).mean(axis=1))  # base <= 0 : moyenne
        x["p"] = x["g"].rank(pct=True)                                        # centile dans le groupe
        morceaux.append(x)
    if not morceaux:                                                          # aucune donnée : série vide
        return pd.Series(dtype=float)
    e = pd.concat(morceaux)                                                   # tous les morceaux réunis
    e["w"] = 6 - e["j"]                                                       # poids 5, 4, 3...
    g = e.dropna(subset=["p"]).assign(wp=lambda d: d["w"] * d["p"]).groupby("cik")  # par société
    return (g["wp"].sum() / g["w"].sum()).where(g.size() >= minimum)          # moyenne pondérée, assez d'exercices


def gs_lsv(exo, colonne, me_de_cik, groupe_de_cik, D, nb=5, minimum=2):
    """Croissance lissée (variante V10). Avec les valeurs par défaut : identique à gs_lsv() de la recherche."""
    e = croissances_gs(exo, colonne, me_de_cik, D, nb)                        # étape par société
    return gs_depuis_croissances(e, groupe_de_cik, minimum)                   # étape par groupe


# --- 3. Normalisation (conception §3), copies de la recherche --------------------------------------------------------
def winsoriser(y):
    """Plafonne aux 5e et 95e centiles de l'échantillon (MSCI 2013 p. 4)."""
    if y.notna().sum() == 0:                                                  # aucune valeur : rien à faire
        return y
    return y.clip(y.quantile(0.05), y.quantile(0.95))                         # ramène les extrêmes aux centiles


def moyenne_sans_soi(y, cle, minimum, positifs=False):
    """Moyenne des pairs de la même clé (secteur), titre exclu ; si moins de `minimum` pairs, celle du groupe."""
    v = y.where(y > 0) if positifs else y                                     # (valeurs positives seulement si demandé)
    present = v.notna().astype(float)                                         # 1 si la valeur existe, 0 sinon
    somme_c = v.fillna(0.0).groupby(cle).transform("sum")                     # somme du secteur
    n_c = present.groupby(cle).transform("sum")                               # nombre de valeurs du secteur
    somme_g, n_g = v.fillna(0.0).sum(), present.sum()                         # somme et nombre du groupe
    propre, propre_n = v.fillna(0.0), present                                 # le titre lui-même, à retirer
    moy_c = (somme_c - propre) / (n_c - propre_n)                             # moyenne du secteur sans le titre
    moy_g = (somme_g - propre) / (n_g - propre_n)                             # moyenne du groupe sans le titre
    return moy_c.where(n_c - propre_n >= minimum, moy_g)                      # secteur si assez de pairs, sinon groupe


def ecart_secteur(y, cle, minimum=8):
    """x = y - moyenne des pairs du secteur (titre exclu), au moins 8 autres valeurs, sinon le groupe."""
    return y - moyenne_sans_soi(y, cle, minimum)


def rapport_pairs(y, cle, minimum=5):
    """d = y / ȳ+ - 1 (valorisation ; poids nul dans C8, gardée pour que noter_ratio reste identique)."""
    ref = moyenne_sans_soi(y, cle, minimum, positifs=True)
    return (y / ref - 1).where(ref > 0)


def note(x):
    """Rang moyen r parmi les n valeurs valides, p = (r - 0,5) / n, note = 100 x min(1, max(0, (p - 0,05) / 0,90))."""
    n = x.notna().sum()                                                       # nombre de valeurs
    if n == 0:                                                                # aucune valeur : rien
        return x
    p = (x.rank(method="average") - 0.5) / n                                  # centile (ex aequo : rang moyen)
    return 100 * ((p - 0.05) / 0.90).clip(0, 1)                               # de 0 à 100


def noter_ratio(y, sens, cle=None, mode="absolu"):
    """Chaîne complète pour un ratio dans UN groupe à UNE date (conception §3, étapes 1 à 6).
    sens = +1 si plus haut = mieux, -1 sinon ; mode = 'absolu', 'secteur' (Q) ou 'valorisation' (V)."""
    y = winsoriser(y * sens)                                                  # étapes 1 et 2 : orienter, winsoriser
    if mode == "secteur":
        y = ecart_secteur(y, cle)                                             # étape 3 : écart au secteur
    elif mode == "valorisation":
        y = rapport_pairs(y, cle)                                             # étape 4 (non utilisée par C8)
    return note(y)                                                            # étapes 5 et 6 : rang, note


def composer(notes, minimum, poids=None):
    """Composante à plusieurs ratios : moyenne des notes disponibles (au moins `minimum`), re-notée."""
    if poids is not None:                                                     # poids internes (non utilisés par C8)
        garder = [i for i, w in enumerate(poids) if w > 0]
        if not garder:
            return pd.Series(np.nan, index=notes.index)
        notes, poids = notes.iloc[:, garder], np.array([poids[i] for i in garder], dtype=float)
    nb = notes.notna().sum(axis=1)                                            # nombre de notes présentes par titre
    if poids is None:
        moyenne = notes.mean(axis=1)                                          # moyenne simple des notes présentes
    else:
        w = notes.notna() * poids
        moyenne = (notes.fillna(0.0) * poids).sum(axis=1) / w.sum(axis=1).replace(0, np.nan)
    return note(moyenne.where(nb >= min(minimum, notes.shape[1])))            # re-notée, si assez de notes
