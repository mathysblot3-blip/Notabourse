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
    assert '"vert": "#2E9E5B", "orange": "#E8912D", "rouge": "#D24444"' in code   # réservées au garde-fou [M]


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


def _luminance(hexa):
    """Luminance relative d'une couleur (formule WCAG 2.1) : 0 pour le noir, 1 pour le blanc."""
    canaux = [int(hexa.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]     # rouge, vert, bleu entre 0 et 1
    canaux = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canaux]
    return 0.2126 * canaux[0] + 0.7152 * canaux[1] + 0.0722 * canaux[2]


def _contraste(a, b):
    """Rapport de contraste WCAG entre deux couleurs : de 1 (identiques) à 21 (noir sur blanc)."""
    claire, sombre = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (claire + 0.05) / (sombre + 0.05)


def test_texte_des_pastilles_lisible_au_moins_4_5():
    """S-A03 (WCAG 1.4.3) : le texte posé sur chaque pastille de couleur a un contraste d'au moins 4,5."""
    import re
    code = (SITE / "vues" / "recherche.py").read_text(encoding="utf-8")
    couleurs = re.search(r"COULEURS = \{(.*?)\}", code).group(1)               # le dictionnaire des couleurs
    fonds = re.findall(r"#[0-9A-Fa-f]{6}", couleurs) + re.findall(r'VIOLET = "(#[0-9A-Fa-f]{6})"', code)
    ligne_texte_sur = re.search(r"TEXTE_SUR = \{.*\}", code).group(0)           # fonds qui reçoivent le texte sombre
    for fond in fonds:
        texte = "#15140f" if fond in ligne_texte_sur or "VIOLET" in ligne_texte_sur and fond == fonds[-1] else "#ffffff"
        assert _contraste(fond, texte) >= 4.5, (fond, texte)


def test_titres_des_composantes_lisibles():
    """[M] 20/11/2026 : le titre de chaque composante prend la nuance de sa note (rouge, orange, vert). Titre de 19 px
    en gras, donc « grand texte » au sens du WCAG 1.4.3 : contraste d'au moins 3 sur le fond, pour toute note."""
    import sys
    sys.path.insert(0, str(SITE))
    from notabourse.nuances import nuance
    couleurs = {"vert": "#2E9E5B", "orange": "#E8912D", "rouge": "#D24444"}   # celles de vues/recherche.py
    assert nuance(0, couleurs) == "#D24444" and nuance(100, couleurs) == "#2E9E5B"   # extrémités du dégradé
    assert nuance(50, couleurs) == "#E8912D"                                  # orange au milieu
    for note in range(0, 101):
        assert _contraste(nuance(note, couleurs), "#15140f") >= 3, note       # lisible sur le fond charbon
    code = (SITE / "vues" / "commun.py").read_text(encoding="utf-8")
    assert "p.ba-composante {{ margin: 0; font-size: 1.2rem; font-weight: 700" in code   # 19 px en gras
