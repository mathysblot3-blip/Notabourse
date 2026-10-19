"""Note M et note sur 100 de la formule C8 : membres du S&P 500 entre eux, et autres sociétés comparées aux membres.

Copies de la recherche (19/10/2026), calcul inchangé :
  - membres : noter_groupe() de Recherche_score/10_score.py avec les options de C8 (W1, V10, V9), puis score_brut()
    et note_finale() de outils/score.py (poids POIDS_C7, plafond u_max = 1 comme 31_formule_c8.py) ;
  - autres sociétés : note_m_reference() et ses fonctions de Recherche_score/outils/note_m.py.
Adaptation décidée par Mathys (cahier des charges, 19/10/2026), dans des fonctions À PART (« affichage ») :
  note globale dès 2 composantes, dynamique comprise ou non, y compris pour une société cotée depuis moins de 12 mois.
  La note de recherche (dynamique exigée) reste calculée à côté et sert de référence pour tous les centiles.
"""
import numpy as np   # calcul numérique
import pandas as pd  # tableaux de données

from notabourse.composantes import composer, m1_final, note, noter_ratio
from notabourse.constantes import (COMPOSANTES, COMPOSANTES_C8, ECHELLE_ETOILES, JOURS_COTATION_MIN, MIN_COMPOSANTES,
                                   POIDS_C7, SOUS_SCORES)


# =====================================================================================================================
# 1. Membres du S&P 500, notés entre eux (10_score.py + outils/score.py)
# =====================================================================================================================
def noter_groupe_c8(x, groupe):
    """Notes Q1, G1, R2, M1 pour UN groupe (NF, FIN ou REIT) à UNE date.
    Copie de noter_groupe() (10_score.py) avec OPTIONS = {W1, V10, V9} et OMEGA = None, limitée aux composantes de
    poids non nul dans C8 (les autres ne changent pas la note : poids nul dans POIDS_C7)."""
    n = pd.DataFrame(index=x.index)                                           # tableau des notes, une ligne par titre
    cle = x["sous_secteur"] if groupe == "FIN" else x["secteur"]              # secteur, ou sous-secteur des FIN
    q_mode = "secteur"                                                        # V7 inactive : écart au secteur
    taille = [noter_ratio(x["TAILLE"], +1)]                                   # V8 inactive : la taille reste dans R2
    roe = noter_ratio(x["ROE"], +1, cle, "secteur")                           # V9 active : Q1 = ROE (NF et REIT)
    if groupe == "NF":
        n["Q1"] = roe
        g1 = [x["PERS_CA"], x["PERS_EBITDA"]]                                 # régularité : CA et EBITDA
        gs = [x["GS_CA"], x["GS_EBITDA"]]                                     # V10 active : niveau de croissance
        r2_ratios = [noter_ratio(x["TLMTA"], -1), noter_ratio(x["CASHMTA"], +1)] + taille
    elif groupe == "REIT":
        n["Q1"] = roe
        g1 = [x["PERS_CA"], x["PERS_FFO"]]                                    # foncières : FFO par action
        gs = [x["GS_CA"], x["GS_EBITDA"]]
        r2_ratios = [noter_ratio(x["TLMTA"], -1), noter_ratio(x["DN_EBITDA"], -1)] + taille
    else:  # FIN (V9 ne s'applique pas : Q1 des financières est déjà un rendement du résultat)
        n["Q1"] = noter_ratio(x["ROA_FIN"], +1, cle, q_mode)
        g1 = [x["PERS_REV"]]                                                  # financières : revenus
        gs = [x["GS_REV"]]
        r2_ratios = [noter_ratio(x["E_FP"], +1, cle, q_mode)] + taille
    n["G1"] = composer(pd.concat([noter_ratio(s, +1) for s in g1], axis=1), 1, None)   # régularité re-notée
    n["G1"] = composer(pd.concat([n["G1"]] + [note(s) for s in gs], axis=1), 1)       # avec le niveau, re-notée
    mini_r2 = 2 if len(r2_ratios) == 3 else 1                                 # R2 : 2 sur 3, ou 1 sur 2
    n["R2"] = composer(pd.concat(r2_ratios, axis=1), mini_r2, None)
    s_med = x["m1w1_ecart_type"].median()                                     # écart-type médian du groupe
    n["M1_brut"] = pd.Series(m1_final(x["m1w1_moyenne"], x["m1w1_ecart_type"], x["m1w1_n"], s_med), index=x.index)
    n["M1"] = noter_ratio(n["M1_brut"], +1)                                   # dynamique notée
    return n


