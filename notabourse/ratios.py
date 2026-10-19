"""Ratios d'UNE société à UNE date, à partir des données Yahoo, avec les définitions de la recherche.

Correspondance des postes Yahoo : CHOIX.md §2 (fixée avant tout calcul). Définitions des ratios : CHOIX.md §3
(Recherche_score/09_composantes.py, 12_variantes.py). Périodes et dollars : CHOIX.md §4 et §5.
Deux modes :
  - « direct » (le site) : D = aujourd'hui, toutes les données publiées par Yahoo ;
  - « daté » (test d'acceptation) : seules les données qui étaient publiées à la date D (délais de 45 et 75 jours).
Les noms de colonnes sont ceux du fichier de ratios de la recherche (ROE, TLMTA, ...), pour réutiliser son calcul.
"""
import numpy as np   # calcul numérique
import pandas as pd  # tableaux de données

from notabourse.composantes import croissances_gs, croissances_pers, dynamique_w1, hebdomadaire
from notabourse.constantes import (DELAI_EXERCICE, DELAI_TRIMESTRE, DN_EBITDA_PIRE, GS_ANNUEL, MOIS_RECENCE,
                                   NB_EXERCICES, PERS_ANNUEL, SEUIL_DETTE_NULLE)
from notabourse.sources import DEVISES_CENTIMES

# --- Postes Yahoo, par ordre de repli (CHOIX.md §2) ------------------------------------------------------------------
P_RESULTAT = {
    "CA": ["Total Revenue", "Operating Revenue"],
    "OI": ["Operating Income"],                          # résultat d'exploitation déjà nettoyé par Yahoo [M] 19/10/2026
    "NI_common": ["Net Income Common Stockholders", "Net Income"],
    "RN_brut": ["Net Income Including Noncontrolling Interests", "Net Income"],
    "DISC": ["Net Income Discontinuous Operations"],
    "INT": ["Interest Expense", "Interest Expense Non Operating"],
    "IMP_res": ["Impairment Of Capital Assets"],
    "DA_res": ["Reconciled Depreciation"],
    "WAD": ["Diluted Average Shares"],
}
P_FLUX = {
    "DA": ["Depreciation And Amortization", "Depreciation Amortization Depletion", "Depreciation"],
    "DEFTAX": ["Deferred Income Tax"],
    "GPINV": ["Gain Loss On Investment Securities"],
    "GC": ["Gain Loss On Sale Of PPE"],
    "IMP": ["Asset Impairment Charge"],
    "CFO": ["Cash Flow From Continuing Operating Activities", "Operating Cash Flow"],
    "INT_PAID": ["Interest Paid Supplemental Data", "Interest Paid Cfo", "Interest Paid Cff"],
}
P_BILAN = {
    "TA": ["Total Assets"],
    "TL": ["Total Liabilities Net Minority Interest"],
    "SE": ["Stockholders Equity"],
    "MINO": ["Minority Interest"],
    "CASH": ["Cash Cash Equivalents And Short Term Investments"],
    "CASH_SEUL": ["Cash And Cash Equivalents"],
    "PCT": ["Other Short Term Investments"],
    "LOC": ["Capital Lease Obligations"],
    "DETTE_TOT": ["Total Debt"],
    "GW": ["Goodwill"],
    "INTANG": ["Other Intangible Assets"],
    "GW_INTANG": ["Goodwill And Other Intangible Assets"],
    "AOCI": ["Gains Losses Not Affecting Retained Earnings"],
}


def poste(df, noms):
    """Série (une valeur par fin de période) du premier poste disponible parmi `noms`, colonne par colonne."""
    s = pd.Series(np.nan, index=df.columns, dtype=float)                      # vide au départ
    for nom in noms:                                                          # dans l'ordre de repli
        if nom in df.index:
            s = s.fillna(pd.to_numeric(df.loc[nom], errors="coerce"))         # complète les cases encore vides
    return s


