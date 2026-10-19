"""Tests du calcul de la note sur de petits cas faits à la main (aucun accès à Internet).
Lancer depuis le dossier site : .venv\\Scripts\\python.exe -m pytest tests -q
"""
import sys                 # chemin d'import
from pathlib import Path   # chemins de fichiers

import numpy as np    # calcul numérique
import pandas as pd   # tableaux de données
import pytest         # outil de test : assert, approx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))                  # dossier site
from notabourse.classement import classer_par_sic  # noqa: E402
from notabourse.composantes import croissance_symetrique, pers, tente  # noqa: E402
from notabourse.constantes import PERS_ANNUEL  # noqa: E402
from notabourse.garde_fou import couleur, exclusions, note_voyant, notes_garde_fou  # noqa: E402
from notabourse.note import etoiles, note_affichage_hors_indice, note_m_reference  # noqa: E402
from notabourse.ratios import couper, poste, ttm  # noqa: E402


# --- Garde-fou : les points du tableau de candidat_c8.md --------------------------------------------------------
@pytest.mark.parametrize("valeur, vert, rouge, attendu", [
    (0.0, 2.0, 1.0, -1.0), (1.0, 2.0, 1.0, -1 / 3), (2.0, 2.0, 1.0, 1 / 3), (3.0, 2.0, 1.0, 1.0),    # trésorerie, intérêts
    (1.00, 0.80, 0.90, -1.0), (0.90, 0.80, 0.90, -1 / 3), (0.80, 0.80, 0.90, 1 / 3), (0.70, 0.80, 0.90, 1.0),  # TLMTA
    (0.03, 0.05, 0.04, -1.0), (0.04, 0.05, 0.04, -1 / 3), (0.05, 0.05, 0.04, 1 / 3), (0.06, 0.05, 0.04, 1.0),  # fonds propres
    (10.0, 2.0, 1.0, 1.0),                                                                             # borné à +1
])
def test_note_voyant_points_du_tableau(valeur, vert, rouge, attendu):
    assert note_voyant(pd.Series([valeur]), vert, rouge).iloc[0] == pytest.approx(attendu)


def test_couleurs():
    assert list(couleur(np.array([-1.0, -1 / 3, 0.0, 1 / 3, 1.0]))) == ["rouge", "rouge", "orange", "vert", "vert"]


def test_cas_particuliers_du_garde_fou():
    """Flux d'exploitation positif : +1 ; pas d'intérêts : +1 ; EBITDA négatif avec intérêts : -1 ; financière : un voyant."""
    r = pd.DataFrame({"groupe": ["NF", "NF", "FIN"], "CASH": [10.0, 10.0, np.nan], "CFO_TTM": [5.0, -5.0, np.nan],
                      "TLMTA": [0.5, 0.5, 0.9], "EBITDA_TTM": [10.0, -1.0, np.nan], "INTERETS_TTM": [0.0, 2.0, np.nan],
                      "E_FP": [np.nan, np.nan, 0.045]})
    n = notes_garde_fou(r)
    assert n.loc[0, "trésorerie"] == 1.0 and n.loc[0, "intérêts"] == 1.0
    assert n.loc[1, "trésorerie"] == pytest.approx(1 / 3)                     # 10 / 5 = 2 ans : seuil vert = +1/3
    assert n.loc[1, "intérêts"] == -1.0
    assert np.isnan(n.loc[2, "endettement"]) and n.loc[2, "fonds propres / actif"] == pytest.approx(0.0)


def test_exclusions():
    """Exclue si la moyenne est orange ou rouge, si un des deux exercices est en perte, si les fonds propres sont <= 0."""
    base = {"groupe": "NF", "CASH": 1.0, "CFO_TTM": 1.0, "TLMTA": 0.5, "EBITDA_TTM": 10.0, "INTERETS_TTM": 1.0,
            "E_FP": np.nan, "NI_FY0": 1.0, "NI_FY1": 1.0, "SE_EXCLUSION": 1.0}
    r = pd.DataFrame([base, {**base, "NI_FY1": -1.0}, {**base, "SE_EXCLUSION": -1.0}, {**base, "TLMTA": 0.95,
                      "INTERETS_TTM": 10.0}])
    e = exclusions(r)
    assert e["gardee"].tolist() == [True, False, False, False]


