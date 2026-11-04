"""Classement mondial (04/11/2026) : note de toutes les grandes sociétés cotées, pour la page Classement du site.

Lancé chaque nuit par le robot GitHub (.github/workflows/classement_nuit.yml), ou à la main :
    python reference/construire_classement.py                      # une nuit : les sociétés les plus anciennes
    python reference/construire_classement.py --depuis-cache DOSSIER  # remplissage à partir de calculs déjà faits

Principe (essais du 03 et 04/11/2026, Recherche_score/resultats/classement_mondial_essais.md) :
  1. univers : filtre d'actions de Yahoo, 33 pays, bourse principale seulement, capitalisation d'au moins 1 milliard
     de dollars, une seule cotation par société, sans les membres du S&P 500 (ils viennent de la référence) ;
     liste refaite une fois par semaine (univers_classement.csv) ;
  2. chaque nuit, on relit chez Yahoo les sociétés lues il y a le plus longtemps (jamais lues d'abord), 4 à la fois,
     pendant DUREE_MINUTES au plus : chaque société est ainsi relue environ une fois par semaine ;
  3. la note est celle du site, calcul hors indice inchangé (notabourse/calcul.py, formule C8 intouchable) ;
  4. les membres du S&P 500 sont repris tels quels de la référence de la semaine ;
  5. le fichier classement.parquet ne contient que des notes et des rapports, aucun montant brut des comptes.
Le robot range ce fichier dans une « release » GitHub (pas dans l'historique du dépôt, qui grossirait chaque nuit) ;
le site le télécharge de là.
"""
import argparse      # options de la ligne de commande
import collections   # fenêtre glissante des derniers résultats
import os            # variables d'environnement (durée, page de bilan de GitHub)
import pickle        # lecture des calculs déjà faits (option --depuis-cache)
import queue         # file d'attente partagée entre les calculs
import re            # nettoyage des noms de sociétés
import sys           # chemin d'import
import threading     # plusieurs calculs en même temps
import time          # chronomètre et pauses
import warnings      # avertissements sans conséquence masqués
from functools import lru_cache  # garder en mémoire un taux de change déjà lu
from pathlib import Path         # chemins de fichiers

import pandas as pd   # tableaux de données
import yfinance as yf # données de Yahoo Finance

warnings.filterwarnings("ignore")                                             # messages de bibliothèques masqués
SITE = Path(__file__).resolve().parents[1]                                    # dossier du site
sys.path.insert(0, str(SITE))                                                 # pour importer notabourse
import notabourse.calcul as calcul  # noqa: E402  calcul complet d'une société
from notabourse.classement import charger_correspondance_yahoo  # noqa: E402  industrie Yahoo -> groupe
from notabourse.constantes import COMPOSANTES_C8                # noqa: E402  Q1, G1, R2, M1
from notabourse.prix import prix_secteur                        # noqa: E402  prix comparé au secteur
from notabourse.sources import marche_sp500tr, table_cik_sec    # noqa: E402

