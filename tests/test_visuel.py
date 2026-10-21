"""Tests du nouveau visuel (20/10/2026) : le nom « Bourse à lunettes » partout dans les textes visibles, le logo
provisoire jamais publié, les couleurs du garde-fou inchangées.
Lancer depuis le dossier site : .\.venv\Scripts\python.exe -m pytest tests
"""
import json              # lecture des textes de l'interface
import subprocess        # demande à git si un fichier est ignoré
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]


def test_nom_du_site_dans_les_deux_langues():
    for lg in ("fr", "en"):
        T = json.loads((SITE / "traductions" / f"{lg}.json").read_text(encoding="utf-8"))
        assert T["titre"] == "Bourse à lunettes", lg
    for fichier in (SITE / "traductions").iterdir():                          # plus d'ancien nom visible
        assert "NotaBourse" not in fichier.read_text(encoding="utf-8"), fichier.name


def test_logo_provisoire_jamais_publie():
    r = subprocess.run(["git", "check-ignore", "-q", "images/logo_provisoire.png"], cwd=SITE)
    assert r.returncode == 0                                                  # 0 : git ignore bien le fichier


def test_couleurs_du_garde_fou_inchangees():
    code = (SITE / "vues" / "recherche.py").read_text(encoding="utf-8")
    assert '"vert": "#2E9E5B", "orange": "#E8912D", "rouge": "#D64545"' in code   # réservées au garde-fou [M]


def test_aucun_emoji_dans_le_menu():
    import re
    code = (SITE / "app.py").read_text(encoding="utf-8")
    assert "icon=" not in code.split("pages = [")[1]                          # menu numéroté 01 à 04, sans icônes [M]
    assert not re.search("[🌀-🫿☀-➿]", code)    # aucun émoji, ni dans l'onglet


def test_haut_de_page_sous_la_barre_de_streamlit():
    """La barre du haut de Streamlit fait 60 pixels (3,75 rem) : une marge plus petite cache le haut du titre sur
    téléphone (vu le 20/10/2026). Vérification complète de l'affichage : tests/verifier_affichage.js."""
    import re
    code = (SITE / "vues" / "commun.py").read_text(encoding="utf-8")
    marge = float(re.search(r'stMainBlockContainer"\] \{\{ padding-top: ([\d.]+)rem', code).group(1))
    assert marge >= 3.75


def test_marges_de_la_jauge():
    """Sur grand écran la jauge grandit : sans marges, le 0 et le 100 étaient coupés en bas et le 50 en haut (vu le
    20/10/2026). Mesuré ensuite de 360 à 2 560 pixels de large : tous entiers."""
    import re
    code = (SITE / "vues" / "recherche.py").read_text(encoding="utf-8")
    m = re.search(r"margin=dict\(l=(\d+), r=(\d+), t=(\d+), b=(\d+)\)", code)
    l, r, t, b = map(int, m.groups())
    assert min(l, r) >= 40 and t >= 40 and b >= 30