def test_trésorerie_deux_ans():
    """Flux d'exploitation de -5 et trésorerie de 10 : 2 ans de trésorerie = seuil vert = +1/3."""
    r = pd.DataFrame({"groupe": ["NF"], "CASH": [10.0], "CFO_TTM": [-5.0], "TLMTA": [0.5], "EBITDA_TTM": [1.0],
                      "INTERETS_TTM": [0.0], "E_FP": [np.nan]})
    assert notes_garde_fou(r).loc[0, "trésorerie"] == pytest.approx(1 / 3)


# --- Étoiles ----------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("note_, attendu", [(100, 5.0), (95, 5.0), (94.6, 5.0), (94.4, 4.5), (90, 4.5), (80, 4.0),
                                            (70, 3.5), (55, 3.0), (40, 2.5), (30, 2.0), (20, 1.5), (10, 1.0), (9.4, 0.5),
                                            (0, 0.5)])
def test_echelle_des_etoiles(note_, attendu):
    assert etoiles(note_) == attendu


def test_pas_d_etoile_sans_note():
    assert etoiles(np.nan) is None


# --- Croissance -------------------------------------------------------------------------------------------------
def test_croissance_symetrique_avec_pertes():
    assert croissance_symetrique([-20.0], [-10.0])[0] == pytest.approx(-2 / 3)


def test_regularite_annuelle_a_la_main():
    """Deux sociétés du même groupe, 3 croissances chacune. A croît de 10 % par an, B de 0 %.
    Médiane de chaque année : moyenne des deux d. A est au-dessus de la médiane (s = +1 si l'écart atteint 10 points)."""
    D = pd.Timestamp("2026-10-01")
    fins = pd.to_datetime(["2025-12-31", "2024-12-31", "2023-12-31"])
    lignes = []
    for cik, g in (("A", 0.10), ("B", 0.0)):
        x = [100 * (1 + g) ** 3, 100 * (1 + g) ** 2, 100 * (1 + g)]          # valeurs de 2025, 2024, 2023
        prec = [100 * (1 + g) ** 2, 100 * (1 + g), 100.0]
        lignes += [{"cik": cik, "fin_trimestre": f, "X": a, "X_1": b} for f, a, b in zip(fins, x, prec)]
    t = pd.DataFrame(lignes)
    res = pers(t, "X", "X_1", pd.Series({"A": "NF", "B": "NF"}), D, **{k: v for k, v in PERS_ANNUEL.items()})
    dA = croissance_symetrique([110.0], [100.0])[0]                            # taux symétrique de A (0,0952)
    s = np.clip(dA / 2, -0.30, 0.10) / 0.10                                    # écart à la médiane (dA / 2)
    assert res["A"] == pytest.approx(s) and res["B"] == pytest.approx(-s)


def test_tente_neutralise_les_hausses_extremes():
    a = np.array([0.0, 0.01, -0.01, 0.005, -0.005, 0.002, 0.30, -0.30])
    t = tente(a)
    assert t["m1_n"] == 8 and t["m1_moyenne"] < np.mean(a[:6]) + 0.01


# --- Périodes ---------------------------------------------------------------------------------------------------
def _periodes(dates, valeurs):
    return pd.DataFrame({"CA": valeurs}, index=pd.DatetimeIndex(pd.to_datetime(dates), name="fin"))


def test_ttm_quatre_trimestres():
    annuel = _periodes(["2025-12-31"], [400.0])
    trim = _periodes(["2026-06-30", "2026-03-31", "2025-12-31", "2025-09-30"], [110.0, 105.0, 100.0, 95.0])
    v, fin, origine = ttm(annuel, trim, "CA", pd.Timestamp("2026-10-01"))
    assert v == 410.0 and origine == "4 trimestres" and fin == pd.Timestamp("2026-06-30")


def test_ttm_semestriel_prend_l_exercice():
    annuel = _periodes(["2025-12-31"], [400.0])
    v, _, origine = ttm(annuel, _periodes([], []), "CA", pd.Timestamp("2026-10-01"))
    assert v == 400.0 and origine == "exercice"