FICHIER = SITE / "reference" / "classement.parquet"                           # le classement (publié dans la release)
UNIVERS = SITE / "reference" / "univers_classement.csv"                       # liste des sociétés à noter
SEUIL_USD = 1e9           # capitalisation minimale : 1 milliard de dollars [P] 04/11/2026
JOURS_UNIVERS = 7         # la liste est refaite au bout de 7 jours
JOURS_RELECTURE = 6       # une société lue il y a moins de 6 jours n'est pas relue
DUREE_MINUTES = float(os.environ.get("DUREE_MINUTES", "110"))                 # durée d'une nuit de calcul
SIMULTANES = 4            # 4 calculs à la fois [T] 03/11/2026
FENETRE, SEUIL = 20, 5    # 5 signes de blocage sur les 20 derniers calculs -> arrêt de 5 minutes [T]
ARRET = 300               # durée d'un arrêt, en secondes [T]
SAUVEGARDE = 200          # le classement est écrit sur le disque toutes les 200 sociétés lues
RANG_MAX = 9500          # au-delà, le filtre de Yahoo renvoie toujours la même page [T] 03/11/2026
# Bourse principale de chaque pays (codes de Yahoo, relevés le 04/11/2026) : cotations secondaires écartées
BOURSES = {"us": {"NMS", "NYQ", "NGM", "NCM", "ASE"}, "ca": {"TOR"}, "br": {"SAO"}, "mx": {"MEX"}, "ar": {"BUE"},
           "cl": {"SGO"}, "fr": {"PAR"}, "de": {"GER"}, "gb": {"LSE"}, "ch": {"EBS"}, "nl": {"AMS"}, "se": {"STO"},
           "it": {"MIL"}, "es": {"MCE"}, "dk": {"CPH"}, "no": {"OSL"}, "fi": {"HEL"}, "be": {"BRU"}, "at": {"VIE"},
           "pt": {"LIS"}, "ie": {"ISE"}, "pl": {"WSE"}, "gr": {"ATH"}, "tr": {"IST"}, "jp": {"JPX"},
           "kr": {"KSC", "KOE"}, "hk": {"HKG"}, "cn": {"SHH", "SHZ"}, "tw": {"TAI", "TWO"}, "in": {"NSI"},
           "au": {"ASX"}, "nz": {"NZE"}, "sg": {"SES"}, "id": {"JKT"}, "th": {"SET"}, "my": {"KLS"},
           "za": {"JNB"}, "il": {"TLV"}, "sa": {"SAU"}, "qa": {"DOH"}}
CENTIMES = {"GBp": ("GBP", 100), "GBX": ("GBP", 100), "ZAc": ("ZAR", 100), "ILA": ("ILS", 100)}   # cours en centimes
COLONNES = ["symbole", "nom", "pays", "bourse", "groupe", "secteur", "sous_secteur", "note", *COMPOSANTES_C8,
            "nb_composantes", "gardee", "capi_usd", "ratio_prix", "perte", "membre", "statut", "date_lecture",
            "date_essai"]
verrou = threading.Lock()  # un seul calcul à la fois modifie les compteurs


def journal(texte):
    """Message horodaté à l'écran (journal du robot)."""
    print(time.strftime("%H:%M:%S ") + texte, flush=True)


def cle_nom(nom):
    """Nom simplifié pour repérer une même société cotée deux fois : « ASML Holding N.V. » -> « asml »."""
    nom = re.sub(r"[^a-z0-9 ]", "", str(nom).lower().replace("-", " "))      # « N.V. » -> « nv », sans ponctuation
    nom = re.sub(r"\b(inc|corp|corporation|plc|ltd|limited|sa|se|nv|ag|co|company|holdings?|group|the)\b", "", nom)
    return nom.replace(" ", "")                                               # mots juridiques retirés, puis collé


@lru_cache(maxsize=None)
def dollars_par_unite(devise):
    """Combien de dollars vaut 1 unité de la devise (dernier cours connu) ; None si Yahoo ne le donne pas."""
    base, diviseur = CENTIMES.get(devise, (devise, 1))
    if base in (None, "USD"):
        return 1.0 / diviseur
    h = yf.Ticker(f"{base}USD=X").history(period="10d")                       # par exemple EURUSD=X
    return float(h["Close"].dropna().iloc[-1]) / diviseur if len(h) else None


