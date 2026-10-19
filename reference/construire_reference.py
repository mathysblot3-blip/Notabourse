"""Référence S&P 500 : ratios et notes C8 de tous les membres, notés entre eux comme dans la recherche (étape b).

Lancé chaque semaine par GitHub Actions (étape f), ou à la main. Pour chaque membre de la liste Wikipédia
« List of S&P 500 companies » : données Yahoo, classement par le SIC de la SEC, ratios, croissances ; puis, pour tous
ensemble : croissances notées dans le groupe, notes Q, G, R, D, S, M, note sur 100, garde-fou et exclusions.

Sorties (dans reference/, ou dans --sortie) :
  - reference.parquet  : une ligne par membre, RATIOS DÉRIVÉS SEULS (aucune ligne brute de comptes) [M] 19/10/2026 ;
  - croissances.parquet : croissances annuelles des membres (taux, sans montants), pour noter les autres sociétés ;
  - membres_sp500.csv : la liste lue sur Wikipédia ; reference_info.json : date, nombre de membres, reprises.
Règle P6 [P, validée avec le plan] : un membre en échec reprend ses valeurs de la référence précédente (2 semaines au
plus, signalé « reprise ») ; si plus de 10 % des membres restent en échec, rien n'est écrit et le script échoue.

Lancer depuis le dossier site :
  .venv\\Scripts\\python.exe reference\\construire_reference.py                    (calcul du jour, environ 40 minutes)
  .venv\\Scripts\\python.exe reference\\construire_reference.py --date 2026-08-31 --membres liste.csv --sortie dossier
       (calcul daté du test d'acceptation : liste.csv a les colonnes symbole, cik)
Un cache (dossier cache/, ignoré par git) permet de reprendre un calcul interrompu sans tout retélécharger.
"""
import argparse   # options de la ligne de commande
import io         # lire une page web comme un fichier
import json       # petit fichier d'informations
import pickle     # cache des calculs par membre
import sys        # chemin d'import, sortie en erreur
import time       # pauses entre deux membres
import warnings   # avertissements sans conséquence masqués
from pathlib import Path  # chemins de fichiers

import numpy as np    # calcul numérique
import pandas as pd   # tableaux de données
import requests       # page Wikipédia

SITE = Path(__file__).resolve().parents[1]                                    # dossier site
sys.path.insert(0, str(SITE))
from notabourse.calcul import croissances_groupe, ratios_et_croissances  # noqa: E402
from notabourse.garde_fou import exclusions, notes_garde_fou  # noqa: E402
from notabourse.note import note_affichage_membres, noter_membres  # noqa: E402
from notabourse.sources import en_tete_sec, marche_sp500tr  # noqa: E402

warnings.filterwarnings("ignore")
PAUSE = 1.0                         # secondes entre deux membres (ne pas surcharger Yahoo) [P]
ECHEC_MAX = 0.10                    # plus de 10 % d'échecs : la référence n'est pas écrite (P6)
REPRISE_MAX_JOURS = 14              # une valeur reprise a au plus 2 semaines (P6)
URL_WIKIPEDIA = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
# Montants bruts : servent au calcul mais ne sont JAMAIS écrits dans la référence publique [M] 19/10/2026
BRUTS = ["CASH", "CFO_TTM", "EBITDA_TTM", "INTERETS_TTM", "NI_FY0", "NI_FY1", "SE_EXCLUSION", "taux_comptes", "taux_cours"]


def membres_wikipedia():
    """Liste des membres du S&P 500 lue sur Wikipédia : symbole Yahoo, nom, CIK, secteur GICS."""
    rep = requests.get(URL_WIKIPEDIA, headers=en_tete_sec(), timeout=30)     # même en-tête poli que pour la SEC
    rep.raise_for_status()
    t = pd.read_html(io.StringIO(rep.text), attrs={"id": "constituents"})[0]  # tableau « constituents »
    m = pd.DataFrame({"symbole": t["Symbol"].str.replace(".", "-", regex=False),   # BRK.B -> BRK-B (Yahoo)
                      "nom_wikipedia": t["Security"], "cik": t["CIK"].astype(int),
                      "secteur_gics": t["GICS Sector"]})
    # Une ligne par société (CIK), comme la recherche (conception_v2 §2.1) : la première catégorie d'actions listée
    # par Wikipédia (catégorie A : GOOGL, FOXA, NWSA, les mêmes que la recherche au 31/08/2026). Les autres catégories
    # (GOOG, FOX, NWS) renvoient vers elle quand on les cherche sur le site.
    premiere = m.groupby("cik")["symbole"].transform("first")                  # symbole gardé pour chaque CIK
    m["autre_categorie_de"] = premiere.where(premiere != m["symbole"])        # vide pour la ligne gardée
    return m


