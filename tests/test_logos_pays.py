"""Tests du logo jaune et des drapeaux (20/11/2026), sans réseau : images fabriquées sur place.
Lancer depuis le dossier site : .\.venv\Scripts\python.exe -m pytest tests
"""
import io                 # images en mémoire
import sys
from pathlib import Path

import numpy as np        # lecture des pixels
from PIL import Image     # fabrication des images d'essai

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))
from notabourse.logos import logo_jaune, telecharger_logo   # noqa: E402
from notabourse.pays import PAYS_YAHOO, a_un_drapeau, adresse_drapeau, pays_de   # noqa: E402

JAUNE = "#D8AE48"


def _png(image):
    """Image Pillow -> octets PNG."""
    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    return tampon.getvalue()


def _pixels(png):
    """Octets PNG -> tableau des pixels (hauteur x largeur x 4)."""
    return np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))


def test_logo_sur_fond_transparent_devient_tout_jaune():
    """Un « logo » de deux couleurs sur fond transparent (comme le G de Google) : tout le dessin devient jaune."""
    im = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(20, 80):
        for y in range(20, 80):
            im.putpixel((x, y), (66, 133, 244, 255) if x < 50 else (234, 67, 53, 255))   # bleu et rouge
    p = _pixels(logo_jaune(_png(im), JAUNE))
    visibles = p[p[..., 3] > 200]                                             # pixels du dessin
    assert len(visibles) > 0
    assert (visibles[:, :3] == (216, 174, 72)).all()                         # une seule couleur : le jaune
    assert p[..., 3].min() < 50 or p.shape[0] == 96                           # rogné au dessin (hauteur fixe)


def test_logo_sur_fond_blanc_garde_le_dessin_et_retire_le_fond():
    """Un dessin noir sur fond blanc (comme Apple) : le fond disparaît, le dessin devient jaune."""
    im = Image.new("RGB", (120, 120), (255, 255, 255))
    for x in range(40, 80):
        for y in range(30, 90):
            im.putpixel((x, y), (0, 0, 0))
    p = _pixels(logo_jaune(_png(im), JAUNE))
    assert p.shape[0] == 96                                                   # hauteur fixe
    assert p[..., 3].mean() > 200                                             # rogné : il ne reste que le dessin


def test_image_illisible_ou_vide_donne_rien():
    assert logo_jaune(b"pas une image", JAUNE) is None
    assert logo_jaune(_png(Image.new("RGB", (50, 50), (255, 255, 255))), JAUNE) is None   # carré blanc : rien


def test_symbole_bizarre_jamais_envoye():
    """Un texte qui n'est pas un symbole de Yahoo n'est jamais envoyé au service des logos (pas de réseau ici)."""
    assert telecharger_logo("../../etc") is None
    assert telecharger_logo("AAPL?x=1") is None
    assert telecharger_logo("") is None


def test_pays_traduits_et_drapeaux_presents():
    assert pays_de("United States", "fr") == ("us", "États-Unis")
    assert pays_de("Ireland", "en") == ("ie", "Ireland")
    assert pays_de("Atlantis", "fr") == (None, "Atlantis")                    # inconnu : nom de Yahoo, sans drapeau
    assert pays_de(None, "fr") == (None, None)
    for code, _, _ in PAYS_YAHOO.values():                                    # chaque pays connu a son image
        assert a_un_drapeau(code), code


def test_drapeaux_des_40_pays_du_classement():
    import re
    code = (SITE / "vues" / "classement.py").read_text(encoding="utf-8")
    bloc = code.split("PAYS = {")[1].split("ZONES = {")[0]                    # dictionnaire des pays du classement
    for pays in re.findall(r'"([a-z]{2})": \(', bloc):
        assert a_un_drapeau(pays) and adresse_drapeau(pays), pays


def test_initiales_sans_formes_juridiques():
    """Sans logo, la fiche montre les initiales du nom [M] 20/11/2026 : formes juridiques et petits mots ignorés."""
    from notabourse.logos import initiales, initiales_svg
    assert initiales("Empresas Lipigas S.A.") == "EL"
    assert initiales("IRSA Inversiones y Representaciones Sociedad Anónima") == "IIR"   # 3 lettres au plus
    assert initiales("Linco Technology Co., Ltd.") == "LT"
    assert initiales("Société Générale") == "SG"                              # accents retirés
    assert initiales("<script>alert(1)</script>") == "SA1"                    # rien que des lettres et des chiffres
    assert initiales("") == "" and initiales_svg("", JAUNE, b"") is None
    assert initiales_svg("Empresas Lipigas S.A.", JAUNE, b"police").startswith("data:image/svg+xml;base64,")


def test_logo_blanc_sur_fond_transparent_garde_sa_forme():
    """Un logo tout blanc sur fond transparent (prévu pour un fond sombre, comme Sprinklr) ne disparaît pas."""
    im = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(20, 80):
        for y in range(30, 70):
            im.putpixel((x, y), (255, 255, 255, 255))
    assert logo_jaune(_png(im), JAUNE) is not None