def score_brut(notes, poids):
    """S = Σ w x note, poids manquants redistribués dans le sous-score, puis entre sous-scores au prorata.
    Copie de outils/score.py. Renvoie S (sur 100), le nombre de composantes et l'éligibilité."""
    total, poids_dispo = pd.Series(0.0, index=notes.index), pd.Series(0.0, index=notes.index)
    for sous, liste in SOUS_SCORES.items():
        w = pd.DataFrame({k: notes[k].notna() * poids[k] for k in liste})     # poids des composantes présentes
        somme_w = w.sum(axis=1)
        valeur = sum(notes[k].fillna(0.0) * w[k] for k in liste) / somme_w.replace(0, np.nan)  # moyenne dans le sous-score
        poids_sous = sum(poids[k] for k in liste)                             # poids du sous-score
        present = somme_w > 0
        total += (valeur * poids_sous).where(present, 0.0)
        poids_dispo += present * poids_sous
    S = total / poids_dispo.replace(0, np.nan)                                # redistribution entre sous-scores
    actives = [k for k in COMPOSANTES if poids[k] > 0]                        # composantes retirées (poids nul) exclues
    nb = notes[actives].notna().sum(axis=1)
    exige = lambda k: notes[k].notna() if poids[k] > 0 else True              # une composante retirée n'est plus exigée
    valo = (notes["V1"].notna() & (poids["V1"] > 0)) | (notes["V2"].notna() & (poids["V2"] > 0))
    if poids["V1"] == 0 and poids["V2"] == 0:                                 # valorisation retirée : plus exigée
        valo = pd.Series(True, index=notes.index)
    eligible = (nb >= MIN_COMPOSANTES - (len(COMPOSANTES) - len(actives))) & exige("R1") & exige("M1") & valo
    return S.where(eligible), nb, eligible


def note_finale(S, groupe, u_max):
    """z dans le groupe, u = rang de z parmi tous les titres notés, u* = min(u, u_max), N = arrondi(100 u*).
    Copie de outils/score.py."""
    z = S.groupby(groupe).transform(lambda s: (s - s.mean()) / s.std(ddof=1))  # M : écart à la moyenne du groupe
    n = z.notna().sum()                                                       # nombre de titres notés
    u = (z.rank(method="average") - 0.5) / n                                  # rang entre 0 et 1
    u_etoile = np.minimum(u, u_max)                                           # plafond (1 dans C8 : aucun effet)
    return z, u, u_etoile, (100 * u_etoile).round()


def noter_membres(r):
    """Note C8 des membres du S&P 500 à UNE date, entre eux, exactement comme la recherche.
    r : une ligne par membre (colonnes des ratios). Renvoie, avec le même index :
      Q1, G1, R2, M1 (notes de 0 à 100, vides si coté depuis moins de 12 mois, comme la recherche),
      Q1_aff, G1_aff, R2_aff, M1_aff (mêmes notes sans la règle des 12 mois, pour l'affichage décidé par Mathys),
      M1_brut, S, nb_composantes, M (= z), note_sur_100 (= N)."""
    morceaux = []
    for groupe, x in r.groupby("groupe"):                                     # un groupe à la fois
        morceaux.append(noter_groupe_c8(x, groupe))
    n = pd.concat(morceaux).reindex(r.index)                                  # dans l'ordre de r
    for k in COMPOSANTES_C8:
        n[k + "_aff"] = n[k]                                                  # copie avant la règle des 12 mois
    recent = r["premier_cours"].isna() | (r["premier_cours"] > r["date"] - pd.Timedelta(days=JOURS_COTATION_MIN))
    n.loc[recent, COMPOSANTES_C8] = np.nan                                    # coté depuis moins de 12 mois : non noté
    for k in COMPOSANTES:                                                     # composantes de poids nul : vides
        if k not in n:
            n[k] = np.nan
    n["S"], n["nb_composantes"], _ = score_brut(n, POIDS_C7)                  # score S (dynamique exigée)
    z, u, _, N = note_finale(n["S"], r["groupe"], 1.0)                        # u_max = 1 : le garde-fou ne plafonne pas
    n["M"], n["note_sur_100"] = z, N                                          # note M et note sur 100
    return n[[*COMPOSANTES_C8, *[k + "_aff" for k in COMPOSANTES_C8], "M1_brut", "S", "nb_composantes", "M",
              "note_sur_100"]]


# =====================================================================================================================
# 2. Société HORS du S&P 500, comparée aux membres (copie de outils/note_m.py)
# =====================================================================================================================
def _winsor_ref(y, ref):
    """Plafonne y aux 5e et 95e centiles de la référence (et la référence elle-même)."""
    bas, haut = ref.quantile(0.05), ref.quantile(0.95)
    return y.clip(bas, haut), ref.clip(bas, haut)


