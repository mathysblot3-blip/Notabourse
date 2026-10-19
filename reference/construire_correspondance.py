"""Table « industrie Yahoo -> groupe, secteur, sous-secteur » pour les sociétés qui ne déposent pas à la SEC (étape b).

Règle [M] 19/10/2026 : la table est calibrée sur les membres du S&P 500, dont le groupe et le secteur viennent du SIC
de la SEC (comme la recherche). Pour chaque industrie Yahoo :
  - avec des membres : le classement le plus fréquent parmi eux (niveau « membres ») ; désaccords listés dans
    correspondance_yahoo.md ;
  - égalité entre membres, ou aucun membre : un code SIC représentatif de l'industrie (SIC_REPRESENTATIF ci-dessous,
    proposé par Claude [P]), classé par les fonctions de la recherche (niveau « SIC représentatif »).
Construite une fois, validée par Mathys le 19/10/2026 (règle et cas Credit Services, immobilier, bourses), puis
FIGÉE : le robot hebdomadaire ne la recalcule pas.
Les arbitrages de Mathys s'écrivent dans ARBITRAGES ci-dessous, puis on relance le script.
Lancer depuis le dossier site : .venv\\Scripts\\python.exe reference\\construire_correspondance.py
"""
import sys                 # chemin d'import
import warnings            # avertissements sans conséquence masqués
from pathlib import Path   # chemins de fichiers

import pandas as pd   # tableaux de données
import yfinance as yf  # liste des industries de Yahoo

DOSSIER = Path(__file__).resolve().parent                                     # dossier reference
sys.path.insert(0, str(DOSSIER.parent))
from notabourse.classement import classer_par_sic  # noqa: E402
warnings.filterwarnings("ignore")
SECTEURS_YAHOO = ["basic-materials", "communication-services", "consumer-cyclical", "consumer-defensive", "energy",
                  "financial-services", "healthcare", "industrials", "real-estate", "technology", "utilities"]
# Code SIC représentatif [P] : industries sans membre du S&P 500, ou dont les membres sont à égalité.
# Le classement en découle par les fonctions de la recherche (groupe_de, secteur_de, sous-secteur).
SIC_REPRESENTATIF = {
    # Sans membre du S&P 500
    "Other Industrial Metals & Mining": 1000, "Other Precious Metals & Mining": 1040, "Silver": 1044,
    "Aluminum": 3334, "Lumber & Wood Production": 2400, "Coking Coal": 1220, "Paper & Paper Products": 2621,
    "Publishing": 2711, "Broadcasting": 4833, "Furnishings, Fixtures & Appliances": 2510, "Gambling": 7990,
    "Recreational Vehicles": 3716, "Department Stores": 5311, "Textile Manufacturing": 2200,
    "Education & Training Services": 8200, "Uranium": 1094, "Oil & Gas Drilling": 1381, "Thermal Coal": 1220,
    "Insurance - Specialty": 6351, "Mortgage Finance": 6162, "Financial Conglomerates": 6199,
    "Pharmaceutical Retailers": 5912, "Metal Fabrication": 3440, "Marine Shipping": 4400,
    "Staffing & Employment Services": 7363, "Airports & Air Services": 4581, "Business Equipment & Supplies": 3579,
    "Infrastructure Operations": 1600, "REIT - Mortgage": 6798, "Real Estate - Development": 6552,
    "Real Estate - Diversified": 6500, "Electronics & Computer Distribution": 5045, "Utilities - Renewable": 4911,
    # Égalité entre membres
    "Advertising Agencies": 7311, "Credit Services": 6141, "Specialty Business Services": 7389,
    "Conglomerates": 3600, "Consulting Services": 8742, "Information Technology Services": 7370,
    "Utilities - Diversified": 4931,
}
# Arbitrages de Mathys : industrie Yahoo -> (groupe, secteur, sous-secteur). Vide tant qu'il n'a pas tranché.
ARBITRAGES = {}


def industries_yahoo():
    """Toutes les industries de Yahoo, avec leur secteur (API « Sector » de yfinance)."""
    lignes = []
    for cle in SECTEURS_YAHOO:
        s = yf.Sector(cle)                                                    # un secteur Yahoo
        for nom in s.industries["name"]:                                      # ses industries
            lignes.append({"secteur_yahoo": s.name, "industrie_yahoo": nom})
    return pd.DataFrame(lignes)


