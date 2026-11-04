"""Essai du classement mondial (04/11/2026) : combien de sociétés hors S&P 500 Yahoo laisse-t-il noter par heure ?

Lancé par le robot d'essai de GitHub (.github/workflows/essai_classement.yml), ou à la main :
    python reference/essai_classement.py
Ce script ne publie rien et n'écrit rien dans le dépôt : il affiche un bilan (vitesse, arrêts, part des sociétés notées).

Déroulé :
  1. liste des sociétés : filtre d'actions de Yahoo, 15 pays, bourse principale seulement, sans les membres du S&P 500,
     sans les certificats brésiliens, une seule cotation par nom de société ;
  2. calcul de la note de chaque société avec le calcul du site (notabourse/calcul.py, formule inchangée), 4 à la fois ;
  3. si Yahoo renvoie trop d'erreurs (5 sur les 20 derniers calculs), tout s'arrête 5 minutes, puis reprend ;
  4. arrêt au bout de DUREE_MINUTES (45 par défaut) ; bilan à l'écran et sur la page du robot.
Rythme mesuré sur le PC de Mathys le 03/11/2026 : environ 2 500 sociétés par heure (resultats/classement_mondial_essais.md
du dépôt de recherche). Cet essai mesure le même rythme depuis les ordinateurs de GitHub.
"""
import collections   # fenêtre glissante des derniers résultats
import os            # variables d'environnement (durée, page de bilan de GitHub)
import queue         # file d'attente partagée entre les calculs
import random        # mélange de la liste
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
from notabourse.sources import marche_sp500tr, table_cik_sec    # noqa: E402  S&P 500 TR, table des symboles SEC

DUREE_MINUTES = float(os.environ.get("DUREE_MINUTES", "45"))                  # durée de l'essai
NOMBRE_MAX = int(os.environ.get("NOMBRE_MAX", "100000"))                      # plafond de sociétés (test rapide)
SIMULTANES = 4            # 4 calculs à la fois : meilleur rythme mesuré le 03/11/2026 [T]
FENETRE, SEUIL = 20, 5    # 5 signes de blocage sur les 20 derniers calculs -> arrêt [T]
ARRET = 300               # durée d'un arrêt, en secondes [T]
PAGES = 4                 # 4 pages de 250 par pays : les 1 000 plus grosses cotations
# Bourse principale de chaque pays (codes de Yahoo) : on écarte les cotations secondaires et les produits structurés
BOURSES = {"us": {"NMS", "NYQ", "NGM", "NCM", "ASE"}, "fr": {"PAR"}, "de": {"GER"}, "gb": {"LSE"}, "jp": {"JPX"},
           "ca": {"TOR"}, "ch": {"EBS"}, "in": {"NSI"}, "kr": {"KSC", "KOE"}, "au": {"ASX"}, "br": {"SAO"},
           "nl": {"AMS"}, "se": {"STO"}, "it": {"MIL"}, "hk": {"HKG"}}
verrou = threading.Lock()  # un seul calcul à la fois modifie les compteurs


def cle_nom(nom):
    """Nom simplifié pour repérer une même société cotée deux fois : « ASML Holding N.V. » -> « asml »."""
    nom = re.sub(r"\b(inc|corp|corporation|plc|ltd|limited|sa|se|nv|ag|co|company|holdings?|group|the)\b", "",
                 str(nom).lower())                                            # mots juridiques retirés
    return re.sub(r"[^a-z0-9]", "", nom)                                      # lettres et chiffres seulement


def liste_societes():
    """Liste des sociétés à noter (une ligne par société), dans un ordre mélangé."""
    membres = pd.read_parquet(SITE / "reference" / "reference.parquet")       # membres du S&P 500
    deja = set(membres["ticker"]) | set(membres["nom"].map(cle_nom))          # leurs symboles et leurs noms
    lignes, vus = [], set()
    for pays, bourses in BOURSES.items():
        for page in range(PAGES):
            r = yf.screen(yf.EquityQuery("eq", ["region", pays]), offset=page * 250, size=250,
                          sortField="intradaymarketcap", sortAsc=False)     # 250 cotations, les plus grosses d'abord
            for x in r["quotes"]:
                nom = x.get("longName")
                cle = cle_nom(nom)
                garder = (x.get("quoteType") == "EQUITY" and x.get("exchange") in bourses and nom
                          and not re.search(r"3[45]\.SA$", x["symbol"])       # pas de certificat brésilien
                          and "-P" not in x["symbol"]                         # pas d'action de préférence
                          and x["symbol"] not in deja and cle not in deja and cle not in vus)
                if garder:
                    vus.add(cle)                                              # une seule cotation par société
                    lignes.append({"pays": pays, "symbole": x["symbol"], "nom": nom})
            time.sleep(0.5)                                                   # petite pause entre deux pages
    random.seed(4112026)                                                      # mélange reproductible
    random.shuffle(lignes)
    return lignes[:NOMBRE_MAX]


