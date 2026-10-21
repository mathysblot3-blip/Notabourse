"""Tests de la page « Tests sur le passé » (20/10/2026) : chaque graphique appelé existe dans les deux langues, les deux
pages appellent les mêmes graphiques dans le même ordre, et l'avertissement sur les performances simulées est présent.
Lancer depuis le dossier site : .\.venv\Scripts\python.exe -m pytest tests
"""
import json              # textes de l'interface
import re                # repérage des lignes {{graphique:...}}
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
PAGES = {lg: (SITE / "traductions" / f"tests_{lg}.md").read_text(encoding="utf-8") for lg in ("fr", "en")}
APPEL = re.compile(r"^\{\{graphique:(\w+)(:sans_avertissement)?\}\}$", re.M)


def test_memes_graphiques_dans_les_deux_langues():
    fr, en = APPEL.findall(PAGES["fr"]), APPEL.findall(PAGES["en"])
    assert fr == en and len(fr) == 8                                          # 8 graphiques, même ordre (« effets déjà connus » retiré le 21/10/2026)
    assert sum(1 for _, sans in fr if sans) == 1                              # un seul sans avertissement (hors indice)


def test_chaque_image_existe():
    for lg, page in PAGES.items():
        for nom, _ in APPEL.findall(page):
            assert (SITE / "images" / "tests" / f"{nom}_{lg}.png").exists(), f"{nom}_{lg}.png"


def test_avertissement_et_echantillon():
    for lg in ("fr", "en"):
        T = json.loads((SITE / "traductions" / f"{lg}.json").read_text(encoding="utf-8"))
        assert "2010-2026" in T["avertissement_simule"], lg                  # avertissement sous chaque graphique
    assert "en échantillon" in PAGES["fr"] and "in sample" in PAGES["en"]     # jamais présentés comme hors échantillon
    for page in PAGES.values():
        assert "—" not in page and "garde-fou" not in page.lower() and "safeguard" not in page.lower()
