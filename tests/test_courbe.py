"""Tests de la courbe du cours sur 10 ans (20/11/2026), sans réseau : cours fabriqués sur place.
Lancer depuis le dossier site : .\.venv\Scripts\python.exe -m pytest tests
"""
import sys
from pathlib import Path

import pandas as pd

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))
from notabourse.courbe import cotee_recemment, preparer_courbe, resume, simplifier   # noqa: E402


def _table(cours, debut="2016-11-21"):
    """Cours hebdomadaires fabriqués, à partir de `debut`."""
    return pd.DataFrame({"date": pd.date_range(debut, periods=len(cours), freq="W-MON"), "cours": cours})


def test_pence_ramenes_en_livres_et_vides_retires():
    t, devise = preparer_courbe(_table([100, None, 0, 200, 300, 400, 500, 600, 700, 800, 900]), "GBp")
    assert devise == "GBP"                                                    # pence -> livres
    assert t["cours"].tolist() == [1, 2, 3, 4, 5, 6, 7, 8, 9]                 # vide et zéro retirés, divisé par 100


def test_trop_peu_de_cours_pas_de_courbe():
    t, devise = preparer_courbe(_table([10, 11, 12]), "USD")
    assert t is None and devise == "USD"


def test_resume_premier_dernier_bas_haut():
    t, _ = preparer_courbe(_table([10, 8, 12, 30, 25, 20, 15, 20]), "USD")
    r = resume(t)
    assert r["debut"] == 10 and r["fin"] == 20 and abs(r["variation"] - 1.0) < 1e-12   # +100 %
    assert r["bas"] == 8 and r["haut"] == 30
    assert r["date_bas"] == t["date"].iloc[1] and r["date_haut"] == t["date"].iloc[3]


def test_cotee_recemment():
    aujourd_hui = pd.Timestamp("2026-11-20")
    assert not cotee_recemment(_table([1] * 10, "2016-11-21"), aujourd_hui)  # 10 ans de cours
    assert cotee_recemment(_table([1] * 10, "2021-06-21"), aujourd_hui)      # cotée en 2021 (Sprinklr)


def test_simplifier_un_point_tous_les_deux_mois():
    t, _ = preparer_courbe(_table(list(range(1, 521))), "USD")             # 10 ans de cours hebdomadaires
    s = simplifier(t)
    assert 58 <= len(s) <= 63                                                 # environ 60 points (120 mois / 2)
    assert s["cours"].iloc[0] == 1 and s["cours"].iloc[-1] == 520             # premier et dernier cours gardés
    assert s["date"].is_monotonic_increasing


def test_simplifier_historique_court_intact():
    t, _ = preparer_courbe(_table(list(range(1, 101))), "USD")             # 2 ans : rien de retiré
    assert len(simplifier(t)) == 100
