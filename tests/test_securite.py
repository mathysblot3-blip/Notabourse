"""Tests de l'audit de sécurité du 19/10/2026 : ces protections ne doivent pas disparaître lors d'une modification.
Lancer depuis le dossier site : .\\.venv\\Scripts\\python.exe -m pytest tests
"""
import re                # recherche de motifs dans le code
import tomllib           # lecture de .streamlit/config.toml
from pathlib import Path

from notabourse.formats import echapper
from notabourse.limites import FENETRE, MAXIMUM, autoriser

SITE = Path(__file__).resolve().parents[1]


def test_nom_venu_de_yahoo_ne_peut_pas_inserer_de_lien_ni_d_image():
    texte = echapper("Société ![traceur](https://exemple.com/x.png) [clic](https://exemple.com)")
    assert "](" not in texte.replace("\\]\\(", "")                            # plus aucun lien Markdown actif
    assert texte.startswith("Société \\!\\[")


def test_limite_de_calculs_par_visite():
    calculs, t = [], 1000.0
    for _ in range(MAXIMUM):                                                  # MAXIMUM calculs permis
        ok, calculs = autoriser(calculs, t)
        assert ok
    ok, calculs = autoriser(calculs, t + 1)                                   # le suivant est refusé
    assert not ok
    ok, _ = autoriser(calculs, t + FENETRE + 1)                               # après la fenêtre : de nouveau permis
    assert ok


def test_erreurs_jamais_detaillees_aux_visiteurs():
    config = tomllib.loads((SITE / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert config["client"]["showErrorDetails"] == "none"


def test_actions_du_robot_figees_par_leur_commit():
    robot = (SITE / ".github" / "workflows" / "reference_hebdo.yml").read_text(encoding="utf-8")
    actions = re.findall(r"uses:\s*(\S+)", robot)
    assert actions and all(re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", a) for a in actions)


def test_html_non_echappe_sans_texte_venu_de_yahoo():
    """Les appels avec HTML non échappé (unsafe_allow_html=True) ne contiennent que des textes du site et des nombres :
    ni le nom de la société, ni sa bourse, ni son symbole (fournis par Yahoo). Analyse appel par appel (module ast)."""
    import ast
    for fichier in (SITE / "vues").glob("*.py"):
        code = fichier.read_text(encoding="utf-8")
        for noeud in ast.walk(ast.parse(code)):
            if isinstance(noeud, ast.Call) and any(k.arg == "unsafe_allow_html" for k in noeud.keywords):
                appel = ast.get_source_segment(code, noeud)
                for interdit in ('"nom"', "'nom'", "bourse", '"symbole"', "'symbole'"):
                    assert interdit not in appel, f"{fichier.name} : {appel[:80]}"


def test_mentions_legales_completes_dans_les_deux_langues():
    pages = {lg: (SITE / "traductions" / f"mentions_{lg}.md").read_text(encoding="utf-8") for lg in ("fr", "en")}
    for lg, p in pages.items():
        p = p.replace(" ", " ")                                          # espaces insécables lues comme des espaces
        assert len([l for l in p.splitlines() if l.startswith("### ")]) == 6, lg
        assert "1-1" in p and "Snowflake Inc." in p and "+1 844 766 9355" in p, lg   # LCEN : hébergeur et téléphone
        assert "—" not in p                                                    # règle de rédaction : pas de tiret cadratin
    assert sum(l.startswith("|") for l in pages["fr"].splitlines()) == sum(l.startswith("|") for l in pages["en"].splitlines())
