"""Membres des grands indices mondiaux (06/11/2026) : écrit reference/indices.csv (indice, symbole Yahoo, nom, nom simplifié).

Lancé chaque samedi par le robot GitHub, ou à la main :  python reference/construire_indices.py
Source : Wikipédia, comme la liste du S&P 500 (le site officiel du Nikkei refuse les lectures automatiques).
Si une liste est illisible ou trop courte, l'ancienne est gardée pour cet indice : jamais d'indice vidé par une panne.
Nasdaq-100 et Dow Jones absents : Wikipédia ne donne pas de tableau lisible ; le S&P 500 vient de la référence.
"""
import io        # lire une page web comme un fichier
import re        # extraction des codes
import sys       # chemin d'import
import time      # petite pause entre deux pages
import warnings  # avertissements sans conséquence masqués
from pathlib import Path  # chemins de fichiers

import pandas as pd   # tableaux de données
import requests       # pages Wikipédia

warnings.filterwarnings("ignore")
SITE = Path(__file__).resolve().parents[1]                                    # dossier du site
sys.path.insert(0, str(SITE))
from notabourse.indices import FICHIER, cle_nom  # noqa: E402
from notabourse.sources import en_tete_sec       # noqa: E402

URL = "https://en.wikipedia.org/wiki/"


def tel_quel(s):
    """Symbole déjà au format Yahoo : AC.PA."""
    return s


def chiffres(s):
    """Seulement les chiffres d'un code : « SEHK: 5 » -> « 5 »."""
    return re.sub(r"\D", "", s)


def chine(s):
    """« SSE: 600519 » -> 600519.SS, « SZSE: 300750 » -> 300750.SZ."""
    return chiffres(s).zfill(6) + (".SZ" if "SZ" in s else ".SS")


# Indice -> (page Wikipédia, colonne du symbole, colonne du nom, passage au symbole Yahoo, nombre attendu)
LISTES = {
    "CAC 40": ("CAC_40", "Ticker", "Company", tel_quel, 40),
    "DAX": ("DAX", "Ticker", "Company", tel_quel, 40),
    "FTSE 100": ("FTSE_100_Index", "Ticker", "Company", lambda s: s.rstrip(".").replace(".", "-") + ".L", 100),
    "Euro Stoxx 50": ("EURO_STOXX_50", "Ticker", "Name", tel_quel, 50),
    "SMI": ("Swiss_Market_Index", "Ticker", "Name", lambda s: s + ".SW", 20),
    "AEX": ("AEX_index", "Ticker", "Company", tel_quel, 25),
    "IBEX 35": ("IBEX_35", "Ticker", "Company", tel_quel, 35),
    "FTSE MIB": ("FTSE_MIB", "Ticker", "Company", tel_quel, 40),
    "OMXS30": ("OMX_Stockholm_30", "Ticker", "Company", tel_quel, 30),
    "Hang Seng": ("Hang_Seng_Index", "Ticker", "Name", lambda s: chiffres(s).zfill(4) + ".HK", 80),
    "CSI 300": ("CSI_300_Index", "Ticker", "Company", chine, 300),
    "KOSPI 200": ("KOSPI_200", "Symbol", "Company", lambda s: chiffres(s).zfill(6) + ".KS", 200),
    "Nifty 50": ("NIFTY_50", "Symbol", "Company name", lambda s: s + ".NS", 50),
    "S&P/ASX 50": ("S%26P/ASX_50", "Symbol", "Company", lambda s: s + ".AX", 49),
    "S&P/TSX 60": ("S%26P/TSX_60", "Symbol", "Company", lambda s: s.replace(".", "-") + ".TO", 60),
}


def page(nom):
    """Texte d'une page Wikipédia."""
    r = requests.get(URL + nom, headers=en_tete_sec(), timeout=30)
    r.raise_for_status()
    return r.text


def lire_tableau(indice):
    """Membres d'un indice lus dans le tableau de sa page. Renvoie un tableau (indice, symbole, nom)."""
    nom_page, col_symbole, col_nom, vers_yahoo, _ = LISTES[indice]
    tables = pd.read_html(io.StringIO(page(nom_page)), converters={col_symbole: str})
    bonnes = [t for t in tables if col_symbole in t.columns and col_nom in t.columns and len(t) >= 20]
    t = bonnes[0]
    symboles = t[col_symbole].astype(str).str.replace("\xa0", " ").str.strip()
    symboles = symboles[symboles.str.len().between(1, 20) & (symboles != "nan")]
    return pd.DataFrame({"indice": indice, "symbole": symboles.map(vers_yahoo), "nom": t.loc[symboles.index, col_nom]})


def lire_nikkei():
    """Membres du Nikkei 225 : pas de tableau, une liste « Sojitz Corp. (TYO: 2768) » dans la partie Components."""
    texte = page("Nikkei_225")
    debut = texte.find('id="Components"')
    partie = texte[debut:texte.find("<h2", debut + 50)]
    lignes = [re.sub(r"<[^>]+>", "", x).replace("\xa0", " ") for x in re.findall(r"<li[^>]*>(.*?)</li>", partie, re.S)]
    membres = [re.match(r"(.+?)\s*\(TYO:\s*([0-9A-Z]{4})\)", x.strip()) for x in lignes]
    return pd.DataFrame([{"indice": "Nikkei 225", "symbole": m.group(2) + ".T", "nom": m.group(1)} for m in membres if m])


def main():
    ancien = pd.read_csv(FICHIER, dtype=str) if FICHIER.exists() else pd.DataFrame(columns=["indice", "symbole", "nom", "cle"])
    morceaux = []
    for indice, attendu in [("Nikkei 225", 225)] + [(k, v[4]) for k, v in LISTES.items()]:
        try:
            t = lire_nikkei() if indice == "Nikkei 225" else lire_tableau(indice)
            t = t.drop_duplicates("symbole")
            if len(t) < 0.8 * attendu:
                raise ValueError(f"{len(t)} membres seulement")
            print(f"{indice} : {len(t)} membres", flush=True)
        except Exception as e:                                                # liste illisible : l'ancienne reste
            t = ancien[ancien["indice"] == indice]
            print(f"{indice} : liste illisible ({str(e)[:60]}), {len(t)} membres repris", flush=True)
        morceaux.append(t)
        time.sleep(0.5)
    sortie = pd.concat(morceaux, ignore_index=True)
    sortie["cle"] = sortie["nom"].map(cle_nom)
    sortie.to_csv(FICHIER, index=False)


if __name__ == "__main__":
    main()
