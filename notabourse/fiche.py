"""Assemble tout ce que la fiche d'une société affiche (sans interface, sans calcul de note : la note vient de note.py).

Deux entrées :
  - fiche_membre() : un membre du S&P 500, dont la note est dans la référence de la semaine [M] 19/10/2026 ;
  - fiche_hors_indice() : une autre société, notée contre les membres par calcul.noter_hors_indice().
Les deux renvoient le même dictionnaire, que l'interface (app.py) affiche tel quel.
Détail d'une composante (cahier des charges §4) : ratios bruts, moyenne du secteur parmi les membres, centile dans le
groupe (« mieux que x % des membres de son groupe »).
"""
import numpy as np    # calcul numérique
import pandas as pd   # tableaux de données

from notabourse.constantes import COMPOSANTES_C8, NOMS_COMPOSANTES, ROUGE, VERT
from notabourse.note import etoiles

# Ratios montrés dans « Voir le détail » : (colonne, sens : +1 si plus haut = mieux, format d'affichage)
RATIOS = {
    "Q1": {"NF": [("ROE", +1, "pct")], "REIT": [("ROE", +1, "pct")], "FIN": [("ROA_FIN", +1, "pct")]},
    "R2": {"NF": [("TLMTA", -1, "pct"), ("CASHMTA", +1, "pct"), ("TAILLE", +1, "usd")],
           "REIT": [("TLMTA", -1, "pct"), ("DN_EBITDA", -1, "x"), ("TAILLE", +1, "usd")],
           "FIN": [("E_FP", +1, "pct"), ("TAILLE", +1, "usd")]},
    "M1": {g: [("AVANCE", +1, "pct"), ("ECART_M", -1, "pct")] for g in ("NF", "REIT", "FIN")},   # avance, irrégularité
}
# Croissances annuelles montrées pour la composante Croissance (série des taux g, du plus récent au plus ancien)
SERIES_CROISSANCE = {"NF": ["GS_CA", "GS_EBITDA"], "REIT": ["GS_CA", "PERS_FFOPA"], "FIN": ["GS_REV_FIN"]}


def _avance(df):
    """Avance annuelle moyenne sur le S&P 500 (dynamique) : moyenne hebdomadaire transformée x 52 semaines."""
    return df["m1w1_moyenne"] * 52


def _ecart_m(df):
    """Irrégularité face au S&P 500 (affichage seulement) : écart-type hebdomadaire de l'écart au marché, ramené à
    l'année (x racine de 52). Plus il est bas, plus l'action a suivi sa tendance sans à-coups."""
    return df["m1w1_ecart_type"] * np.sqrt(52)


CALCULEES = {"AVANCE": ("m1w1_moyenne", 52), "ECART_M": ("m1w1_ecart_type", np.sqrt(52))}   # colonne lue, facteur
SERIES_CALCULEES = {"AVANCE": _avance, "ECART_M": _ecart_m}                  # même calcul sur tout un groupe


def _valeur(ligne, col):
    """Valeur d'un ratio pour une ligne (dict ou Series), avec les colonnes calculées AVANCE et ECART_M."""
    if col in CALCULEES:
        source, facteur = CALCULEES[col]                                      # colonne d'origine et facteur
        v = ligne.get(source)
        return None if v is None or pd.isna(v) else float(v) * facteur
    v = ligne.get(col)
    return None if v is None or pd.isna(v) else float(v)


def _centile(valeur, valeurs, sens):
    """Part (de 0 à 100) des valeurs du groupe que la société dépasse, dans le bon sens (ex aequo : moitié)."""
    v = valeurs.dropna() * sens
    if valeur is None or not len(v):
        return None
    x = valeur * sens
    return float(100 * ((v < x).sum() + 0.5 * (v == x).sum()) / len(v))


def _detail(ligne, ref, code):
    """Ratios bruts d'une composante, moyenne du secteur et centile dans le groupe, parmi les membres."""
    groupe = ligne["groupe"]
    cle = "sous_secteur" if groupe == "FIN" else "secteur"                   # financières : sous-secteur
    membres_groupe = ref[ref["groupe"] == groupe]
    membres_secteur = membres_groupe[membres_groupe[cle] == ligne[cle]]
    sortie = []
    for col, sens, fmt in RATIOS[code][groupe]:
        calcul = SERIES_CALCULEES.get(col)                                    # colonne calculée, ou lue telle quelle
        serie_g = calcul(membres_groupe) if calcul else membres_groupe[col]
        serie_s = calcul(membres_secteur) if calcul else membres_secteur[col]
        v = _valeur(ligne, col)
        sortie.append({"ratio": col, "format": fmt, "valeur": v,
                       "moyenne_secteur": float(serie_s.mean()) if serie_s.notna().any() else None,
                       "mediane_secteur": float(serie_s.median()) if serie_s.notna().any() else None,   # phrases simples
                       "nb_secteur": int(serie_s.notna().sum()), "centile": _centile(v, serie_g, sens)})
    return sortie