def calculer_membre(symbole, cik, D, mode, marche, dossier_cache):
    """Ratios et croissances d'un membre, avec cache sur disque. Renvoie (ligne, croissances) ou lève une erreur."""
    fichier = dossier_cache / f"{symbole}.pkl"
    if fichier.exists():                                                      # déjà calculé : on relit
        with open(fichier, "rb") as f:
            return pickle.load(f)
    resultat = ratios_et_croissances(symbole, D, mode, cik=cik, marche=marche)
    if resultat[0]["groupe"] is None:
        raise ValueError("société non classée (SIC introuvable)")
    with open(fichier, "wb") as f:                                            # garde le résultat pour une reprise
        pickle.dump(resultat, f)
    time.sleep(PAUSE)                                                         # pause seulement après un vrai téléchargement
    return resultat


def mesures_garde_fou(t):
    """Mesures dérivées affichées pour chaque voyant (sans montant brut)."""
    m = pd.DataFrame(index=t.index)
    m["annees_tresorerie"] = (t["CASH"] / (-t["CFO_TTM"])).where(t["CFO_TTM"] < 0)   # seulement si le flux est négatif
    m["flux_exploitation_positif"] = t["CFO_TTM"] >= 0
    m["couverture_interets"] = (t["EBITDA_TTM"] / t["INTERETS_TTM"]).where(t["INTERETS_TTM"] > 0)
    m["sans_interets"] = t["INTERETS_TTM"] <= 0
    m["ebitda_negatif_avec_interets"] = (t["EBITDA_TTM"] <= 0) & (t["INTERETS_TTM"] > 0)
    m["benefice_fy0_connu"] = t["NI_FY0"].notna()
    m["benefice_fy1_connu"] = t["NI_FY1"].notna()
    return m


