"""Dégradé rouge, orange, vert du site, et la nuance d'une note sur ce dégradé [M] 20/11/2026.

Le même dégradé sert aux barres (risque de faillite, prix comparé au secteur) et, depuis le 20/11/2026, à la couleur du
titre de chaque composante : rouge pour une note basse, orange vers 50, vert pour une note haute.
Fonctions sans Streamlit : testables avec pytest.
"""

# Points d'arrêt du dégradé, en % de la largeur (ou note sur 100) : rouge plein jusqu'à 18, orange à 50, vert plein
# dès 82. Mêmes positions que les barres de la fiche depuis le 21/10/2026.
ARRETS = [(0, "rouge"), (18, "rouge"), (50, "orange"), (82, "vert"), (100, "vert")]


def _rgb(hexa):
    """« #D24444 » -> (210, 68, 68)."""
    hexa = hexa.lstrip("#")
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def nuance(note, couleurs):
    """Couleur (« #rrggbb ») de la note (0 à 100) sur le dégradé ; `couleurs` donne « rouge », « orange » et « vert »."""
    x = min(max(float(note), 0.0), 100.0)                                     # note bornée entre 0 et 100
    for (x1, c1), (x2, c2) in zip(ARRETS, ARRETS[1:]):                        # segment du dégradé qui contient x
        if x <= x2:
            t = 0.0 if x2 == x1 else (x - x1) / (x2 - x1)                     # avancée dans le segment, de 0 à 1
            a, b = _rgb(couleurs[c1]), _rgb(couleurs[c2])
            return "#" + "".join(f"{round(u + t * (v - u)):02X}" for u, v in zip(a, b))   # mélange des deux couleurs
    return couleurs["vert"]                                                   # jamais atteint (x <= 100)


def degrade_css(couleurs):
    """Le dégradé en CSS, de gauche (rouge) à droite (vert), pour les barres de la fiche."""
    return "linear-gradient(90deg," + ",".join(f"{couleurs[c]} {x}%" for x, c in ARRETS) + ")"
