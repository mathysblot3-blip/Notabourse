"""Télécharge une fois les petits drapeaux du site dans static/drapeaux/ [M] 20/11/2026.

Source : flagcdn.com (drapeaux du domaine public), images PNG de 80 pixels de large. Le site les sert lui-même : le
navigateur du visiteur ne contacte pas flagcdn. À relancer seulement si un pays est ajouté dans notabourse/pays.py.

Lancer depuis le dossier site :
    .venv\\Scripts\\python.exe -X utf8 reference\\telecharger_drapeaux.py
"""
import sys                 # chemin du dossier site, pour importer notabourse
import time                # petite pause entre deux téléchargements (politesse envers le service)
from pathlib import Path   # chemins de fichiers

import requests            # téléchargement

SITE = Path(__file__).resolve().parents[1]                                    # dossier site
sys.path.insert(0, str(SITE))                                                 # pour « import notabourse »
from notabourse.pays import DOSSIER_DRAPEAUX, DOSSIER_TABLEAU, codes_utiles   # noqa: E402  (après le chemin)

URL = "https://flagcdn.com/w80/{code}.png"                                    # 80 pixels de large

DOSSIER_DRAPEAUX.mkdir(parents=True, exist_ok=True)                           # crée le dossier s'il manque
for code in codes_utiles():                                                   # chaque pays connu du site
    fichier = DOSSIER_DRAPEAUX / f"{code}.png"
    if fichier.exists():                                                      # déjà là : on ne refait rien
        continue
    r = requests.get(URL.format(code=code), timeout=15)                       # téléchargement
    if r.status_code == 200 and r.headers.get("content-type", "").startswith("image/png"):
        fichier.write_bytes(r.content)                                        # image enregistrée
        print(f"{code} : {len(r.content)} octets")
    else:
        print(f"{code} : échec ({r.status_code})")                            # signalé, sans arrêter le reste
    time.sleep(0.2)                                                           # 5 demandes par seconde au plus

# Versions pour le tableau du classement : le tableau agrandit chaque image à la hauteur de la ligne (44 pixels), le
# drapeau prenait toute la case. On le pose au milieu d'une image transparente plus haute : il paraît plus petit
# (environ 24 pixels de large). Fabriquées ici, sans réseau.
from PIL import Image   # noqa: E402  (bibliothèque Pillow, déjà installée avec Streamlit)

DOSSIER_TABLEAU.mkdir(parents=True, exist_ok=True)
for fichier in sorted(DOSSIER_DRAPEAUX.glob("*.png")):
    drapeau = Image.open(fichier).convert("RGBA")                             # drapeau d'origine (80 px de large)
    fond = Image.new("RGBA", (drapeau.width, round(drapeau.width * 4 / 3)), (0, 0, 0, 0))   # 3 x 4, transparent
    fond.alpha_composite(drapeau, (0, (fond.height - drapeau.height) // 2))   # drapeau centré en hauteur
    fond.save(DOSSIER_TABLEAU / fichier.name, optimize=True)