def main():
    debut = time.time()
    societes = liste_societes()
    print(f"liste : {len(societes)} sociétés distinctes hors S&P 500 en {time.time() - debut:.0f} s", flush=True)

    # Données communes, lues une seule fois pour toutes les sociétés
    D = pd.Timestamp.today().normalize()                                      # date du calcul
    marche = marche_sp500tr((D - pd.DateOffset(years=calcul.ANS_DE_COURS)).strftime("%Y-%m-%d"))
    table_cik, correspondance = table_cik_sec(), charger_correspondance_yahoo()
    ref, croissances_ref = calcul.charger_reference()
    calcul.taux_en_dollars = lru_cache(maxsize=None)(calcul.taux_en_dollars)  # un taux par devise, pas par société

    # Espion : les cours de la dernière société lue par CE calcul étaient-ils vides ? (signe de blocage)
    local = threading.local()
    historique_origine = calcul.historique

    def historique_espion(symbole, date_debut):
        h = historique_origine(symbole, date_debut)
        local.cours_vides = h.empty
        return h

    calcul.historique = historique_espion

    file = queue.Queue()                                                      # sociétés qui restent à lire
    for s in societes:
        file.put(s)
    derniers = collections.deque(maxlen=FENETRE)                              # vrai = signe de blocage
    etat = {"reprise": 0.0, "arrets": 0, "faits": 0, "debut": time.time()}
    resultats = []                                                            # une ligne par société

    def une_societe(x):
        """Calcule la note d'une société. Renvoie (statut, signe de blocage)."""
        local.cours_vides = False
        try:
            ligne, c = calcul.ratios_et_croissances(x["symbole"], D, "direct", table_cik=table_cik,
                                                    correspondance=correspondance, marche=marche)
        except Exception:
            return "erreur", True                                             # Yahoo n'a pas répondu
        if local.cours_vides:
            return "cours vides", True                                        # sans doute un blocage
        if ligne["groupe"] is None:
            return "non classée", False                                       # fonds, société d'investissement...
        notes = calcul.noter_hors_indice(ligne, c, ref, croissances_ref).get("notes", {})
        return ("notée" if pd.notna(notes.get("note_sur_100")) else "pas de note"), False

    def calculateur():
        """Prend des sociétés dans la file jusqu'à la fin du temps ou de la liste."""
        while time.time() - etat["debut"] < DUREE_MINUTES * 60:
            attente = etat["reprise"] - time.time()
            if attente > 0:                                                   # arrêt en cours : on attend
                time.sleep(attente)
            try:
                x = file.get_nowait()
            except queue.Empty:
                return                                                        # liste finie
            statut, signe = une_societe(x)
            message = None
            with verrou:
                derniers.append(signe)
                resultats.append({**x, "statut": statut})
                etat["faits"] += 1
                if sum(derniers) >= SEUIL and time.time() >= etat["reprise"]:
                    etat["reprise"] = time.time() + ARRET                     # tout le monde s'arrête 5 minutes
                    etat["arrets"] += 1
                    derniers.clear()
                    message = f"arrêt n° {etat['arrets']} (5 min) après {etat['faits']} sociétés"
                elif etat["faits"] % 250 == 0:
                    minutes = (time.time() - etat["debut"]) / 60
                    message = f"{etat['faits']} sociétés en {minutes:.0f} min ({etat['faits'] / minutes:.0f} par minute)"
            if message:
                print(time.strftime("%H:%M:%S ") + message, flush=True)

    fils = [threading.Thread(target=calculateur) for _ in range(SIMULTANES)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()

    # Bilan
    t = pd.DataFrame(resultats)
    minutes = (time.time() - etat["debut"]) / 60
    parts = t["statut"].value_counts(normalize=True) if len(t) else pd.Series(dtype=float)
    bilan = (f"## Essai du classement mondial\n\n"
             f"| Mesure | Valeur |\n|---|---|\n"
             f"| Sociétés dans la liste | {len(societes)} |\n"
             f"| Sociétés lues | {len(t)} en {minutes:.0f} min |\n"
             f"| Rythme, arrêts compris | **{len(t) / minutes:.0f} par minute, soit {len(t) / minutes * 60:.0f} par heure** |\n"
             f"| Arrêts de 5 min (Yahoo ralentit) | {etat['arrets']} |\n"
             + "".join(f"| Part « {k} » | {v:.0%} |\n" for k, v in parts.items()))
    print(bilan, flush=True)
    page = os.environ.get("GITHUB_STEP_SUMMARY")                              # page de bilan du robot GitHub
    if page:
        with open(page, "a", encoding="utf-8") as f:
            f.write(bilan)


if __name__ == "__main__":
    main()
