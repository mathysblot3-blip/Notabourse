"""Cas de test du cahier des charges : ratios, voyants du garde-fou et exclusions, en direct (données Yahoo du jour).

Ce n'est pas un test automatique (il lit Internet) : on le lance à la main et on relit le tableau produit.
Les notes finales des sociétés hors du S&P 500 demandent la référence S&P 500 (étape b) : elles seront ajoutées ensuite.
Classement : SIC de la SEC pour les sociétés américaines ; pour les autres, groupe PROVISOIRE écrit ci-dessous, en
attendant la table « industrie Yahoo » de l'étape b.
Sortie : tests/cas_de_test.md
Lancer depuis le dossier site : .venv\\Scripts\\python.exe tests\\cas_de_test.py
"""
import sys                 # chemin d'import
import warnings            # avertissements sans conséquence masqués
from pathlib import Path   # chemins de fichiers

import numpy as np    # calcul numérique
import pandas as pd   # tableaux de données

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))                  # dossier site
from notabourse.calcul import charger_reference, noter_hors_indice, ratios_et_croissances  # noqa: E402
from notabourse.classement import charger_correspondance_yahoo  # noqa: E402
from notabourse.note import etoiles  # noqa: E402
from notabourse.garde_fou import exclusions, notes_garde_fou  # noqa: E402
from notabourse.sources import marche_sp500tr  # noqa: E402

warnings.filterwarnings("ignore")
# (symbole Yahoo, CIK SEC si la société y dépose, classement provisoire sinon)
CAS = [("AAPL", 320193, None), ("MSFT", 789019, None), ("NVDA", 1045810, None), ("JPM", 19617, None),
       ("PLD", 1045609, None), ("URW.PA", None, ("REIT", "REIT", "REIT")), ("MC.PA", None, ("NF", "?", "?")),
       ("TTE.PA", None, ("NF", "?", "?")), ("AIR.PA", None, ("NF", "?", "?")), ("7203.T", None, ("NF", "?", "?")),
       ("NESN.SW", None, ("NF", "?", "?")), ("ALCLA.PA", None, ("NF", "?", "?"))]


def f(v, chiffres=3):
    """Nombre lisible (vide si manquant)."""
    if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NaT:
        return ""
    if isinstance(v, pd.Timestamp):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, (int, float, np.floating, np.integer)):
        return f"{v:.{chiffres}g}"
    return str(v)


D = pd.Timestamp.today().normalize()                                          # aujourd'hui
marche = marche_sp500tr((D - pd.DateOffset(years=3)).strftime("%Y-%m-%d"))   # S&P 500 TR, lu une seule fois
correspondance = charger_correspondance_yahoo()                                # table industrie Yahoo (étape b)
reference = None
if (Path(__file__).resolve().parents[1] / "reference" / "reference.parquet").exists():
    reference, croissances_ref = charger_reference()                          # membres du S&P 500
lignes, croissances, notes = [], {}, {}
for symbole, cik, provisoire in CAS:
    print(symbole, flush=True)
    ligne, cr = ratios_et_croissances(symbole, D, "direct", cik=cik, correspondance=correspondance, marche=marche)
    if provisoire is not None and ligne["groupe"] is None:                     # pas encore de table Yahoo
        ligne["groupe"], ligne["secteur"], ligne["sous_secteur"] = provisoire
        ligne["origine_classement"] = "provisoire (étape b)"
    lignes.append(ligne)
    croissances[symbole] = {k: len(t) for k, t in cr.items()}                 # nombre de croissances par série
    if reference is not None:
        if symbole in reference.index:                                        # membre : note de la référence
            m = reference.loc[symbole]
            notes[symbole] = {"origine": "référence (membre)", **{k: m[k + "_aff"] for k in ["Q1", "G1", "R2", "M1"]},
                              "S": m["S_aff"], "M": m["M_aff"], "note": m["note_aff"], "regle": m["regle"],
                              "rech": m["note_sur_100"], "date_ref": m["date"]}
        else:                                                                 # hors indice : comparée aux membres
            r = noter_hors_indice(ligne, cr, reference.drop(index=symbole, errors="ignore"), croissances_ref)
            n, nr = r.get("notes", {}), r.get("notes_recherche", {})
            notes[symbole] = {"origine": "calcul contre les membres", **{k: n.get(k) for k in ["Q1", "G1", "R2", "M1"]},
                              "S": n.get("S"), "M": n.get("M"), "note": n.get("note_sur_100"),
                              "regle": "recherche" if pd.notna(nr.get("note_sur_100")) else "affichage",
                              "rech": nr.get("note_sur_100"), "date_ref": reference["date"].iloc[0]}
t = pd.DataFrame(lignes).set_index("cik")
v = notes_garde_fou(t)                                                        # voyants de -1 à +1
e = exclusions(t)                                                             # conditions d'exclusion