def publie(df):
    """Vrai pour chaque période où l'état financier contient au moins un chiffre (règle « 0 si absent d'un état publié »)."""
    return df.notna().any(axis=0) if len(df.columns) else pd.Series(dtype=bool)


def zero_si_publie(s, pub):
    """Poste d'événement (dépréciation, plus-value...) : 0 s'il manque dans un état publié (conception_v2 §9)."""
    return s.where(s.notna() | ~pub.reindex(s.index).fillna(False), 0.0)


def flux_par_periode(resultat, flux):
    """Postes de flux et grandeurs composées pour chaque période (colonnes de Yahoo). Renvoie un tableau
    (une ligne par fin de période, de la plus récente à la plus ancienne). Définitions : CHOIX.md §2."""
    resultat = resultat.loc[:, publie(resultat)] if len(resultat.columns) else resultat   # colonnes vides retirées
    flux = flux.loc[:, publie(flux)] if len(flux.columns) else flux
    dates = sorted(set(resultat.columns) | set(flux.columns), reverse=True)  # toutes les fins de période
    if not dates:
        return pd.DataFrame()
    res, flu = resultat.reindex(columns=dates), flux.reindex(columns=dates)   # mêmes colonnes pour les deux états
    pub_r, pub_f = publie(res), publie(flu)                                   # périodes publiées
    t = pd.DataFrame(index=pd.DatetimeIndex(dates, name="fin"))
    for k, noms in P_RESULTAT.items():
        t[k] = poste(res, noms).values
    for k, noms in P_FLUX.items():
        t[k] = poste(flu, noms).values
    pub_r, pub_f = pub_r.reindex(t.index).values, pub_f.reindex(t.index).values
    t["DISC"] = zero_si_publie(t["DISC"], pd.Series(pub_r, index=t.index))   # activités abandonnées : 0 si absent
    t["DEFTAX"] = zero_si_publie(t["DEFTAX"], pd.Series(pub_f, index=t.index))   # impôts différés : 0 si absent
    t["GP_inv"] = zero_si_publie(-t["GPINV"], pd.Series(pub_f, index=t.index))   # plus-values de placements (signe gain)
    t["GC_"] = zero_si_publie(-t["GC"], pd.Series(pub_f, index=t.index))         # plus-values de cession (signe gain)
    imp = t["IMP"].fillna(t["IMP_res"])                                       # dépréciations (flux, sinon résultat)
    t["IMP_"] = zero_si_publie(imp, pd.Series(pub_f | pub_r, index=t.index)).abs()
    t["DA"] = t["DA"].fillna(t["DA_res"]).abs()                               # D&A en valeur absolue
    t["INT_PAID"] = t["INT_PAID"].abs()                                       # intérêts payés (signe variable selon l'état)
    t["INT"] = t["INT"].abs()                                                 # charge d'intérêts (une charge est positive)
    # Grandeurs composées (définitions de la recherche, outils/panel.py)
    t["EBIT_adj"] = t["OI"]                                                   # déjà sans éléments exceptionnels [M] 19/10/2026
    t["EBITDA"] = t["EBIT_adj"] + t["DA"]                                     # D&A absent : EBITDA manquant
    t["E_star"] = t["NI_common"] - t["DISC"] + t["DEFTAX"]                    # E* de Gray-Vogel
    t["RN_conso"] = t["RN_brut"] - t["DISC"]                                  # résultat consolidé des activités poursuivies
    t["NR"] = t["GC_"] + t["GP_inv"] - t["IMP_"]                              # éléments non récurrents (signés comme un gain)
    t["FFO"] = t["RN_conso"] + t["DA"] - t["NR"]                              # FFO des foncières
    t["FFOPA"] = t["FFO"] / t["WAD"].where(t["WAD"] > 0)                      # FFO par action diluée
    t["REV_FIN"] = t["CA"]                                                    # revenus des financières
    return t


