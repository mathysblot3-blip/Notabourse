"""Table de secours du prix comparé au secteur : moyennes des secteurs gardées à part (21/10/2026).

Sert seulement si la référence de la semaine n'a pas les colonnes EP (bénéfice / capitalisation) ou SP (ventes /
capitalisation) : la fiche compare alors la société à ces moyennes datées, avec la mention « valeur peu fiable » [M].
Une ligne par secteur : moyenne des rapports positifs des membres (au moins 5, sinon tout le groupe), comme
notabourse/prix.py. Aucun montant brut : des moyennes de ratios seulement.

Lancer depuis le dossier site, quand la référence est complète (à refaire de temps en temps, pas chaque semaine) :
  .venv\\Scripts\\python.exe reference\\construire_secours_prix.py
"""
import sys                 # chemin d'import
from pathlib import Path   # chemins de fichiers

import pandas as pd        # tableaux de données

SITE = Path(__file__).resolve().parents[1]                                    # dossier site
sys.path.insert(0, str(SITE))
from notabourse.prix import SECOURS, moyenne_secteur  # noqa: E402


def main():
    ref = pd.read_parquet(SITE / "reference" / "reference.parquet")           # référence de la semaine
    lignes = []
    for (groupe, secteur), _ in ref.groupby(["groupe", "secteur"]):           # chaque secteur de chaque groupe
        ligne = {"groupe": groupe, "secteur": secteur, "date": str(pd.Timestamp(ref["date"].iloc[0]).date())}
        for colonne in ("EP", "SP"):                                          # bénéfice, puis ventes
            moyenne, nb, repli = moyenne_secteur(ref, groupe, secteur, colonne)
            ligne.update({colonne: moyenne, "nb_" + colonne: nb, "repli_" + colonne: repli})
        lignes.append(ligne)
    table = pd.DataFrame(lignes)
    table.to_csv(SECOURS, index=False)
    print(table.assign(PER=1 / table["EP"], prix_ventes=1 / table["SP"]).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