def _note_ref(y, ref):
    """Note de 0 à 100 de chaque valeur de y, d'après son centile parmi les valeurs de la référence (comme note())."""
    r = np.sort(ref.dropna().values)                                          # valeurs de la référence, triées
    n = len(r)
    if n == 0:
        return pd.Series(np.nan, index=y.index)
    inf = np.searchsorted(r, y.values, side="left")                           # valeurs de la référence strictement plus basses
    sup = np.searchsorted(r, y.values, side="right")                          # plus basses ou égales
    p = (inf + (sup - inf) / 2) / n                                           # centile (ex aequo : milieu)
    note_ = 100 * np.clip((p - 0.05) / 0.90, 0, 1)
    return pd.Series(np.where(y.notna(), note_, np.nan), index=y.index)


def _moyenne_pairs(ref_val, ref_cle, cle, minimum=8):
    """Moyenne des valeurs de la référence dans le secteur `cle` (au moins `minimum`), sinon de tout le groupe."""
    stats = ref_val.groupby(ref_cle).agg(["mean", "count"])
    m = cle.map(stats["mean"])
    n = cle.map(stats["count"]).fillna(0)
    return m.where(n >= minimum, ref_val.mean())


def _ratio(y_ext, y_ref, sens, cle_ext=None, cle_ref=None, mode="absolu"):
    """Chaîne d'un ratio (winsorisation, écart au secteur si mode='secteur', centile) contre la référence.
    Renvoie (notes de l'action hors indice, notes de la référence) pour pouvoir composer ensuite."""
    ye, yr = _winsor_ref(y_ext * sens, y_ref * sens)
    if mode == "secteur":
        # référence : chaque membre comparé à ses pairs SANS lui (comme ecart_secteur) ; action : à tous les membres
        somme = yr.groupby(cle_ref).transform("sum")
        nb = yr.notna().groupby(cle_ref).transform("sum")
        pairs_ref = ((somme - yr.fillna(0)) / (nb - yr.notna())).where(nb - yr.notna() >= 8, yr.mean())
        xr = yr - pairs_ref
        xe = ye - _moyenne_pairs(yr, cle_ref, cle_ext)
        return _note_ref(xe, xr), _note_ref(xr, xr)
    return _note_ref(ye, yr), _note_ref(yr, yr)


def _composer(notes_ext, notes_ref, minimum):
    """Composante à plusieurs ratios : moyenne des notes présentes (au moins `minimum`), re-notée contre la référence."""
    me = pd.concat(notes_ext, axis=1)
    mr = pd.concat(notes_ref, axis=1)
    k = min(minimum, me.shape[1])
    moy_e = me.mean(axis=1).where(me.notna().sum(axis=1) >= k)
    moy_r = mr.mean(axis=1).where(mr.notna().sum(axis=1) >= k)
    return _note_ref(moy_e, moy_r), _note_ref(moy_r, moy_r)


