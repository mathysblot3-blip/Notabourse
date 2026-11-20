"""Logo d'une société, redessiné d'une seule couleur (le jaune du site) [M] 20/11/2026.

Le logo vient du service public d'images de Financial Modeling Prep (une image PNG par symbole, sans clé). Le serveur
du site le télécharge, puis le transforme : chaque pixel du dessin devient jaune, le fond devient transparent. Le logo
de Google, un « G » de quatre couleurs, devient ainsi un « G » tout jaune. Le navigateur du visiteur ne contacte
jamais ce service : il reçoit l'image déjà transformée, glissée dans la page.

Deux cas de logos :
  - fond transparent (Google, Coca-Cola) : le dessin est la partie opaque ; les parties presque blanches à l'intérieur
    (le texte blanc dans la forme bleue de SAP) deviennent des trous, comme sur un fond clair ;
  - fond plein (Apple sur blanc, Samsung sur noir) : la couleur du fond est lue sur le bord de l'image ; plus un pixel
    s'en éloigne, plus il est jaune.
Fonctions sans Streamlit : testables avec pytest (tests/test_logos.py).
"""
import base64          # image glissée dans la page (adresse « data: »)
import io              # image lue et écrite en mémoire, sans fichier
import re              # découpage du nom en mots (initiales)
import unicodedata     # lettres sans accent (initiales)

import numpy as np     # calculs sur tous les pixels à la fois
import requests        # téléchargement du logo
from PIL import Image  # lecture et écriture des images (bibliothèque Pillow)

URL_LOGO = "https://financialmodelingprep.com/image-stock/{symbole}.png"   # une image par symbole (format Yahoo)
DELAI = 4              # secondes d'attente au plus : sans réponse, la fiche s'affiche sans logo
TAILLE_MAX = 300_000   # octets au plus : un fichier plus gros est ignoré (protection)
HAUTEUR = 96           # hauteur du logo transformé, en pixels (affiché à environ 40 pixels : net sur tous les écrans)
COUVERTURE_MIN = 0.01  # moins de 1 % de pixels dessinés : logo vide ou raté, on n'affiche rien
COUVERTURE_MAX = 0.92  # plus de 92 % : un carré plein (fond non reconnu), on n'affiche rien


def couleur_rgb(hexa):
    """« #D8AE48 » -> (216, 174, 72)."""
    hexa = hexa.lstrip("#")                                                   # retire le dièse
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))                  # rouge, vert, bleu de 0 à 255


def opacite_du_dessin(image):
    """Opacité (0 à 1) de chaque pixel du dessin, selon le cas du logo (fond transparent ou fond plein)."""
    rgba = np.asarray(image.convert("RGBA"), dtype=float) / 255               # tableau hauteur x largeur x 4, de 0 à 1
    rgb, alpha = rgba[..., :3], rgba[..., 3]                                  # couleurs, puis transparence
    bord = np.concatenate([alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]])  # transparence des pixels du bord
    if np.median(bord) < 0.5:                                                 # bord surtout transparent : 1er cas
        blancheur = np.clip((rgb.min(axis=2) - 0.80) / 0.15, 0, 1)            # 0 sous 80 % de blanc, 1 au-dessus de 95 %
        troue = alpha * (1 - blancheur)                                       # parties presque blanches : trous
        if (troue > 0.5).sum() < 0.1 * (alpha > 0.5).sum():                   # logo blanc (prévu pour un fond sombre,
            return alpha                                                      # Sprinklr) : on garde toute la forme
        return troue
    pixels_bord = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])    # couleurs du bord : le fond
    fond = np.median(pixels_bord, axis=0)                                     # couleur médiane du bord
    distance = np.sqrt(((rgb - fond) ** 2).sum(axis=2)) / np.sqrt(3)          # écart à la couleur du fond, de 0 à 1
    plus_loin = np.percentile(distance, 99)                                   # écart du dessin le plus net
    if plus_loin < 0.05:                                                      # image d'une seule couleur : rien
        return np.zeros_like(alpha)
    return np.clip((distance - 0.04) / (0.55 * plus_loin), 0, 1) * alpha      # fond 0, dessin 1, bords adoucis


