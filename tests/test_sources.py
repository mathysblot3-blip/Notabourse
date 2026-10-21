"""Tests de la page Sources (20/10/2026) : les deux langues restent identiques, chaque lien DOI est bien formé, et les
mentions de licence demandées par Wikipédia (CC BY-SA 4.0) ne disparaissent pas.
Lancer depuis le dossier site : .\\.venv\\Scripts\\python.exe -m pytest tests
"""
import re                # recherche de motifs dans le texte
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
PAGES = {lg: (SITE / "traductions" / f"sources_{lg}.md").read_text(encoding="utf-8") for lg in ("fr", "en")}
DOI = re.compile(r"\[doi\.org/(10\.\d{4,9}/[^\]\s]+)\]\(https://doi\.org/(10\.\d{4,9}/[^)\s]+)\)")   # [texte](lien)


def _references(page):
    """Lignes qui commencent une référence (puce de liste), section par section (titres « ### »)."""
    sections, courante = [], None
    for ligne in page.splitlines():
        if ligne.startswith("### "):
            courante = []
            sections.append(courante)
        elif ligne.startswith("- ") and courante is not None:
            courante.append(ligne)
    return sections


def test_memes_references_dans_les_deux_langues():
    fr, en = _references(PAGES["fr"]), _references(PAGES["en"])
    assert len(fr) == len(en) == 6                                            # six parties
    assert [len(s) for s in fr] == [len(s) for s in en]                      # autant de références par partie
    assert len(fr[0]) == 32                                                   # les 32 articles du corpus
    assert DOI.findall(PAGES["fr"]) == DOI.findall(PAGES["en"])               # mêmes DOI, dans le même ordre


def test_liens_doi_bien_formes():
    for lg, page in PAGES.items():
        liens = DOI.findall(page)
        assert len(liens) >= 40, lg
        assert all(texte == cible for texte, cible in liens), lg              # le texte affiché = le lien suivi
        assert page.count("](https://doi.org/") == len(liens), lg             # aucun lien DOI mal écrit


def test_licence_wikipedia_et_marques():
    for lg, page in PAGES.items():
        assert page.count("CC BY-SA 4.0") >= 3, lg                           # attribution exigée par la licence
        assert "creativecommons.org/licenses/by-sa/4.0" in page, lg
        assert "membres_sp500.csv" in page and "CC BY-NC 4.0" in page, lg
        assert "—" not in page, lg                                           # règle de rédaction : pas de tiret cadratin
