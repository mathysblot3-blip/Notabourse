"""Tests du fichier de référence publié (reference/) : il est public, il ne doit contenir que des ratios dérivés.
Lancer depuis le dossier site : .\\.venv\\Scripts\\python.exe -m pytest tests
"""
from pathlib import Path

import pandas as pd

from reference.construire_reference import BRUTS

REFERENCE = Path(__file__).resolve().parents[1] / "reference"


def test_reference_publique_sans_montant_brut():
    colonnes = set(pd.read_parquet(REFERENCE / "reference.parquet").columns)
    assert not colonnes & set(BRUTS)                                          # décision de Mathys : ratios dérivés seuls


def test_robot_publie_seulement_la_reference():
    """Le robot ne publie que les 4 fichiers de la référence (pas le cache, pas les secrets)."""
    robot = (REFERENCE.parent / ".github" / "workflows" / "reference_hebdo.yml").read_text(encoding="utf-8")
    ligne = next(l for l in robot.splitlines() if l.strip().startswith("git add"))
    assert ligne.split()[2:] == ["reference/reference.parquet", "reference/croissances.parquet",
                                 "reference/membres_sp500.csv", "reference/reference_info.json"]
