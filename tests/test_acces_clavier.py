"""Tests d'accessibilité du classement (S-A04, WCAG 3.2.2) : choisir une case ne change pas de page tout seul.
Lancer depuis le dossier site : .\.venv\Scripts\python.exe -m pytest tests
"""
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
CODE = (SITE / "vues" / "classement.py").read_text(encoding="utf-8")        # le code de la page Classement


def test_le_changement_de_page_passe_par_un_bouton():
    """Le seul appel à st.switch_page doit se trouver dans le bloc d'un st.button, pas dans la simple sélection."""
    assert CODE.count("st.switch_page") == 1                                  # un seul changement de page
    avant = CODE.split("st.switch_page")[0]                                   # tout le code qui précède l'appel
    derniere_ligne_if = [l for l in avant.splitlines() if l.strip()][-2:]      # les deux lignes juste avant
    assert any("st.button(" in l for l in derniere_ligne_if), derniere_ligne_if


def test_le_bouton_a_un_texte_dans_les_deux_langues():
    assert CODE.count('"ouvrir": ') == 4                                      # prototype puis mise à jour, en fr et en en (la mise à jour l'emporte)
