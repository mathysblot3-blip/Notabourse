"""Calcul complet pour une société : téléchargement, classement, ratios, croissances, garde-fou, note.

Enchaînement (une société à la fois) :
  1. telecharger() : comptes, cours, taux de change, S&P 500 TR (sources.py) ;
  2. classer() : groupe, secteur, sous-secteur (SIC de la SEC, sinon industrie Yahoo) ;
  3. ratios_societe() : ratios et croissances de la société (ratios.py) ;
  4. noter_hors_indice() : croissances et note comparées aux membres du S&P 500 (référence), garde-fou, exclusions.
Les membres du S&P 500 sont notés entre eux par reference/construire_reference.py, avec les mêmes fonctions.
"""
import pandas as pd  # tableaux de données

from notabourse.classement import classer_par_sic, classer_par_yahoo
from notabourse.composantes import gs_depuis_croissances, pers_depuis_croissances
from notabourse.constantes import GS_ANNUEL, PERS_ANNUEL
from notabourse.garde_fou import exclusions, notes_garde_fou
from notabourse.note import note_affichage_hors_indice, note_m_reference
from notabourse.ratios import ratios_societe
from notabourse.sources import (DEVISES_CENTIMES, comptes, depots_sec, historique, marche_sp500tr, sic_par_cik,
                                symbole_sec, taux_en_dollars)

ANS_DE_COURS = 3                                                              # cours lus sur 3 ans (fenêtre de 252 jours + marge)
# Nom de la série calculée -> nom de la colonne de recherche
SERIES_PERS = {"PERS_CA": "PERS_CA", "PERS_EBITDA": "PERS_EBITDA", "PERS_FFOPA": "PERS_FFO", "PERS_REV_FIN": "PERS_REV"}
SERIES_GS = {"GS_CA": "GS_CA", "GS_EBITDA": "GS_EBITDA", "GS_REV_FIN": "GS_REV"}
PARAMS_PERS = {k: v for k, v in PERS_ANNUEL.items() if k != "mois_fenetre"}  # paramètres de l'étape par groupe


def devise_principale(devise):
    """GBp (pence) -> GBP, ZAc -> ZAR, ILA -> ILS ; les autres devises ne changent pas."""
    return DEVISES_CENTIMES.get(devise, devise)


def telecharger(symbole, D, marche=None):
    """Toutes les données Yahoo d'une société pour un calcul à la date D (marche : S&P 500 TR déjà lu, facultatif)."""
    d = comptes(symbole)                                                      # fiche et états financiers
    info = d["info"]
    debut = (D - pd.DateOffset(years=ANS_DE_COURS)).strftime("%Y-%m-%d")      # premier jour de cours lu
    d["cours"] = historique(symbole, debut)                                   # cours quotidiens
    devise_cours = devise_principale(info.get("currency"))
    devise_comptes = info.get("financialCurrency") or devise_cours           # devise des comptes (ADR : différente)
    d["change_cours"] = taux_en_dollars(devise_cours, debut)                  # None si dollar
    d["change_comptes"] = taux_en_dollars(devise_comptes, debut)
    d["marche"] = marche if marche is not None else marche_sp500tr(debut)     # S&P 500 TR
    return d


def classer(symbole, info, cik=None, table_cik=None, correspondance=None):
    """Groupe, secteur, sous-secteur : SIC de la SEC si la société y dépose, sinon industrie Yahoo [M] 19/10/2026.
    cik : numéro SEC s'il est déjà connu (membres : liste de Wikipédia) ; table_cik : table symbole -> CIK de la SEC.
    Renvoie un dict, ou None si la société ne peut pas être classée."""
    if cik is None and table_cik is not None:
        s = symbole_sec(symbole)                                              # symbole au format SEC (ou None)
        cik = table_cik.get(s) if s else None
    if cik is not None:
        fiche = sic_par_cik(cik)                                              # code SIC chez la SEC
        if fiche and fiche["sic"] is not None:
            groupe, secteur, sous_secteur = classer_par_sic(fiche["sic"])
            return {"groupe": groupe, "secteur": secteur, "sous_secteur": sous_secteur, "sic": fiche["sic"],
                    "cik_sec": int(cik), "origine_classement": "SIC de la SEC"}
    y = classer_par_yahoo(info.get("industry"), correspondance)               # repli : industrie Yahoo
    if y is not None:
        return {"groupe": y[0], "secteur": y[1], "sous_secteur": y[2], "sic": None, "cik_sec": None,
                "origine_classement": "industrie Yahoo"}
    return None