def _croissances(cr, groupe, cik):
    """Taux de croissance annuels affichés (du plus récent au plus ancien) pour la composante Croissance."""
    sortie = {}
    for serie in SERIES_CROISSANCE[groupe]:
        t = cr.get(serie)
        if t is None or not len(t):
            continue
        t = t[t["cik"] == cik]
        if serie.startswith("GS_"):                                           # taux simples, j = 1 le plus récent
            sortie[serie] = [None if pd.isna(g) else float(g) for g in t.sort_values("j")["g"]]
        else:                                                                 # taux symétriques (FFO par action)
            sortie[serie] = [float(d) for d in t.sort_values("fin", ascending=False)["d"]]
    return sortie


def _garde_fou(groupe, voyants, mesures, exclusion):
    """Voyants (note de -1 à +1, couleur, mesure) et conditions d'exclusion « remplie / non remplie »."""
    couleur = lambda n: None if n is None or pd.isna(n) else ("vert" if n >= VERT else ("orange" if n > ROUGE else "rouge"))
    noms = ["fonds propres / actif"] if groupe == "FIN" else ["trésorerie", "endettement", "intérêts"]
    liste = []
    for nom in noms:
        n = voyants.get(nom)
        n = None if n is None or pd.isna(n) else float(n)
        liste.append({"voyant": nom, "note": n, "couleur": couleur(n), "mesure": mesures.get(nom)})
    moyenne = exclusion.get("garde_fou")
    moyenne = None if moyenne is None or pd.isna(moyenne) else float(moyenne)
    conditions = [{"condition": "garde_fou", "remplie": bool(exclusion.get("garde_fou_ok"))},
                  {"condition": "benefices", "remplie": bool(exclusion.get("benefices_ok")),
                   "donnee_manquante": bool(mesures.get("benefices_inconnus"))},
                  {"condition": "fonds_propres", "remplie": bool(exclusion.get("fonds_propres_ok"))}]
    return {"voyants": liste, "moyenne": moyenne, "couleur": couleur(moyenne), "conditions": conditions,
            "exclue": not bool(exclusion.get("gardee"))}


def _comparaison(note, ligne, ref, cik):
    """Rang parmi les membres du S&P 500, moyenne du secteur, 5 membres du même secteur aux notes les plus proches."""
    notes = ref["note_aff"].dropna()
    autres = notes.drop(index=cik, errors="ignore")
    if note is None:
        return None
    rang = int((autres > note).sum()) + 1                                     # 1 = la meilleure note
    cle = "sous_secteur" if ligne["groupe"] == "FIN" else "secteur"
    secteur = ref[(ref["groupe"] == ligne["groupe"]) & (ref[cle] == ligne[cle]) & ref["note_aff"].notna()]
    secteur = secteur.drop(index=cik, errors="ignore")
    proches = secteur.assign(distance=(secteur["note_aff"] - note).abs()).sort_values("distance").head(5)
    return {"rang": rang, "nb": int(len(autres)) + 1, "moyenne_secteur": float(secteur["note_aff"].mean()) if len(secteur) else None,
            "nb_secteur": int(len(secteur)),
            "proches": [{"symbole": s, "nom": p["nom"], "note": float(p["note_aff"])} for s, p in proches.iterrows()]}