def ttm(annuel, trim, colonne, D):
    """Valeur des 12 derniers mois d'une grandeur (CHOIX.md §4). Renvoie (valeur, fin de période, origine).
    4 derniers trimestres s'ils se suivent, contiennent la grandeur et sont postérieurs au dernier exercice ;
    sinon le dernier exercice. Plus de 15 mois depuis la fin de la période : manquant."""
    fy = annuel[colonne].dropna() if len(annuel) else pd.Series(dtype=float)  # exercices où la grandeur existe
    fin_fy = fy.index[0] if len(fy) else None                                 # dernier exercice
    valeur, fin, origine = np.nan, None, None
    if len(trim) >= 4:
        q = trim.iloc[:4]                                                     # 4 trimestres les plus récents
        ecarts = -np.diff(q.index.values).astype("timedelta64[D]").astype(int)  # jours entre deux fins de trimestre
        suivis = bool(((ecarts >= 80) & (ecarts <= 100)).all())               # des trimestres qui se suivent
        if suivis and q[colonne].notna().all() and (fin_fy is None or q.index[0] > fin_fy):
            valeur, fin, origine = float(q[colonne].sum()), q.index[0], "4 trimestres"
    if origine is None and fin_fy is not None:                                # repli : le dernier exercice
        valeur, fin, origine = float(fy.iloc[0]), fin_fy, "exercice"
    if fin is not None and fin < D - pd.DateOffset(months=MOIS_RECENCE):      # données trop anciennes
        return np.nan, fin, "trop ancien"
    return valeur, fin, origine


def dernier_bilan(bilan, bilan_t, D):
    """Postes du bilan le plus récent (trimestriel, semestriel ou annuel). Renvoie (dict des postes, date)."""
    colonnes = {}
    for df in (bilan_t, bilan):                                               # trimestriel d'abord, à date égale
        for c in df.columns:
            if df[c].notna().any():
                colonnes.setdefault(c, []).append(df[c])
    if not colonnes:
        return {}, None
    date = max(colonnes)                                                      # date du bilan le plus récent
    if date < D - pd.DateOffset(months=MOIS_RECENCE):                         # trop ancien : rien
        return {}, date
    tableau = pd.concat(colonnes[date], axis=1)                               # le ou les bilans de cette date
    valeurs = {}
    for k, noms in P_BILAN.items():
        v = np.nan
        for nom in noms:                                                      # ordre de repli
            if nom in tableau.index:
                x = pd.to_numeric(tableau.loc[nom], errors="coerce").dropna()
                if len(x):
                    v = float(x.iloc[0])
                    break
        valeurs[k] = v
    return valeurs, date


def couper(df, limite, depots=None, D=None):
    """Colonnes (fins de période) connues à la date D (calcul daté). Avec l'index des dépôts de la SEC (depots) :
    une période est connue si un rapport sur cette période (à 15 jours près) a été déposé avant D [M] 19/10/2026.
    Sans dépôts SEC : fin de période antérieure ou égale à `limite` (délai de 45 ou 75 jours)."""
    if not len(df.columns):
        return df
    if depots is not None and len(depots):
        avant = depots[depots["depot"] < D]                                   # rapports déposés avant D
        garder = [c for c in df.columns if ((avant["periode"] - c).abs() <= pd.Timedelta(days=15)).any()]
    else:
        garder = [c for c in df.columns if c <= limite]
    return df.loc[:, garder]


def taux_a_la_date(serie, D):
    """Taux de change de la veille de D (dernier connu), 1 pour le dollar."""
    if serie is None:
        return 1.0
    s = serie[serie.index <= D - pd.Timedelta(days=1)].dropna()
    return float(s.iloc[-1]) if len(s) else np.nan