def main():
    p = argparse.ArgumentParser(description="Construit la référence S&P 500 de NotaBourse.")
    p.add_argument("--date", help="date du calcul daté (AAAA-MM-JJ) ; sans elle : calcul du jour")
    p.add_argument("--membres", help="fichier CSV (symbole, cik) à la place de la liste Wikipédia")
    p.add_argument("--sortie", default=str(SITE / "reference"), help="dossier de sortie")
    p.add_argument("--limite", type=int, help="seulement les N premiers membres (essai)")
    a = p.parse_args()
    D = pd.Timestamp(a.date) if a.date else pd.Timestamp.today().normalize()  # date du calcul
    mode = "daté" if a.date else "direct"
    sortie = Path(a.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    dossier_cache = SITE / "cache" / "reference" / f"{D.date()}_{mode}"
    dossier_cache.mkdir(parents=True, exist_ok=True)

    # --- 1. Liste des membres ------------------------------------------------------------------------------------
    membres = pd.read_csv(a.membres) if a.membres else membres_wikipedia()
    if a.limite:
        membres = membres.head(a.limite)
    if not a.membres:
        membres.to_csv(sortie / "membres_sp500.csv", index=False)             # toutes les catégories, avec les renvois
        membres = membres[membres["autre_categorie_de"].isna()]               # une ligne par société pour le calcul
    print(f"Date {D.date()} ({mode}), {len(membres)} membres", flush=True)

    # --- 2. Chaque membre --------------------------------------------------------------------------------------
    marche = marche_sp500tr((D - pd.DateOffset(years=3)).strftime("%Y-%m-%d"))   # S&P 500 TR, lu une fois
    lignes, croissances, echecs = [], {}, {}
    for i, m in enumerate(membres.itertuples(index=False), 1):
        try:
            ligne, cr = calculer_membre(m.symbole, int(m.cik), D, mode, marche, dossier_cache)
            if "nom_wikipedia" in membres.columns and not ligne.get("nom"):
                ligne["nom"] = m.nom_wikipedia
            ligne["statut"], ligne["date_donnees"] = "frais", D
            lignes.append(ligne)
            for k, t in cr.items():
                croissances.setdefault(k, []).append(t)
        except Exception as erreur:                                           # échec : noté, on continue
            echecs[m.symbole] = str(erreur)[:200]
        if i % 25 == 0:
            print(f"  {i}/{len(membres)} membres, {len(echecs)} échecs", flush=True)
    frais = pd.DataFrame(lignes).set_index("cik", drop=False)

    # --- 3. Échecs : reprise de la référence précédente (P6) -----------------------------------------------------
    reprises = pd.DataFrame()
    precedente = sortie / "reference.parquet"
    if echecs and precedente.exists():
        ancienne = pd.read_parquet(precedente).set_index("cik", drop=False)
        recents = ancienne[pd.to_datetime(ancienne["date_donnees"]) >= D - pd.Timedelta(days=REPRISE_MAX_JOURS)]
        reprises = recents[recents.index.isin(list(echecs))].copy()
        reprises["statut"] = "reprise"
        anciennes_cr = pd.read_parquet(sortie / "croissances.parquet")
        for k, t in anciennes_cr[anciennes_cr["cik"].isin(reprises.index)].groupby("serie"):
            croissances.setdefault(k, []).append(t.drop(columns="serie").dropna(axis=1, how="all"))
    restants = [s for s in echecs if s not in reprises.index]
    print(f"Échecs : {len(echecs)} ; repris de la semaine précédente : {len(reprises)} ; sans valeur : {len(restants)}",
          flush=True)
    if len(restants) > ECHEC_MAX * len(membres):                              # trop d'échecs : on n'écrit rien
        print("TROP D'ÉCHECS : référence non écrite. Exemples : " +
              "; ".join(f"{k} ({v})" for k, v in list(echecs.items())[:5]), flush=True)
        sys.exit(1)

    # --- 4. Garde-fou et exclusions (membres frais ; les repris gardent les leurs) -------------------------------
    voy = notes_garde_fou(frais).add_prefix("voyant_")
    exc = exclusions(frais)
    mes = mesures_garde_fou(frais)
    frais = pd.concat([frais.drop(columns=BRUTS, errors="ignore"), voy, exc, mes], axis=1)
    ref = pd.concat([frais, reprises[[c for c in reprises.columns if c in frais.columns]]]) if len(reprises) else frais
    ref["date"] = D                                                           # même date pour tous (calcul de la note)

    # --- 5. Croissances notées dans le groupe, puis notes des membres entre eux ----------------------------------
    tables = {k: pd.concat(v, ignore_index=True) for k, v in croissances.items()}
    g = croissances_groupe(tables, ref["groupe"], D)
    for col in g.columns:
        ref[col] = g[col].reindex(ref.index)
    notes = noter_membres(ref)                                                # calcul de la recherche (10_score.py)
    aff = note_affichage_membres(ref, notes)                                  # règle d'affichage de Mathys
    ref = ref.drop(columns=[c for c in notes.columns if c in ref.columns] + [c for c in aff.columns if c in ref.columns])
    ref = pd.concat([ref, notes, aff], axis=1)

    # --- 6. Écriture ----------------------------------------------------------------------------------------------
    ref = ref.drop(columns=BRUTS, errors="ignore").reset_index(drop=True)      # jamais de montant brut
    ref.to_parquet(sortie / "reference.parquet", index=False)
    longues = []
    for k, t in tables.items():
        t = t[t["cik"].isin(ref["cik"])].copy()
        t["serie"] = k
        longues.append(t)
    pd.concat(longues, ignore_index=True).to_parquet(sortie / "croissances.parquet", index=False)
    info = {"date": str(D.date()), "mode": mode, "membres_liste": int(len(membres)), "membres_notes": int(ref["note_sur_100"].notna().sum()),
            "membres_dans_reference": int(len(ref)), "reprises": int(len(reprises)), "echecs_sans_valeur": restants,
            "echecs": echecs, "groupes": {k: int(v) for k, v in ref["groupe"].value_counts().items()}}
    (sortie / "reference_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Référence écrite : {len(ref)} membres, {info['membres_notes']} notés (règle de la recherche) ; "
          f"groupes {info['groupes']}", flush=True)


if __name__ == "__main__":
    main()