def _assembler(ligne, notes, voyants, mesures, exclusion, ref, cr, membre, date_reference):
    """Dictionnaire commun de la fiche."""
    cik = ligne["cik"]
    note = notes.get("note")
    note = None if note is None or pd.isna(note) else float(round(note))      # note affichée : entier
    comp = []
    for k in COMPOSANTES_C8:
        n = notes.get(k)
        bloc = {"code": k, "nom": NOMS_COMPOSANTES[k], "note": None if n is None or pd.isna(n) else float(n)}
        bloc["croissances" if k == "G1" else "detail"] = (_croissances(cr, ligne["groupe"], cik) if k == "G1"
                                                          else _detail(ligne, ref, k))
        comp.append(bloc)
    nb = sum(c["note"] is not None for c in comp)
    gf = _garde_fou(ligne["groupe"], voyants, mesures, exclusion)
    av = []
    if note is not None and nb < 4:
        av.append("partielle")                                                # [M] « note peu fiable : données manquantes »
    if note is not None and notes.get("regle") == "affichage" and pd.notna(ligne.get("premier_cours")) and \
            pd.Timestamp(ligne["premier_cours"]) > pd.Timestamp(ligne["date"]) - pd.Timedelta(days=365):
        av.append("cotee_recente")
    if gf["exclue"]:
        av.append("exclue")
    return {"symbole": cik, "nom": ligne.get("nom"), "bourse": ligne.get("bourse"), "devise": ligne.get("devise_cours"),
            "groupe": ligne["groupe"], "secteur": ligne["secteur"], "sous_secteur": ligne["sous_secteur"],
            "secteur_yahoo": ligne.get("secteur_yahoo"), "industrie_yahoo": ligne.get("industrie_yahoo"),
            "pays": ligne.get("pays"), "origine_classement": ligne.get("origine_classement"),
            "capitalisation_usd": ligne.get("TAILLE"), "membre": membre,
            "dates": {"exercice": ligne.get("fin_exercice"), "cours": ligne.get("date_cours"), "reference": date_reference},
            "note": {"sur_100": note, "etoiles": etoiles(note), "M": notes.get("M"), "regle": notes.get("regle"),
                     "nb_composantes": nb},
            "avertissements": av, "composantes": comp, "garde_fou": gf,
            "comparaison": _comparaison(note, ligne, ref, cik)}


def fiche_membre(symbole, ref, croissances_ref):
    """Fiche d'un membre du S&P 500, entièrement tirée de la référence de la semaine."""
    m = ref.loc[symbole]
    notes = {k: m[k + "_aff"] for k in COMPOSANTES_C8}
    notes.update({"note": m["note_aff"], "M": m["M_aff"], "regle": m["regle"]})
    voyants = {k: m.get("voyant_" + k) for k in ["trésorerie", "endettement", "intérêts", "fonds propres / actif"]}
    mesures = {"trésorerie": {"annees": m.get("annees_tresorerie"), "flux_positif": bool(m.get("flux_exploitation_positif"))},
               "endettement": {"tlmta": m.get("TLMTA")},
               "intérêts": {"couverture": m.get("couverture_interets"), "sans_interets": bool(m.get("sans_interets")),
                            "ebitda_negatif": bool(m.get("ebitda_negatif_avec_interets"))},
               "fonds propres / actif": {"ratio": m.get("E_FP")},
               "benefices_inconnus": not (bool(m.get("benefice_fy0_connu")) and bool(m.get("benefice_fy1_connu")))}
    exclusion = {k: m.get(k) for k in ["garde_fou", "garde_fou_ok", "benefices_ok", "fonds_propres_ok", "gardee"]}
    return _assembler(m.to_dict(), notes, voyants, mesures, exclusion, ref, croissances_ref, True, m["date"])


def fiche_hors_indice(resultat, croissances, ref):
    """Fiche d'une société hors du S&P 500 : resultat = calcul.noter_hors_indice(), croissances = ses tables."""
    ligne = resultat["ligne"]
    n = resultat.get("notes", {})
    notes = {k: n.get(k) for k in COMPOSANTES_C8}
    regle = "recherche" if pd.notna(resultat.get("notes_recherche", {}).get("note_sur_100")) else (
        "affichage" if pd.notna(n.get("note_sur_100")) else "aucune")
    notes.update({"note": n.get("note_sur_100"), "M": n.get("M"), "regle": regle})
    cfo, cash = ligne.get("CFO_TTM"), ligne.get("CASH")
    ebitda, interets = ligne.get("EBITDA_TTM"), ligne.get("INTERETS_TTM")
    mesures = {"trésorerie": {"annees": cash / -cfo if pd.notna(cfo) and cfo < 0 and pd.notna(cash) else None,
                              "flux_positif": bool(pd.notna(cfo) and cfo >= 0)},
               "endettement": {"tlmta": ligne.get("TLMTA")},
               "intérêts": {"couverture": ebitda / interets if pd.notna(interets) and interets > 0 and pd.notna(ebitda) else None,
                            "sans_interets": bool(pd.notna(interets) and interets <= 0),
                            "ebitda_negatif": bool(pd.notna(ebitda) and ebitda <= 0 and pd.notna(interets) and interets > 0)},
               "fonds propres / actif": {"ratio": ligne.get("E_FP")},
               "benefices_inconnus": bool(pd.isna(ligne.get("NI_FY0")) or pd.isna(ligne.get("NI_FY1")))}
    return _assembler(ligne, notes, resultat["voyants"], mesures, resultat["exclusions"], ref,
                      {**croissances}, False, ref["date"].iloc[0])
