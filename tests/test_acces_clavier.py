"""Tests du clic du classement vers la fiche (20/11/2026). Le bouton intermédiaire de l'audit (S-A04, WCAG 3.2.2) a
été retiré à la demande de Mathys : un clic sur une case ouvre directement la fiche. Ces tests vérifient qu'il n'y a
qu'un seul changement de page et que la sélection est oubliée avant (sinon, au retour sur le classement, l'ancienne
sélection renverrait aussitôt vers la fiche).
Lancer depuis le dossier site : .\\.venv\\Scripts\\python.exe -m pytest tests
"""
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
CODE = (SITE / "vues" / "classement.py").read_text(encoding="utf-8")        # le code de la page Classement


def test_un_seul_changement_de_page():
    assert CODE.count("st.switch_page") == 1                                  # un seul changement de page


def test_selection_oubliee_avant_de_changer_de_page():
    avant = CODE.split("st.switch_page")[0]                                   # tout le code qui précède l'appel
    dernieres = [l for l in avant.splitlines() if l.strip()][-6:]             # les lignes juste avant
    assert any("st.session_state.pop(cle" in l for l in dernieres), dernieres
