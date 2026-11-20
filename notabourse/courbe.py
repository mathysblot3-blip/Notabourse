"""Courbe du cours sur 10 ans, sur la fiche d'une société [M] 20/11/2026.

Affichage seulement : la courbe n'entre pas dans la note (formule C8 inchangée). Une valeur par semaine (environ 520
points), le cours de clôture corrigé des divisions d'actions mais pas des dividendes (« cours seul », choix de Mathys).
Une seule demande à Yahoo, sans nouvel essai : si Yahoo ne répond pas, la fiche s'affiche sans la courbe plutôt que
d'attendre. Aucune donnée n'est enregistrée sur le disque.
Fonctions de préparation sans Streamlit ni réseau : testables avec pytest (tests/test_courbe.py).
"""
import pandas as pd      # tableaux de données
import yfinance as yf    # données de Yahoo Finance

from notabourse.sources import DEVISES_CENTIMES, DonneesIndisponibles, _sans_fuseau

PERIODE = "10y"          # 10 ans
INTERVALLE = "1wk"       # une valeur par semaine : la courbe reste légère et lisible
POINTS_MIN = 8           # moins de 8 semaines de cours : pas de courbe (rien à montrer)


def telecharger_cours(symbole):
    """(table date / cours, devise donnée par Yahoo). Lève DonneesIndisponibles si Yahoo ne répond pas (l'erreur
    n'est pas gardée en mémoire par le site : on réessaiera à la visite suivante)."""
    try:
        t = yf.Ticker(symbole)
        h = t.history(period=PERIODE, interval=INTERVALLE, auto_adjust=False)   # cours non corrigés des dividendes
        devise = (t.history_metadata or {}).get("currency")                    # « USD », « GBp »... (même demande)
    except Exception as erreur:                                               # réseau, blocage de Yahoo...
        raise DonneesIndisponibles(f"Cours sur 10 ans indisponibles : {erreur}") from erreur
    if h is None or h.empty or "Close" not in h:
        return pd.DataFrame(columns=["date", "cours"]), devise                # société sans cours : table vide
    return pd.DataFrame({"date": _sans_fuseau(h.index), "cours": h["Close"].values}), devise


def preparer_courbe(table, devise):
    """Cours rangés par date, sans valeur vide ni nulle, en devise principale (pence -> livres) ; renvoie
    (table, devise affichée), ou (None, devise) s'il y a trop peu de points pour une courbe."""
    t = table.dropna(subset=["cours"])                                        # semaines sans cours retirées
    t = t[t["cours"] > 0].sort_values("date").reset_index(drop=True)          # cours positifs, du plus ancien au récent
    if devise in DEVISES_CENTIMES:                                            # cours en centimes (pence, cents)
        t = t.assign(cours=t["cours"] / 100)                                  # -> unités (livres, rands...)
        devise = DEVISES_CENTIMES[devise]
    if not (isinstance(devise, str) and len(devise) == 3 and devise.isalpha() and devise.isascii()):
        devise = ""                                                           # code de devise inattendu : non affiché
    if len(t) < POINTS_MIN:
        return None, devise
    return t, devise


def resume(table):
    """Chiffres clés de la courbe : premier et dernier cours, variation, plus bas et plus haut, avec leurs dates. Ils
    servent aussi de description du graphique pour les lecteurs d'écran (accessibilité)."""
    premier, dernier = table.iloc[0], table.iloc[-1]                         # plus ancienne et plus récente semaine
    bas, haut = table.loc[table["cours"].idxmin()], table.loc[table["cours"].idxmax()]
    return {"date_debut": premier["date"], "debut": premier["cours"], "date_fin": dernier["date"],
            "fin": dernier["cours"], "variation": dernier["cours"] / premier["cours"] - 1,
            "bas": bas["cours"], "date_bas": bas["date"], "haut": haut["cours"], "date_haut": haut["date"]}


def cotee_recemment(table, aujourd_hui):
    """Vrai si la courbe commence nettement après la date d'il y a 10 ans (société cotée depuis moins longtemps)."""
    return table["date"].iloc[0] > pd.Timestamp(aujourd_hui) - pd.DateOffset(years=10) + pd.DateOffset(weeks=4)
