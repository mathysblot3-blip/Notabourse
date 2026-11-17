"""Calcul de la note NotaBourse (formule C8 de la recherche de Mathys Blot), sans interface.

Ce dossier est un « paquet » Python : app.py et les tests l'importent avec `from notabourse import ...`.
Il ne contient aucune donnée et aucun secret.
"""
import shutil    # copie de fichier
import tempfile  # dossier temporaire du système
from pathlib import Path  # chemins de fichiers

import certifi   # fichier des autorités de certification (connexions sécurisées)

# Correctif du 17/11/2026 (audit, constat 4.4). La bibliothèque réseau de yfinance (curl_cffi) ne sait pas lire le
# fichier de certificats quand son chemin contient un caractère accentué (dossier « BàL » sur le PC de Mathys) :
# « curl: (77) error adding trust anchors ». On copie alors ce fichier dans le dossier temporaire du système et on dit
# à certifi de donner ce nouveau chemin. Sans effet en ligne (chemin sans accent) : on ne change rien dans ce cas.
# Ce code s'exécute avant tout import de yfinance, car tous les modules du site sont dans ce paquet.
_copie = Path(tempfile.gettempdir()) / "cacert_bourse_a_lunettes.pem"         # copie, dans un dossier sans accent
if not certifi.where().isascii() and str(_copie).isascii():                  # seulement si c'est utile et possible
    shutil.copyfile(certifi.where(), _copie)                                  # copie à jour à chaque démarrage
    certifi.where = lambda: str(_copie)                                       # nouveau chemin, sans accent