def ratios_societe(d, classement, D, mode="direct"):
    """Ratios de la société décrite par d (sortie de sources.comptes + cours + change) à la date D.

    d : dict avec info, resultat, bilan, flux, resultat_t, bilan_t, flux_t (sources.comptes), cours (sources.historique),
        change_cours, change_comptes (sources.taux_en_dollars, None pour le dollar), marche (sources.marche_sp500tr).
    classement : (groupe, secteur, sous_secteur). mode : « direct » ou « daté ».
    Renvoie (ligne, croissances) : ligne = dict des ratios (noms de la recherche) et des informations affichées ;
    croissances = dict de tableaux (cik, fin, d) pour la régularité et (cik, j, g, cle_ckl) pour le niveau."""
    info = d["info"]
    symbole = info.get("symbol")
    groupe, secteur, sous_secteur = classement
    lim_ex = D - DELAI_EXERCICE if mode == "daté" else D                      # exercices connus à la date
    lim_tr = D - DELAI_TRIMESTRE if mode == "daté" else D                     # trimestres connus à la date
    dep = d.get("depots") if mode == "daté" else None                        # dates de dépôt SEC (calcul daté)
    annuel = flux_par_periode(couper(d["resultat"], lim_ex, dep, D), couper(d["flux"], lim_ex, dep, D))
    trim = flux_par_periode(couper(d["resultat_t"], lim_tr, dep, D), couper(d["flux_t"], lim_tr, dep, D))
    bilan, date_bilan = dernier_bilan(couper(d["bilan"], lim_ex, dep, D), couper(d["bilan_t"], lim_tr, dep, D), D)

    # --- Dollars et capitalisation (CHOIX.md §5) -----------------------------------------------------------------
    fx_comptes = taux_a_la_date(d["change_comptes"], D)                       # 1 unité de la devise des comptes en dollars
    fx_cours = taux_a_la_date(d["change_cours"], D)                           # 1 unité de la devise de cotation en dollars
    centimes = 100.0 if info.get("currency") in DEVISES_CENTIMES else 1.0     # cours en pence : / 100
    cours = d["cours"].copy()
    veille = cours[cours["date"] <= D - pd.Timedelta(days=1)]                 # cours connus la veille de D
    cap = info.get("marketCap")                                               # capitalisation du jour (devise principale)
    if cap and len(veille) and len(cours):
        cap_date = cap * (veille["close"].iloc[-1] / cours["close"].iloc[-1]) if mode == "daté" else cap  # P4
        me = cap_date * fx_cours                                              # en dollars
    else:
        me = np.nan
    me = me if me and me > 0 else np.nan                                      # capitalisation <= 0 : manquante

    # --- 12 derniers mois ----------------------------------------------------------------------------------------
    valeurs, origines = {}, {}
    for k in ["NI_common", "E_star", "GP_inv", "EBITDA", "CFO", "INT", "INT_PAID", "CA"]:
        valeurs[k], fin, origines[k] = ttm(annuel, trim, k, D) if len(annuel) or len(trim) else (np.nan, None, None)
    if not len(annuel):                                                       # aucun exercice : tableau vide utilisable
        annuel = pd.DataFrame(columns=["CA", "NI_common", "RN_conso", "E_star"], dtype=float)
    interets = valeurs["INT"] if pd.notna(valeurs["INT"]) else valeurs["INT_PAID"]   # repli : intérêts payés

    # --- Bilan ---------------------------------------------------------------------------------------------------
    b = bilan
    TA = b.get("TA", np.nan)
    ta = TA if TA > 0 else np.nan                                             # dénominateur <= 0 : ratio manquant
    TL, SE = b.get("TL", np.nan), b.get("SE", np.nan)
    loc = 0.0 if pd.isna(b.get("LOC", np.nan)) else b["LOC"]                  # dettes de location, 0 si absentes
    tl_adj = TL - loc                                                         # passif hors location simple
    cash = b.get("CASH", np.nan)
    if pd.isna(cash) and pd.notna(b.get("CASH_SEUL", np.nan)):                # repli : trésorerie + placements
        cash = b["CASH_SEUL"] + (0.0 if pd.isna(b.get("PCT", np.nan)) else b["PCT"])
    mino = 0.0 if pd.isna(b.get("MINO", np.nan)) else b["MINO"]
    gw, intang = b.get("GW", np.nan), b.get("INTANG", np.nan)
    if pd.isna(gw) and pd.isna(intang) and pd.notna(b.get("GW_INTANG", np.nan)):
        gw, intang = b["GW_INTANG"], 0.0                                      # seulement le total des deux
    gw = 0.0 if pd.isna(gw) else gw                                           # 0 si absent d'un bilan publié
    intang = 0.0 if pd.isna(intang) else intang
    aoci = b.get("AOCI", np.nan)
    dette = b.get("DETTE_TOT", np.nan)
    if pd.notna(dette):
        dette = dette - loc                                                   # dette hors location
    elif pd.notna(interets) and pd.notna(ta) and abs(interets) < SEUIL_DETTE_NULLE * ta:
        dette = 0.0                                                           # règle de dette nulle

    # --- Ratios (CHOIX.md §3) ------------------------------------------------------------------------------------
    tl_usd, cash_usd = tl_adj * fx_comptes, cash * fx_comptes                 # montants du bilan en dollars
    r = {}
    r["ROE"] = valeurs["NI_common"] / SE if SE > 0 else np.nan                # rentabilité des fonds propres
    r["ROA_FIN"] = (valeurs["E_star"] - valeurs["GP_inv"]) / ta               # rentabilité de l'actif (financières)
    r["TLMTA"] = tl_usd / (tl_usd + me)                                       # dettes / (dettes + capitalisation)
    r["CASHMTA"] = cash_usd / (tl_usd + me)                                   # trésorerie / (dettes + capitalisation)
    r["TAILLE"] = me                                                          # capitalisation en dollars
    ebitda = valeurs["EBITDA"]
    if pd.isna(dette) or pd.isna(cash) or pd.isna(ebitda):
        r["DN_EBITDA"] = np.nan                                               # un poste manque
    else:
        r["DN_EBITDA"] = (dette - cash) / ebitda if ebitda > 0 else DN_EBITDA_PIRE   # EBITDA <= 0 : le pire
    fp_banque = (SE - gw - intang + 0.0) / ta                                 # moins-value latente HTM : 0 (absente)
    fp_autres = (SE - (0.0 if pd.isna(aoci) else aoci)) / ta
    r["E_FP"] = fp_banque if sous_secteur == "banques" else fp_autres         # fonds propres / actif
    # Garde-fou : entrées (CHOIX.md §2)
    r["CASH"], r["CFO_TTM"], r["EBITDA_TTM"], r["INTERETS_TTM"] = cash, valeurs["CFO"], ebitda, interets
    # Exclusions : bénéfices des deux derniers exercices, fonds propres (replis de outils/recherche.py)
    ni = annuel["NI_common"] if len(annuel) else pd.Series(dtype=float)
    rn = annuel["RN_conso"] if len(annuel) else pd.Series(dtype=float)
    es = annuel["E_star"] if len(annuel) else pd.Series(dtype=float)
    r["NI_FY0"] = ni.iloc[0] if len(ni) and pd.notna(ni.iloc[0]) else (rn.iloc[0] if len(rn) else np.nan)
    r["NI_FY1"] = ni.iloc[1] if len(ni) > 1 and pd.notna(ni.iloc[1]) else (es.iloc[1] if len(es) > 1 else np.nan)
    r["SE_EXCLUSION"] = SE if pd.notna(SE) else TA - TL - mino

    # --- Dynamique (cours en dollars, contre le S&P 500 TR) ----------------------------------------------------
    change = d["change_cours"]
    px = cours.set_index("date")["adj_close"] / centimes                      # cours ajusté en devise principale
    if change is not None:
        px = px * change.reindex(px.index, method="ffill")                    # converti en dollars jour par jour
    marche_hebdo = hebdomadaire(d["marche"])                                  # S&P 500 TR, clôtures du vendredi
    dyn = dynamique_w1(pd.DataFrame({"date": px.index, "adj_close": px.values}), marche_hebdo, D)
    r.update({k: dyn.get(k, np.nan) for k in ["m1w1_moyenne", "m1w1_ecart_type", "m1w1_n"]})
    r["premier_cours"] = dyn.get("premier_cours", pd.NaT)

    # --- Croissances par société (CHOIX.md §7) -----------------------------------------------------------------
    croissances = croissances_societe(annuel, symbole, me / fx_comptes, D)   # capitalisation dans la devise des comptes

    # --- Ligne complète --------------------------------------------------------------------------------------------
    ligne = {"cik": symbole, "ticker": symbole, "date": D, "groupe": groupe, "secteur": secteur,
             "sous_secteur": sous_secteur, **r,
             "nom": info.get("longName") or info.get("shortName"), "bourse": info.get("exchange"),
             "devise_cours": info.get("currency"), "devise_comptes": info.get("financialCurrency"),
             "industrie_yahoo": info.get("industry"), "secteur_yahoo": info.get("sector"), "pays": info.get("country"),
             "fin_exercice": annuel["CA"].dropna().index[0] if len(annuel) and annuel["CA"].notna().any() else pd.NaT,
             "fin_ttm": next((f for f in [ttm(annuel, trim, "NI_common", D)[1]] if f is not None), pd.NaT),
             "origine_ttm": origines.get("NI_common"), "date_bilan": date_bilan,
             "date_cours": veille["date"].iloc[-1] if len(veille) else pd.NaT,
             "taux_comptes": fx_comptes, "taux_cours": fx_cours,
             "nb_exercices": int(annuel["CA"].notna().sum()) if len(annuel) else 0}
    return ligne, croissances


