"""Contrôle de la référence S&P 500 avant sa publication par le robot hebdomadaire (étape f).

Si un contrôle échoue, le script s'arrête avec une erreur : le robot ne publie rien, l'ancienne référence reste en ligne
et GitHub prévient Mathys par courriel [P] P6. Contrôles :
  1. calcul du jour (mode direct), daté d'au plus 2 jours ;
  2. assez de membres lus, présents et notés ;
  3. les trois groupes (industrie, financières, foncières) bien remplis ;
  4. aucun montant brut des comptes dans le fichier public (décision de Mathys : ratios dérivés seuls).
Lancer (depuis le dossier site) : python reference/controler_reference.py
"""
import json        # lecture de reference_info.json
import sys         # code d'erreur pour le robot
from pathlib import Path

import pandas as pd  # lecture du fichier de référence

DOSSIER = Path(__file__).resolve().parent                                     # dossier reference/
sys.path.insert(0, str(DOSSIER.parent))                                       # pour importer construire_reference
from reference.construire_reference import BRUTS  # noqa: E402  (colonnes de montants bruts, jamais publiées)

MIN_MEMBRES = 480            # la liste Wikipédia compte environ 500 sociétés [P]
MIN_PART_PRESENTS = 0.90     # au moins 90 % des membres dans la référence (P6 : arrêt au-delà de 10 % d'échecs)
MIN_PART_NOTES = 0.85        # au moins 85 % des membres notés (19/10/2026 : 496 sur 500) [P]
MIN_PAR_GROUPE = {"NF": 300, "FIN": 40, "REIT": 15}   # 19/10/2026 : 411, 62 et 27 [P]
AGE_MAX_JOURS = 2            # la référence doit dater du jour du robot (marge d'un week-end) [P]


def controler():
    """Liste des problèmes trouvés (vide si tout va bien)."""
    info = json.loads((DOSSIER / "reference_info.json").read_text(encoding="utf-8"))
    ref = pd.read_parquet(DOSSIER / "reference.parquet")
    problemes = []
    if info["mode"] != "direct":
        problemes.append(f"mode {info['mode']} au lieu de « direct »")
    age = (pd.Timestamp.today().normalize() - pd.Timestamp(info["date"])).days
    if age > AGE_MAX_JOURS:
        problemes.append(f"référence vieille de {age} jours")
    n = info["membres_liste"]
    if n < MIN_MEMBRES:
        problemes.append(f"seulement {n} membres dans la liste Wikipédia")
    if info["membres_dans_reference"] < MIN_PART_PRESENTS * n:
        problemes.append(f"seulement {info['membres_dans_reference']} membres sur {n} dans la référence")
    if info["membres_notes"] < MIN_PART_NOTES * n:
        problemes.append(f"seulement {info['membres_notes']} membres notés sur {n}")
    for groupe, minimum in MIN_PAR_GROUPE.items():
        nb = int((ref["groupe"] == groupe).sum())
        if nb < minimum:
            problemes.append(f"groupe {groupe} : {nb} sociétés (au moins {minimum} attendues)")
    bruts = [c for c in BRUTS if c in ref.columns]
    if bruts:
        problemes.append(f"montants bruts dans le fichier public : {bruts}")
    return problemes, info


if __name__ == "__main__":
    problemes, info = controler()
    if problemes:
        print("Référence REFUSÉE :", " ; ".join(problemes), flush=True)
        sys.exit(1)                                                           # le robot s'arrête, rien n'est publié
    print(f"Référence du {info['date']} acceptée : {info['membres_dans_reference']} membres, {info['membres_notes']} "
          f"notés, {info['reprises']} repris de la semaine précédente.", flush=True)