def construire_univers(ref):
    """Liste des sociétés à noter : une ligne par société, la plus grosse cotation gardée en cas de doublon."""
    deja = set(ref["ticker"]) | set(ref["nom"].map(cle_nom))                  # membres du S&P 500 : à part
    lignes = []
    for pays, bourses in BOURSES.items():
        for debut in range(0, RANG_MAX, 250):                                 # pages de 250, les plus grosses d'abord
            r = yf.screen(yf.EquityQuery("eq", ["region", pays]), offset=debut, size=250,
                          sortField="intradaymarketcap", sortAsc=False)
            page = r.get("quotes", [])
            assez_grosse = False                                              # au moins une société au-dessus du seuil ?
            for x in page:
                taux = dollars_par_unite(x.get("currency"))
                capi = x.get("marketCap")
                capi_usd = capi * taux if capi and taux else None
                if capi_usd is None or capi_usd < SEUIL_USD:
                    continue
                assez_grosse = True
                nom = x.get("longName")
                garder = (x.get("quoteType") == "EQUITY" and x.get("exchange") in bourses and nom
                          and not re.search(r"3[2-5]\.SA$", x["symbol"])       # pas de certificat brésilien
                          and "-P" not in x["symbol"]                         # pas d'action de préférence
                          and x["symbol"] not in deja and cle_nom(nom) not in deja)
                if garder:
                    lignes.append({"symbole": x["symbol"], "nom": nom, "pays": pays, "bourse": x.get("exchange"),
                                   "capi_usd": capi_usd, "cle": cle_nom(nom)})
            time.sleep(0.5)                                                   # petite pause entre deux pages
            if not page or not assez_grosse or len(page) < 250:
                break                                                         # plus rien au-dessus du seuil
        journal(f"univers : {pays} lu ({len(lignes)} cotations en tout)")
    u = pd.DataFrame(lignes).sort_values("capi_usd", ascending=False)
    u = u.drop_duplicates("cle").drop_duplicates("symbole").drop(columns="cle")   # une cotation par société
    u["date_univers"] = pd.Timestamp.today().normalize()
    u.to_csv(UNIVERS, index=False)
    journal(f"univers : {len(u)} sociétés distinctes hors S&P 500 d'au moins {SEUIL_USD / 1e9:.0f} Md$")
    return u


def charger_univers(ref):
    """Liste des sociétés : relue sur le disque si elle a moins de 7 jours, refaite sinon."""
    if UNIVERS.exists():
        u = pd.read_csv(UNIVERS, parse_dates=["date_univers"])
        if len(u) and u["date_univers"].iloc[0] > pd.Timestamp.today() - pd.Timedelta(days=JOURS_UNIVERS):
            return u
    return construire_univers(ref)


def ligne_hors_indice(x, ligne, c, ref, cr, date):
    """Ligne du classement pour une société hors S&P 500, à partir de son calcul (ratios et croissances)."""
    s = {"symbole": x["symbole"], "nom": x["nom"], "pays": x["pays"], "bourse": x["bourse"],
         "capi_usd": ligne.get("TAILLE"), "membre": False, "date_lecture": date, "date_essai": date}
    s.update({k: ligne.get(k) for k in ("groupe", "secteur", "sous_secteur")})
    if ligne["groupe"] is None:                                               # fonds, société d'investissement...
        s["statut"] = "non classée"
        return s
    res = calcul.noter_hors_indice(ligne, c, ref, cr)                         # calcul du site, inchangé
    n = res.get("notes", {})
    s.update({k: n.get(k) for k in COMPOSANTES_C8})
    s["note"] = n.get("note_sur_100")
    s["nb_composantes"] = n.get("nb_composantes")
    s["gardee"] = bool(res["exclusions"].get("gardee"))                       # écartée pour risque de faillite ?
    p = prix_secteur(res["ligne"], ref)                                       # prix comparé au secteur (à part)
    s["ratio_prix"], s["perte"] = p["ratio"], bool(p["perte"])
    s["statut"] = "notée" if pd.notna(s["note"]) else "pas de note"
    return s


def lignes_membres(ref):
    """Lignes du classement pour les membres du S&P 500, reprises de la référence de la semaine."""
    sortie = []
    for _, m in ref.iterrows():
        p = prix_secteur(m.to_dict(), ref)
        sortie.append({"symbole": m["ticker"], "nom": m["nom"], "pays": "us", "bourse": m.get("bourse"),
                       "groupe": m["groupe"], "secteur": m["secteur"], "sous_secteur": m["sous_secteur"],
                       "note": m["note_aff"], **{k: m[k + "_aff"] for k in COMPOSANTES_C8},
                       "nb_composantes": m["nb_aff"], "gardee": bool(m["gardee"]), "capi_usd": m["TAILLE"],
                       "ratio_prix": p["ratio"], "perte": bool(p["perte"]), "membre": True,
                       "statut": "notée" if pd.notna(m["note_aff"]) else "pas de note",
                       "date_lecture": pd.Timestamp(m["date"]), "date_essai": pd.Timestamp(m["date"])})
    return sortie


