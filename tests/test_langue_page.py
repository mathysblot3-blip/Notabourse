"""Test S-A01 (WCAG 3.1.1) : le script qui règle l'attribut lang de la page reçoit la bonne langue.
Lancer depuis le dossier site : .\.venv\Scripts\python.exe -m pytest tests
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))                  # pour importer le dossier vues
from vues.commun import code_langue_page                                      # noqa: E402


def test_lang_francais_et_anglais():
    assert "lang = 'fr'" in code_langue_page("fr")
    assert "lang = 'en'" in code_langue_page("en")


def test_langue_inconnue_retombe_sur_le_francais():
    assert "lang = 'fr'" in code_langue_page("<script>")                      # rien d'autre n'est jamais écrit
