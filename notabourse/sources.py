"""Téléchargement des données : Yahoo Finance (bibliothèque yfinance) et SEC (code SIC).

Aucun calcul de note ici : ce fichier ne fait que lire les données brutes d'UNE société à la fois, avec des
reprises automatiques si Yahoo refuse temporairement (trop de requêtes). Les données brutes ne sont jamais
enregistrées dans le dépôt public (règle de Mathys : aucune donnée brute téléchargeable en masse).

En-tête SEC : la SEC demande à chaque programme de s'identifier (« Nom contact@exemple.com »). Cette valeur est un
secret : elle est lue dans la variable d'environnement SEC_USER_AGENT ou dans les secrets de Streamlit, jamais écrite
dans le code.
"""
import os    # variables d'environnement
import time  # pauses entre deux essais

import pandas as pd  # tableaux de données
import requests      # requêtes web (SEC)
import yfinance as yf  # données de Yahoo Finance

ESSAIS = 3                      # nombre d'essais avant d'abandonner [P]
PAUSES = [5, 20, 60]            # secondes d'attente avant le 2e, le 3e essai... [P]
DEVISES_CENTIMES = {"GBp": "GBP", "GBX": "GBP", "ZAc": "ZAR", "ILA": "ILS"}   # cours en centimes -> devise principale


class DonneesIndisponibles(Exception):
    """Erreur claire quand Yahoo ou la SEC ne répondent pas (affichée telle quelle sur le site)."""


def avec_reprises(fonction, *args, **kwargs):
    """Appelle fonction(*args) ; en cas d'erreur (blocage temporaire, réseau), réessaie après une pause."""
    derniere = None
    for essai in range(ESSAIS):                                               # 0, 1, 2
        try:
            return fonction(*args, **kwargs)                                  # réussite : on renvoie le résultat
        except Exception as erreur:                                           # échec : on garde l'erreur
            derniere = erreur
            if essai < ESSAIS - 1:
                time.sleep(PAUSES[essai])                                     # attendre avant de réessayer
    raise DonneesIndisponibles(f"Source indisponible après {ESSAIS} essais : {derniere}")


# --- SEC -------------------------------------------------------------------------------------------------------------
def en_tete_sec():
    """En-tête d'identification demandé par la SEC, lu dans l'environnement ou dans les secrets de Streamlit."""
    valeur = os.environ.get("SEC_USER_AGENT")                                 # 1. variable d'environnement (robot GitHub)
    if not valeur:
        try:
            import streamlit as st                                            # 2. secrets de Streamlit (site)
            valeur = st.secrets.get("SEC_USER_AGENT")
        except Exception:                                                     # pas de Streamlit ou pas de secrets
            valeur = None
    return {"User-Agent": valeur or "NotaBourse (site de Mathys Blot)"}       # valeur par défaut : sans contact


def sic_par_cik(cik):
    """Code SIC et nom d'une société déposant à la SEC, d'après son numéro CIK. None si la SEC ne la connaît pas."""
    url = f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json"         # fiche de la société chez la SEC
    rep = avec_reprises(requests.get, url, headers=en_tete_sec(), timeout=20)
    if rep.status_code == 404:                                                # société inconnue
        return None
    rep.raise_for_status()                                                    # autre erreur : exception
    fiche = rep.json()
    sic = fiche.get("sic")
    return {"sic": int(sic) if sic not in (None, "") else None, "nom_sec": fiche.get("name")}


def depots_sec(cik):
    """Index des rapports périodiques déposés à la SEC (10-K, 10-Q, 20-F...) : période couverte et date de dépôt.
    Métadonnées seulement (aucun chiffre des comptes) ; sert au calcul daté du test d'acceptation."""
    url = f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json"
    rep = avec_reprises(requests.get, url, headers=en_tete_sec(), timeout=20)
    rep.raise_for_status()
    recents = rep.json().get("filings", {}).get("recent", {})                 # les ~1 000 derniers dépôts
    t = pd.DataFrame({"forme": recents.get("form", []), "depot": recents.get("filingDate", []),
                      "periode": recents.get("reportDate", [])})
    t = t[t["forme"].isin(["10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-QT", "20-F", "20-F/A", "40-F"])]
    t["depot"] = pd.to_datetime(t["depot"], errors="coerce")                  # date de dépôt
    t["periode"] = pd.to_datetime(t["periode"], errors="coerce")              # fin de la période du rapport
    return t.dropna(subset=["depot", "periode"]).reset_index(drop=True)