def logo_jaune(octets, couleur):
    """Image PNG (octets) du logo redessiné dans `couleur`, rognée au dessin ; None si le logo est inutilisable."""
    try:
        image = Image.open(io.BytesIO(octets))                                # lecture du fichier reçu
        image.load()                                                          # décodage complet (erreur ici si abîmé)
    except Exception:                                                         # pas une image lisible
        return None
    if image.width * image.height > 4_000_000:                                # image démesurée : ignorée
        return None
    opacite = opacite_du_dessin(image)                                        # 0 = fond, 1 = dessin
    couverture = float((opacite > 0.5).mean())                                # part de l'image dessinée
    if not COUVERTURE_MIN <= couverture <= COUVERTURE_MAX:                    # vide ou carré plein : rien
        return None
    lignes = np.where((opacite > 0.1).any(axis=1))[0]                         # lignes qui contiennent du dessin
    colonnes = np.where((opacite > 0.1).any(axis=0))[0]                       # colonnes qui contiennent du dessin
    opacite = opacite[lignes[0]:lignes[-1] + 1, colonnes[0]:colonnes[-1] + 1]  # rognage : marges vides retirées
    r, v, b = couleur_rgb(couleur)
    sortie = np.zeros(opacite.shape + (4,), dtype=np.uint8)                   # image vide, 4 canaux
    sortie[..., 0], sortie[..., 1], sortie[..., 2] = r, v, b                  # tout en jaune...
    sortie[..., 3] = np.round(opacite * 255).astype(np.uint8)                 # ...visible seulement sur le dessin
    image = Image.fromarray(sortie, "RGBA")
    largeur = max(1, round(image.width * HAUTEUR / image.height))            # même proportions, hauteur fixe
    image = image.resize((min(largeur, 4 * HAUTEUR), HAUTEUR), Image.LANCZOS)   # logo très large : borné à 4 fois
    tampon = io.BytesIO()
    image.save(tampon, format="PNG", optimize=True)                           # PNG transparent
    return tampon.getvalue()


def adresse_data(png):
    """Octets PNG -> adresse « data:image/png;base64,... » à mettre dans une balise <img>."""
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


# --- Sans logo : les initiales du nom, en jaune [M] 20/11/2026 -----------------------------------------------------
# Mots qui ne comptent pas pour les initiales : formes juridiques (Inc., S.A., Ltd...) et petits mots (de, of, y...).
MOTS_IGNORES = {
    "inc", "incorporated", "corp", "corporation", "co", "company", "companies", "ltd", "limited", "plc", "sa", "ag",
    "nv", "se", "spa", "ab", "asa", "as", "oyj", "bhd", "berhad", "tbk", "pt", "sab", "cv", "kgaa", "gmbh", "llc", "lp",
    "pcl", "anonima", "anonyme", "public", "holding", "holdings", "group", "the", "and", "of",
    "y", "de", "del", "la", "le", "les", "et", "und", "du", "des", "da", "do", "di", "e",
}
INITIALES_MAX = 3      # au plus 3 lettres : « IIR » pour IRSA Inversiones y Representaciones


def initiales(nom):
    """« Empresas Lipigas S.A. » -> « EL » ; lettres et chiffres sans accent seulement (rien d'autre ne passe)."""
    sans_accent = unicodedata.normalize("NFKD", str(nom or "")).encode("ascii", "ignore").decode("ascii")
    sans_accent = sans_accent.replace(".", "")                                # « S.A. » -> « SA » (forme juridique)
    mots = [m for m in re.split(r"[^A-Za-z0-9]+", sans_accent) if m]         # mots du nom, ponctuation retirée
    utiles = [m for m in mots if m.lower() not in MOTS_IGNORES] or mots       # tout ignoré : on garde tous les mots
    return "".join(m[0].upper() for m in utiles[:INITIALES_MAX])             # première lettre de chaque mot


def initiales_svg(nom, couleur, police):
    """Image SVG (adresse « data: ») des initiales dans la police à points du site (`police` : octets du fichier
    woff2, glissés dans l'image), ou None si le nom ne donne aucune lettre."""
    texte = initiales(nom)
    if not texte:
        return None
    largeur = 62 * len(texte) + 8                                             # police à chasse fixe : 62 par lettre
    fonte = base64.b64encode(police).decode("ascii")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{largeur}" height="{HAUTEUR}" '
           f'viewBox="0 0 {largeur} {HAUTEUR}"><style>@font-face{{font-family:P;'
           f"src:url(data:font/woff2;base64,{fonte}) format('woff2');font-weight:900}}</style>"
           f'<text x="50%" y="76" text-anchor="middle" font-family="P, monospace" font-weight="900" '
           f'font-size="100" fill="{couleur}">{texte}</text></svg>')            # texte : lettres et chiffres seulement
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def telecharger_logo(symbole):
    """Octets du logo d'origine, ou None (symbole inconnu, service muet, fichier trop gros)."""
    if not symbole or not all(c.isalnum() or c in ".-^=" for c in symbole):  # symbole de Yahoo seulement
        return None
    try:
        r = requests.get(URL_LOGO.format(symbole=symbole), timeout=DELAI)
    except requests.RequestException:                                         # réseau en panne : pas de logo
        return None
    if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
        return None                                                           # 404 : symbole inconnu du service
    if len(r.content) > TAILLE_MAX:
        return None
    return r.content