def _notes_groupe(e, r, groupe, masquer_recents_ext=True):
    """Notes Q1, G1, R2 et D (M1) d'actions hors indice e contre la référence r, pour UN groupe à UNE date.
    Seul ajout au code de recherche : masquer_recents_ext (vrai par défaut = recherche). Faux seulement pour la règle
    d'affichage de Mathys (société cotée depuis moins de 12 mois notée quand même) ; la référence n'est pas touchée."""
    cle_e = e["sous_secteur"] if groupe == "FIN" else e["secteur"]
    cle_r = r["sous_secteur"] if groupe == "FIN" else r["secteur"]
    out_e, out_r = pd.DataFrame(index=e.index), pd.DataFrame(index=r.index)
    # Q1 : ROE en écart au secteur (financières : rendement de l'actif, en écart au sous-secteur)
    col_q = "ROA_FIN" if groupe == "FIN" else "ROE"
    out_e["Q1"], out_r["Q1"] = _ratio(e[col_q], r[col_q], +1, cle_e, cle_r, "secteur")
    # G1 : régularité de la croissance (PERS), puis moyenne avec la croissance lissée (GS), re-notée
    pers = {"NF": ["PERS_CA", "PERS_EBITDA"], "REIT": ["PERS_CA", "PERS_FFO"], "FIN": ["PERS_REV"]}[groupe]
    gs = {"NF": ["GS_CA", "GS_EBITDA"], "REIT": ["GS_CA", "GS_EBITDA"], "FIN": ["GS_REV"]}[groupe]
    p = [_ratio(e[c], r[c], +1) for c in pers]
    g1_e, g1_r = _composer([a for a, _ in p], [b for _, b in p], 1)
    gsn = [_ratio(e[c], r[c], +1) for c in gs]
    out_e["G1"], out_r["G1"] = _composer([g1_e] + [a for a, _ in gsn], [g1_r] + [b for _, b in gsn], 1)
    # R2 : solidité du bilan et taille
    if groupe == "NF":
        r2 = [_ratio(e["TLMTA"], r["TLMTA"], -1), _ratio(e["CASHMTA"], r["CASHMTA"], +1), _ratio(e["TAILLE"], r["TAILLE"], +1)]
    elif groupe == "REIT":
        r2 = [_ratio(e["TLMTA"], r["TLMTA"], -1), _ratio(e["DN_EBITDA"], r["DN_EBITDA"], -1), _ratio(e["TAILLE"], r["TAILLE"], +1)]
    else:
        r2 = [_ratio(e["E_FP"], r["E_FP"], +1, cle_e, cle_r, "secteur"), _ratio(e["TAILLE"], r["TAILLE"], +1)]
    out_e["R2"], out_r["R2"] = _composer([a for a, _ in r2], [b for _, b in r2], 2 if len(r2) == 3 else 1)
    # D (M1) : « action - marché », s_med = médiane des écarts-types de la référence
    s_med = r["m1w1_ecart_type"].median()
    d_e = pd.Series(m1_final(e["m1w1_moyenne"], e["m1w1_ecart_type"], e["m1w1_n"], s_med), index=e.index)
    d_r = pd.Series(m1_final(r["m1w1_moyenne"], r["m1w1_ecart_type"], r["m1w1_n"], s_med), index=r.index)
    out_e["M1"], out_r["M1"] = _ratio(d_e, d_r, +1)
    # Coté depuis moins de 12 mois : non noté
    for out, x in ((out_e, e), (out_r, r)):
        if out is out_e and not masquer_recents_ext:                          # règle d'affichage de Mathys
            continue
        recent = x["premier_cours"].isna() | (x["premier_cours"] > x["date"] - pd.Timedelta(days=365))
        out.loc[recent, :] = np.nan
    return out_e, out_r


def _m_de_reference(ref):
    """M de tous les membres de la référence, triées (pour le centile), comme dans note_m_reference()."""
    S_ref_tous = []
    for groupe, r in ref.groupby("groupe"):                                    # M de tous les membres (pour le centile)
        _, nr = _notes_groupe(r.iloc[:0], r, groupe)
        S_r = nr[["Q1", "G1", "R2", "M1"]].mean(axis=1)
        ok_r = nr["M1"].notna() & (nr[["Q1", "G1", "R2", "M1"]].notna().sum(axis=1) >= 2)
        S_r = S_r.where(ok_r)
        S_ref_tous.append((S_r - S_r.mean()) / S_r.std(ddof=1))
    return np.sort(pd.concat(S_ref_tous).dropna().to_numpy())


def _centile_m(M, M_ref):
    """Note sur 100 = centile de M parmi les M triées de la référence (ex aequo : milieu), comme note_m_reference()."""
    return np.where(M.notna(),
                    100 * (np.searchsorted(M_ref, M.values, side="left")
                           + 0.5 * (np.searchsorted(M_ref, M.values, side="right")
                                    - np.searchsorted(M_ref, M.values, side="left"))) / len(M_ref),
                    np.nan)


def note_m_reference(ext, ref):
    """Note M et note sur 100 d'actions HORS du S&P 500 (ext), comparées aux membres du S&P 500 (ref), même date.
    Copie de outils/note_m.py (le calcul des M de la référence est seulement rangé dans _m_de_reference).
    Renvoie un DataFrame (Q1, G1, R2, M1 = D, S, M, note_sur_100) indexé comme ext."""
    lignes = []
    for groupe, e in ext.groupby("groupe"):
        r = ref[ref["groupe"] == groupe]
        ne, nr = _notes_groupe(e, r, groupe)
        S_e = ne[["Q1", "G1", "R2", "M1"]].mean(axis=1)                       # poids égaux, notes présentes
        S_r = nr[["Q1", "G1", "R2", "M1"]].mean(axis=1)
        ok_e = ne["M1"].notna() & (ne[["Q1", "G1", "R2", "M1"]].notna().sum(axis=1) >= 2)   # D exigée, 2 notes au moins
        ok_r = nr["M1"].notna() & (nr[["Q1", "G1", "R2", "M1"]].notna().sum(axis=1) >= 2)
        S_e, S_r = S_e.where(ok_e), S_r.where(ok_r)
        ne["S"] = S_e
        ne["M"] = (S_e - S_r.mean()) / S_r.std(ddof=1)                        # M : écart à la moyenne du groupe S&P 500
        lignes.append(ne)
    res = pd.concat(lignes).reindex(ext.index)
    res["note_sur_100"] = _centile_m(res["M"], _m_de_reference(ref))          # centile parmi les M des membres
    return res