def majoritaire(x):
    """Classement le plus fréquent d'un ensemble de membres, sa part, et les membres en désaccord."""
    trio = x["groupe"] + " / " + x["secteur"] + " / " + x["sous_secteur"]
    comptes = trio.value_counts()
    egalite = len(comptes) > 1 and comptes.iloc[0] == comptes.iloc[1]        # deux classements aussi fréquents
    choix = comptes.index[0]
    desaccord = x.loc[trio != choix, "cik"] + " (" + trio[trio != choix] + ")"
    return choix, comptes.iloc[0] / comptes.sum(), egalite, ", ".join(desaccord)


ref = pd.read_parquet(DOSSIER / "reference.parquet")                          # membres classés par SIC
ref = ref[ref["origine_classement"] == "SIC de la SEC"]
toutes = industries_yahoo()
lignes = []
for _, l in toutes.iterrows():
    x = ref[ref["industrie_yahoo"] == l["industrie_yahoo"]]
    choix, part, egalite, desaccord, nb = None, None, False, "", len(x)
    if len(x):                                                                # niveau « membres »
        choix, part, egalite, desaccord = majoritaire(x)
        niveau = "membres"
    if (not len(x) or egalite) and l["industrie_yahoo"] in SIC_REPRESENTATIF:  # SIC représentatif
        sic = SIC_REPRESENTATIF[l["industrie_yahoo"]]
        choix, niveau = " / ".join(classer_par_sic(sic)), f"SIC représentatif {sic}"
    if choix is None:                                                         # industrie inconnue de la table
        raise ValueError(f"Industrie sans classement : {l['industrie_yahoo']} (ajouter un SIC représentatif)")
    if l["industrie_yahoo"] in ARBITRAGES:                                    # Mathys a tranché
        choix, niveau = " / ".join(ARBITRAGES[l["industrie_yahoo"]]), "arbitrage de Mathys"
    g, s, ss = choix.split(" / ")
    lignes.append({"secteur_yahoo": l["secteur_yahoo"], "industrie_yahoo": l["industrie_yahoo"], "groupe": g,
                   "secteur": s, "sous_secteur": ss, "niveau": niveau, "nb_membres": nb, "part_majoritaire": None if part is None else round(part, 2),
                   "egalite": egalite, "desaccords": desaccord})
t = pd.DataFrame(lignes)
t.to_csv(DOSSIER / "correspondance_yahoo.csv", index=False)

# Rapport à relire par Mathys
a_relire = t[(t["nb_membres"] > 0) & (t["part_majoritaire"] < 1)]
sans = t[t["nb_membres"] == 0]
part = lambda r: "" if pd.isna(r["part_majoritaire"]) else f"{r['part_majoritaire']:.0%}"
ligne = lambda r: (f"| {r['secteur_yahoo']} | {r['industrie_yahoo']} | {r['groupe']} / {r['secteur']} / {r['sous_secteur']} | "
                   f"{r['niveau']} | {r['nb_membres']} | {part(r)}{' (égalité)' if r['egalite'] else ''} | {r['desaccords']} |")
texte = f"""# Correspondance industrie Yahoo -> groupe, secteur, sous-secteur (généré par `construire_correspondance.py`)

Calibrée sur {len(ref)} membres du S&P 500 classés par le SIC de la SEC. {len(t)} industries Yahoo :
{int((t['nb_membres'] > 0).sum())} avec des membres, {len(sans)} sans membre (SIC représentatif).
Ne sert qu'aux sociétés qui ne déposent pas à la SEC.

## Industries où les membres ne sont pas tous classés pareil ({len(a_relire)})

| Secteur Yahoo | Industrie Yahoo | Classement retenu | Règle | Membres | Part majoritaire | Membres en désaccord |
|---|---|---|---|---|---|---|
{chr(10).join(ligne(r) for _, r in a_relire.iterrows())}

## Industries sans aucun membre du S&P 500 ({len(sans)}) : SIC représentatif

| Secteur Yahoo | Industrie Yahoo | Classement retenu | Règle | Membres | | |
|---|---|---|---|---|---|---|
{chr(10).join(ligne(r) for _, r in sans.iterrows())}
"""
(DOSSIER / "correspondance_yahoo.md").write_text(texte, encoding="utf-8")
print(f"{len(t)} industries ; {len(a_relire)} à relire ; {len(sans)} sans membre", flush=True)