def table_cik_sec():
    """Table « symbole -> CIK » de toutes les sociétés de la SEC (exige un en-tête SEC avec un contact)."""
    rep = avec_reprises(requests.get, "https://www.sec.gov/files/company_tickers.json", headers=en_tete_sec(), timeout=30)
    rep.raise_for_status()
    lignes = rep.json().values()                                              # {"0": {"cik_str":..., "ticker":...}, ...}
    return {l["ticker"].upper(): int(l["cik_str"]) for l in lignes}


def symbole_sec(symbole_yahoo):
    """Symbole Yahoo -> symbole SEC (BRK-B -> BRK-B ; une cotation étrangère, avec un point, n'est pas à la SEC)."""
    if "." in symbole_yahoo or "=" in symbole_yahoo or symbole_yahoo.startswith("^"):
        return None                                                           # MC.PA, 7203.T... : pas de SIC
    return symbole_yahoo.upper()


# --- Yahoo -----------------------------------------------------------------------------------------------------------
def _sans_fuseau(index):
    """Dates sans fuseau horaire et sans heure (Yahoo donne l'heure de la bourse)."""
    index = pd.DatetimeIndex(index)
    if index.tz is not None:
        index = index.tz_localize(None)                                       # retire le fuseau, garde la date locale
    return index.normalize()                                                  # minuit


def historique(symbole, debut):
    """Cours quotidiens depuis `debut` : date, close (non ajusté), adj_close (ajusté des dividendes et divisions)."""
    h = avec_reprises(lambda: yf.Ticker(symbole).history(start=debut, auto_adjust=False))
    if h is None or h.empty:
        return pd.DataFrame(columns=["date", "close", "adj_close"])
    h.index = _sans_fuseau(h.index)
    return pd.DataFrame({"date": h.index, "close": h["Close"].values, "adj_close": h["Adj Close"].values})


def taux_en_dollars(devise, debut):
    """Valeur d'une unité de `devise` en dollars, jour par jour (série indexée par date). Dollar : None."""
    if devise in (None, "USD"):
        return None
    h = historique(f"{devise}USD=X", debut)                                   # par exemple EURUSD=X
    if h.empty:
        raise DonneesIndisponibles(f"Taux de change {devise} -> USD introuvable")
    return h.set_index("date")["close"]


def marche_sp500tr(debut):
    """S&P 500 dividendes réinvestis (^SP500TR), clôtures quotidiennes indexées par date."""
    h = historique("^SP500TR", debut)
    if h.empty:
        raise DonneesIndisponibles("Indice ^SP500TR introuvable")
    return h.set_index("date")["close"]


def comptes(symbole):
    """Fiche et états financiers d'une société chez Yahoo. Renvoie un dict :
    info (fiche), et six tableaux (lignes = postes, colonnes = fins de période) : resultat, bilan, flux (annuels),
    resultat_t, bilan_t, flux_t (trimestriels ou semestriels)."""
    t = yf.Ticker(symbole)

    def lire():
        return {"info": t.info, "resultat": t.income_stmt, "bilan": t.balance_sheet, "flux": t.cashflow,
                "resultat_t": t.quarterly_income_stmt, "bilan_t": t.quarterly_balance_sheet,
                "flux_t": t.quarterly_cashflow}

    d = avec_reprises(lire)
    if not d["info"] or d["info"].get("quoteType") not in ("EQUITY", None):
        raise DonneesIndisponibles(f"{symbole} n'est pas une action")
    for k in ["resultat", "bilan", "flux", "resultat_t", "bilan_t", "flux_t"]:
        df = d[k] if d[k] is not None else pd.DataFrame()
        if len(df.columns):
            df.columns = _sans_fuseau(df.columns)                             # fins de période en dates simples
            df = df.loc[:, ~df.columns.duplicated()]                          # une colonne par date
            df = df.reindex(sorted(df.columns, reverse=True), axis=1)         # plus récente d'abord
        d[k] = df
    return d


def rechercher(texte, nombre=8):
    """Cotations proposées par Yahoo pour un nom ou un symbole : liste de dict (symbole, nom, bourse, type)."""
    s = avec_reprises(yf.Search, texte, max_results=nombre, news_count=0)
    return [{"symbole": q.get("symbol"), "nom": q.get("longname") or q.get("shortname"), "bourse": q.get("exchDisp"),
             "code_bourse": q.get("exchange"), "type": q.get("quoteType")} for q in s.quotes]