# =====================================================================================================================
# 3. Règle d'affichage de Mathys : note dès 2 composantes (dynamique non exigée), cotées < 12 mois comprises
# =====================================================================================================================
def note_affichage_hors_indice(ext, ref):
    """Comme note_m_reference(), avec les deux seules différences décidées par Mathys pour l'affichage :
    S dès 2 composantes présentes (dynamique non exigée) et pas de règle des 12 mois pour la société elle-même.
    La référence (moyenne, écart-type, centiles) reste celle de la recherche. Quand la dynamique existe et que la
    société est cotée depuis plus de 12 mois, le résultat est identique à note_m_reference() (vérifié par les tests)."""
    lignes = []
    for groupe, e in ext.groupby("groupe"):
        r = ref[ref["groupe"] == groupe]
        ne, nr = _notes_groupe(e, r, groupe, masquer_recents_ext=False)       # sans la règle des 12 mois pour e
        S_e = ne[COMPOSANTES_C8].mean(axis=1)                                 # moyenne des notes présentes
        S_r = nr[COMPOSANTES_C8].mean(axis=1)
        ok_e = ne[COMPOSANTES_C8].notna().sum(axis=1) >= 2                    # [M] dès 2 composantes
        ok_r = nr["M1"].notna() & (nr[COMPOSANTES_C8].notna().sum(axis=1) >= 2)   # référence : règle de la recherche
        S_e, S_r = S_e.where(ok_e), S_r.where(ok_r)
        ne["S"] = S_e
        ne["M"] = (S_e - S_r.mean()) / S_r.std(ddof=1)
        ne["nb_composantes"] = ne[COMPOSANTES_C8].notna().sum(axis=1)
        lignes.append(ne)
    res = pd.concat(lignes).reindex(ext.index)
    res["note_sur_100"] = _centile_m(res["M"], _m_de_reference(ref))
    return res


def note_affichage_membres(r, notes):
    """Note affichée d'un membre : la note de recherche (noter_membres) quand elle existe ; sinon, dès 2 composantes
    (règle de Mathys), M calculée contre la moyenne et l'écart-type du groupe, note = centile parmi les M des membres.
    r : ratios des membres ; notes : sortie de noter_membres(). Renvoie S_aff, M_aff, note_aff, nb_aff, regle."""
    aff = notes[[k + "_aff" for k in COMPOSANTES_C8]]                         # notes sans la règle des 12 mois
    nb = aff.notna().sum(axis=1)                                              # nombre de composantes présentes
    S_aff = aff.mean(axis=1).where(nb >= 2)                                   # dès 2 composantes
    stats = notes["S"].groupby(r["groupe"]).agg(["mean", "std"])              # moyenne et écart-type du groupe (recherche)
    M_aff = (S_aff - r["groupe"].map(stats["mean"])) / r["groupe"].map(stats["std"])
    M_ref = np.sort(notes["M"].dropna().to_numpy())                           # M de recherche des membres, triées
    sortie = pd.DataFrame(index=r.index)
    recherche = notes["note_sur_100"].notna()                                 # la note de recherche existe
    sortie["S_aff"] = notes["S"].where(recherche, S_aff)
    sortie["M_aff"] = notes["M"].where(recherche, M_aff)
    sortie["note_aff"] = notes["note_sur_100"].where(recherche, pd.Series(_centile_m(M_aff, M_ref), index=r.index))
    sortie["nb_aff"] = nb
    sortie["regle"] = np.where(recherche, "recherche", np.where(S_aff.notna(), "affichage", "aucune"))
    return sortie


# =====================================================================================================================
# 4. Demi-étoiles
# =====================================================================================================================
def etoiles(note_sur_100):
    """Nombre d'étoiles (de 0,5 à 5) d'après la note arrondie affichée, borne basse incluse [M] échelle, [P] arrondi."""
    if note_sur_100 is None or pd.isna(note_sur_100):
        return None
    n = round(float(note_sur_100))                                            # note affichée (entier)
    for minimum, nb in ECHELLE_ETOILES:                                       # de la plus haute à la plus basse
        if n >= minimum:
            return nb
    return 0.5