def test_ttm_trop_ancien():
    annuel = _periodes(["2024-12-31"], [400.0])
    v, _, origine = ttm(annuel, _periodes([], []), "CA", pd.Timestamp("2026-10-01"))
    assert np.isnan(v) and origine == "trop ancien"


def test_couper_avec_dates_de_depot():
    """Calcul daté : une période n'est gardée que si son rapport a été déposé avant la date."""
    df = pd.DataFrame({pd.Timestamp("2026-07-26"): [1.0], pd.Timestamp("2026-04-26"): [2.0]})
    depots = pd.DataFrame({"periode": pd.to_datetime(["2026-07-26", "2026-04-26"]),
                           "depot": pd.to_datetime(["2026-08-27", "2026-05-28"])})
    assert list(couper(df, None, depots, pd.Timestamp("2026-08-31")).columns) == list(df.columns)
    assert list(couper(df, None, depots, pd.Timestamp("2026-08-20")).columns) == [pd.Timestamp("2026-04-26")]


def test_poste_ordre_de_repli():
    df = pd.DataFrame([[np.nan, 3.0], [5.0, 7.0]], index=["Premier", "Second"], columns=["a", "b"])
    s = poste(df, ["Premier", "Second"])
    assert s["a"] == 5.0 and s["b"] == 3.0


# --- Classement -------------------------------------------------------------------------------------------------
def test_classement_sic():
    assert classer_par_sic(6021) == ("FIN", "FIN", "banques")
    assert classer_par_sic(6324) == ("FIN", "FIN", "assurances")              # UnitedHealth : assureur (recherche)
    assert classer_par_sic(6798) == ("REIT", "REIT", "REIT")
    assert classer_par_sic(3571)[0] == "NF"
    assert classer_par_sic(7389)[0] == "NF"                                   # Visa, Mastercard : industrie


# --- Règle d'affichage ------------------------------------------------------------------------------------------
def _reference(n=60, graine=1):
    gen = np.random.default_rng(graine)
    D = pd.Timestamp("2026-08-31")
    r = pd.DataFrame({"cik": [f"M{i}" for i in range(n)], "groupe": "NF",
                      "secteur": gen.choice(["A", "B", "C"], n), "date": D,
                      "premier_cours": D - pd.Timedelta(days=4000)})
    r["sous_secteur"] = r["secteur"]
    for c in ["ROE", "PERS_CA", "PERS_EBITDA", "GS_CA", "GS_EBITDA", "TLMTA", "CASHMTA", "TAILLE", "ROA_FIN", "E_FP",
              "DN_EBITDA", "PERS_FFO", "PERS_REV", "GS_REV"]:
        r[c] = gen.normal(size=n)
    r["m1w1_moyenne"], r["m1w1_ecart_type"], r["m1w1_n"] = gen.normal(0, 0.003, n), gen.uniform(0.02, 0.04, n), 46
    return r.set_index("cik", drop=False)


def test_affichage_identique_a_la_recherche_quand_la_dynamique_existe():
    ref = _reference()
    ext = _reference(5, graine=2)
    ext.index = ext["cik"] = [f"E{i}" for i in range(5)]
    a, b = note_m_reference(ext, ref), note_affichage_hors_indice(ext, ref)
    assert np.allclose(a["note_sur_100"], b["note_sur_100"])


def test_affichage_sans_dynamique_donne_une_note():
    ref = _reference()
    ext = _reference(1, graine=3)
    ext.index = ext["cik"] = ["E0"]
    ext["m1w1_moyenne"] = np.nan                                              # pas de dynamique
    assert np.isnan(note_m_reference(ext, ref)["note_sur_100"].iloc[0])      # recherche : pas de note
    assert note_affichage_hors_indice(ext, ref)["note_sur_100"].notna().iloc[0]   # site : note dès 2 composantes


def test_affichage_societe_recente_notee():
    ref = _reference()
    ext = _reference(1, graine=4)
    ext.index = ext["cik"] = ["E0"]
    ext["premier_cours"] = ext["date"] - pd.Timedelta(days=100)               # cotée depuis 100 jours
    assert np.isnan(note_m_reference(ext, ref)["note_sur_100"].iloc[0])
    assert note_affichage_hors_indice(ext, ref)["note_sur_100"].notna().iloc[0]