def nuit(univers, anciennes, ref, cr, sauver=None):
    """Relit chez Yahoo les sociétés les plus anciennes, pendant DUREE_MINUTES au plus. Renvoie les nouvelles lignes.
    sauver(nouvelles) : appelée toutes les SAUVEGARDE sociétés, pour qu'un arrêt brutal ne perde presque rien."""
    D = pd.Timestamp.today().normalize()                                      # date du calcul
    vues = anciennes.set_index("symbole") if len(anciennes) else pd.DataFrame()
    lu = univers["symbole"].map(vues["date_lecture"]) if len(vues) else pd.Series(pd.NaT, index=univers.index)
    essai = univers["symbole"].map(vues["date_essai"]) if len(vues) else pd.Series(pd.NaT, index=univers.index)
    a_lire = univers[(lu.isna() | (lu < D - pd.Timedelta(days=JOURS_RELECTURE)))      # vieille de 6 jours ou plus
                     & (essai.isna() | (essai < D))]                          # pas déjà ratée aujourd'hui
    a_lire = a_lire.assign(_lu=lu).sort_values("_lu", na_position="first")    # jamais lues d'abord, puis les plus vieilles
    journal(f"nuit : {len(a_lire)} sociétés à relire, {DUREE_MINUTES:.0f} min au plus")

    marche = marche_sp500tr((D - pd.DateOffset(years=calcul.ANS_DE_COURS)).strftime("%Y-%m-%d"))
    table_cik, correspondance = table_cik_sec(), charger_correspondance_yahoo()
    calcul.taux_en_dollars = lru_cache(maxsize=None)(calcul.taux_en_dollars)  # un taux par devise, pas par société
    local = threading.local()                                                 # espion : cours vides = blocage
    historique_origine = calcul.historique

    def historique_espion(symbole, date_debut):
        h = historique_origine(symbole, date_debut)
        local.cours_vides = h.empty
        return h

    calcul.historique = historique_espion
    file = queue.Queue()
    for x in a_lire.to_dict("records"):
        file.put(x)
    derniers = collections.deque(maxlen=FENETRE)
    etat = {"reprise": 0.0, "arrets": 0, "debut": time.time()}
    nouvelles = []

    def une_societe(x):
        local.cours_vides = False
        try:
            ligne, c = calcul.ratios_et_croissances(x["symbole"], D, "direct", table_cik=table_cik,
                                                    correspondance=correspondance, marche=marche)
        except Exception:
            return None, True                                                 # Yahoo n'a pas répondu
        if local.cours_vides:
            return None, True                                                 # sans doute un blocage
        return ligne_hors_indice(x, ligne, c, ref, cr, D), False

    def calculateur():
        while time.time() - etat["debut"] < DUREE_MINUTES * 60:
            attente = etat["reprise"] - time.time()
            if attente > 0:
                time.sleep(attente)                                           # arrêt en cours
            try:
                x = file.get_nowait()
            except queue.Empty:
                return
            s, signe = une_societe(x)
            message = None
            with verrou:
                derniers.append(signe)
                nouvelles.append(s or {"symbole": x["symbole"], "date_essai": D, "echec": True})
                if sum(derniers) >= SEUIL and time.time() >= etat["reprise"]:
                    etat["reprise"], etat["arrets"] = time.time() + ARRET, etat["arrets"] + 1
                    derniers.clear()
                    message = f"arrêt n° {etat['arrets']} (5 min) après {len(nouvelles)} sociétés"
                elif len(nouvelles) % 250 == 0:
                    message = f"{len(nouvelles)} sociétés en {(time.time() - etat['debut']) / 60:.0f} min"
                if sauver and len(nouvelles) % SAUVEGARDE == 0:
                    sauver(list(nouvelles))                                   # point de reprise sur le disque
            if message:
                journal(message)

    fils = [threading.Thread(target=calculateur) for _ in range(SIMULTANES)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()
    journal(f"nuit : {len(nouvelles)} sociétés lues, {etat['arrets']} arrêt(s)")
    return nouvelles


def depuis_cache(dossier, univers, ref, cr):
    """Lignes calculées à partir de calculs déjà faits (fichiers .pkl : ratios et croissances d'une société)."""
    sortie, par_symbole = [], univers.set_index("symbole")
    for f in sorted(Path(dossier).glob("*.pkl")):
        if f.stem not in par_symbole.index:
            continue                                                          # hors de l'univers : ignorée
        ligne, c = pickle.loads(f.read_bytes())
        x = {"symbole": f.stem, **par_symbole.loc[f.stem, ["nom", "pays", "bourse"]].to_dict()}
        sortie.append(ligne_hors_indice(x, ligne, c, ref, cr, pd.Timestamp(ligne["date"])))
        if len(sortie) % 500 == 0:
            journal(f"cache : {len(sortie)} sociétés notées")
    journal(f"cache : {len(sortie)} sociétés notées en tout")
    return sortie


def assembler(anciennes, nouvelles, membres, univers):
    """Classement final : membres du S&P 500, puis sociétés de l'univers (nouvelle ligne si elle existe, sinon
    l'ancienne ; un échec ne remplace jamais une ligne valable, il note seulement la date de l'essai)."""
    t = anciennes.set_index("symbole") if len(anciennes) else pd.DataFrame(columns=COLONNES).set_index("symbole")
    for s in nouvelles:
        if s.get("echec"):
            if s["symbole"] in t.index:
                t.loc[s["symbole"], "date_essai"] = s["date_essai"]           # ratée : on retentera demain
            else:
                t.loc[s["symbole"], ["date_essai", "statut"]] = [s["date_essai"], "erreur"]
        else:
            t.loc[s["symbole"], [k for k in COLONNES if k != "symbole"]] = [s.get(k) for k in COLONNES[1:]]
    t = t[t.index.isin(univers["symbole"])].reset_index()                     # sociétés sorties de l'univers retirées
    t = pd.concat([pd.DataFrame(membres), t], ignore_index=True)[COLONNES]
    for k in ["note", *COMPOSANTES_C8, "nb_composantes", "capi_usd", "ratio_prix"]:
        t[k] = pd.to_numeric(t[k], errors="coerce")
    for k in ["gardee", "perte", "membre"]:
        t[k] = t[k].astype("boolean")
    for k in ["date_lecture", "date_essai"]:
        t[k] = pd.to_datetime(t[k])
    return t


def main():
    options = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    options.add_argument("--depuis-cache", help="dossier de calculs déjà faits (.pkl)")
    args = options.parse_args()
    ref, cr = calcul.charger_reference()                                      # référence S&P 500 de la semaine
    univers = charger_univers(ref)
    anciennes = pd.read_parquet(FICHIER) if FICHIER.exists() else pd.DataFrame(columns=COLONNES)
    anciennes = anciennes[~anciennes["membre"].fillna(False).astype(bool)] if len(anciennes) else anciennes   # membres : refaits
    membres = lignes_membres(ref)

    def sauver(lignes):
        """Écrit le classement avec les lignes lues jusqu'ici (fichier temporaire, puis remplacement d'un coup)."""
        provisoire = FICHIER.with_suffix(".tmp")
        assembler(anciennes, lignes, membres, univers).to_parquet(provisoire, index=False)
        provisoire.replace(FICHIER)                                           # jamais de fichier à moitié écrit

    nouvelles = (depuis_cache(args.depuis_cache, univers, ref, cr) if args.depuis_cache
                 else nuit(univers, anciennes, ref, cr, sauver))
    sauver(nouvelles)
    t = pd.read_parquet(FICHIER)
    notees = t["note"].notna()
    bilan = (f"## Classement mondial\n\n| Mesure | Valeur |\n|---|---|\n"
             f"| Sociétés de l'univers (hors S&P 500) | {len(univers)} |\n"
             f"| Lignes du classement | {len(t)} (dont {int(t['membre'].sum())} membres du S&P 500) |\n"
             f"| Sociétés notées | {int(notees.sum())} |\n"
             f"| Lues cette fois | {sum(not s.get('echec') for s in nouvelles)} |\n"
             f"| Ratées cette fois | {sum(bool(s.get('echec')) for s in nouvelles)} |\n"
             f"| Jamais lues | {int((~univers['symbole'].isin(t.loc[t['date_lecture'].notna(), 'symbole'])).sum())} |\n")
    print(bilan, flush=True)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(bilan)


if __name__ == "__main__":
    main()