def ratios_et_croissances(symbole, D, mode="direct", cik=None, table_cik=None, correspondance=None, marche=None):
    """Étapes 1 à 3 pour une société. Renvoie (ligne, croissances) ; lève DonneesIndisponibles si Yahoo ne répond pas."""
    d = telecharger(symbole, D, marche)
    c = classer(symbole, d["info"], cik, table_cik, correspondance)
    if mode == "daté" and c is not None and c.get("cik_sec"):                 # calcul daté : vraies dates de dépôt SEC
        d["depots"] = depots_sec(c["cik_sec"])
    if c is None:                                                             # impossible de classer : pas de note
        c = {"groupe": None, "secteur": None, "sous_secteur": None, "sic": None, "cik_sec": None,
             "origine_classement": "inconnue"}
    ligne, croissances = ratios_societe(d, (c["groupe"], c["secteur"], c["sous_secteur"]), D, mode)
    ligne.update(c)
    return ligne, croissances


def croissances_groupe(tables, groupe_de_cik, D):
    """Seconde moitié des calculs PERS et GS, pour toutes les sociétés des tables (CHOIX.md §7).
    tables : dict « nom de série -> tableau des croissances de toutes les sociétés ». Renvoie un tableau
    (une ligne par société, colonnes PERS_CA, PERS_EBITDA, PERS_FFO, PERS_REV, GS_CA, GS_EBITDA, GS_REV)."""
    sortie = {}
    for k, nom in SERIES_PERS.items():
        t = tables.get(k)
        sortie[nom] = (pers_depuis_croissances(t, groupe_de_cik, D, **PARAMS_PERS) if t is not None and len(t)
                       else pd.Series(dtype=float))
    for k, nom in SERIES_GS.items():
        t = tables.get(k)
        sortie[nom] = (gs_depuis_croissances(t, groupe_de_cik, GS_ANNUEL["minimum"]) if t is not None and len(t)
                       else pd.Series(dtype=float))
    return pd.DataFrame(sortie)


def noter_hors_indice(ligne, croissances, reference, croissances_reference):
    """Étape 4 pour une société HORS du S&P 500 : ses croissances comme si elle était ajoutée au groupe des membres,
    puis sa note contre les membres (règle d'affichage de Mathys et règle de la recherche), garde-fou, exclusions.
    reference : tableau des membres (ratios, croissances, une même date) ; croissances_reference : leurs tables.
    Renvoie un dict : ligne (ratios), notes (affichage), notes_recherche, voyants, exclusions."""
    cik, D = ligne["cik"], ligne["date"]
    tables = {k: pd.concat([croissances_reference.get(k, pd.DataFrame()), croissances.get(k, pd.DataFrame())])
              for k in set(croissances_reference) | set(croissances)}         # membres + la société
    groupe_de_cik = pd.concat([reference.set_index("cik")["groupe"], pd.Series({cik: ligne["groupe"]})])
    g = croissances_groupe(tables, groupe_de_cik, D)                          # croissances notées dans le groupe
    ext = pd.DataFrame([ligne], index=[cik])                                  # la société, une ligne
    for col in g.columns:
        ext[col] = g[col].get(cik, float("nan"))                              # ses valeurs (celles des membres ne changent pas)
    sortie = {"ligne": ext.iloc[0].to_dict(), "voyants": notes_garde_fou(ext).iloc[0].to_dict(),
              "exclusions": exclusions(ext).iloc[0].to_dict()}
    if ligne["groupe"] is None:                                               # société non classée : pas de note
        return sortie
    sortie["notes"] = note_affichage_hors_indice(ext, reference).iloc[0].to_dict()   # règle d'affichage de Mathys
    sortie["notes_recherche"] = note_m_reference(ext, reference).iloc[0].to_dict()   # règle de la recherche
    return sortie