def croissances_societe(annuel, cik, me, D):
    """Croissances annuelles de la société (première moitié des calculs PERS et GS, CHOIX.md §7).
    Régularité : CA, EBITDA, FFO par action, revenus ; niveau : CA, EBITDA, revenus.
    me : capitalisation dans la DEVISE DES COMPTES (la clé des bases négatives, variation / capitalisation, doit être
    sans unité, comme dans la recherche où tout est en dollars)."""
    sortie = {}
    if not len(annuel):
        return sortie
    a = annuel.sort_index(ascending=False)                                    # exercices, du plus récent au plus ancien
    for serie in ["CA", "EBITDA", "FFOPA", "REV_FIN"]:
        x = a[serie].dropna().iloc[:NB_EXERCICES]                             # les 4 plus récents où la série existe
        table = pd.DataFrame({"cik": cik, "fin": x.index, serie: x.values})
        # Valeur de l'exercice précédent : exercice clos environ un an plus tôt (comparable d'un an, comme X_q-4)
        prec = []
        for fin in x.index:
            avant = x[(x.index <= fin - pd.Timedelta(days=334)) & (x.index >= fin - pd.Timedelta(days=396))]
            prec.append(avant.iloc[0] if len(avant) else np.nan)
        table[serie + "_prec"] = prec
        sortie["PERS_" + serie] = croissances_pers(table, serie, serie + "_prec", D, PERS_ANNUEL["mois_fenetre"])
    for serie in ["CA", "EBITDA", "REV_FIN"]:
        x = a[serie].dropna().iloc[:NB_EXERCICES]
        exo = pd.DataFrame({"cik": cik, "fy_fin": x.index, serie: x.values})
        sortie["GS_" + serie] = croissances_gs(exo, serie, pd.Series({cik: me}), D, GS_ANNUEL["nb"])
    return sortie