ent1 = "| Société | Groupe (origine) | Devises cours / comptes | Dernier exercice | TTM (origine) | Bilan | Cours | Exercices |"
l1 = [f"| {r['nom']} ({s}) | {r['groupe']} ({r['origine_classement']}) | {r['devise_cours']} / {r['devise_comptes']} | "
      f"{f(r['fin_exercice'])} | {f(r['fin_ttm'])} ({r['origine_ttm']}) | {f(r['date_bilan'])} | {f(r['date_cours'])} | "
      f"{r['nb_exercices']} |" for s, r in t.iterrows()]
ent2 = "| Société | ROE | ROA fin. | TLMTA | CASHMTA | Capitalisation (Md$) | Dette nette / EBITDA | Fonds propres / actif | Dynamique : moyenne, écart-type, semaines |"
l2 = [f"| {s} | {f(r['ROE'])} | {f(r['ROA_FIN'])} | {f(r['TLMTA'])} | {f(r['CASHMTA'])} | {f(r['TAILLE'] / 1e9, 4)} | "
      f"{f(r['DN_EBITDA'])} | {f(r['E_FP'])} | {f(r['m1w1_moyenne'])}, {f(r['m1w1_ecart_type'])}, {f(r['m1w1_n'])} |"
      for s, r in t.iterrows()]
ent3 = "| Société | Croissances CA / EBITDA / FFO par action / revenus (régularité) | Niveau CA / EBITDA / revenus |"
l3 = [f"| {s} | {c['PERS_CA']} / {c['PERS_EBITDA']} / {c['PERS_FFOPA']} / {c['PERS_REV_FIN']} | "
      f"{c['GS_CA']} / {c['GS_EBITDA']} / {c['GS_REV_FIN']} |" for s, c in croissances.items()]
ent4 = "| Société | Trésorerie | Endettement | Intérêts | Fonds propres / actif | Moyenne | Bénéfices 2 ans > 0 | Fonds propres > 0 | Gardée |"
oui = lambda b: "oui" if b else "non"
l4 = [f"| {s} | {f(v.loc[s, 'trésorerie'], 2)} | {f(v.loc[s, 'endettement'], 2)} | {f(v.loc[s, 'intérêts'], 2)} | "
      f"{f(v.loc[s, 'fonds propres / actif'], 2)} | {f(e.loc[s, 'garde_fou'], 2)} | {oui(e.loc[s, 'benefices_ok'])} | "
      f"{oui(e.loc[s, 'fonds_propres_ok'])} | {oui(e.loc[s, 'gardee'])} |" for s in t.index]
sep = lambda ent: "|" + "---|" * (ent.count("|") - 1)
ent5 = "| Société | Origine | Rentabilité | Croissance | Bilan | Dynamique | S | M | Note sur 100 | Étoiles | Règle | Note de recherche |"
l5 = [f"| {s} | {n['origine']} | {f(n['Q1'], 3)} | {f(n['G1'], 3)} | {f(n['R2'], 3)} | {f(n['M1'], 3)} | {f(n['S'], 3)} | "
      f"{f(n['M'], 3)} | {f(n['note'], 3)} | {f(etoiles(n['note']))} | {n['regle']} | {f(n['rech'], 3)} |"
      for s, n in notes.items()]
if notes:                                                                     # tableau des notes
    date_ref = f(next(iter(notes.values()))["date_ref"])
    bloc_notes = "\n".join([f"## 5. Notes (référence S&P 500 du {date_ref})", "", ent5, sep(ent5)] + l5)
else:
    bloc_notes = "## 5. Notes\n\nRéférence S&P 500 absente : à construire (étape b)."
texte = f"""# Cas de test : ratios, garde-fou, exclusions (généré par `tests/cas_de_test.py` le {D.strftime('%d/%m/%Y')})

Données Yahoo Finance du jour, mode direct. Notes finales : après la référence S&P 500 (étape b).

## 1. Données lues

{ent1}
{sep(ent1)}
{chr(10).join(l1)}

## 2. Ratios (définitions de la recherche, CHOIX.md §3)

{ent2}
{sep(ent2)}
{chr(10).join(l2)}

## 3. Croissances annuelles disponibles (nombre ; au moins 2 pour une note)

{ent3}
{sep(ent3)}
{chr(10).join(l3)}

## 4. Garde-fou (notes de -1 à +1 ; vert dès +0,33, rouge sous -0,33) et exclusions

{ent4}
{sep(ent4)}
{chr(10).join(l4)}

{bloc_notes}
"""
(Path(__file__).resolve().parent / "cas_de_test.md").write_text(texte, encoding="utf-8")
print("Tableau : tests/cas_de_test.md", flush=True)
