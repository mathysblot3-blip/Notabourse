"""Tests des phrases simples de la fiche (notabourse/phrases.py) et des textes traduits.
Lancer depuis le dossier site : .\\.venv\\Scripts\\python.exe -m pytest tests
"""
import json            # lecture des fichiers de textes
from pathlib import Path

import pytest          # outil de test

from notabourse.phrases import _mediane, _taux, phrases, phrases_bilan, phrases_croissance, rendre, sante

SITE = Path(__file__).resolve().parents[1]
T = {lg: json.loads((SITE / "traductions" / f"{lg}.json").read_text(encoding="utf-8")) for lg in ("fr", "en")}


# --- Fiches fabriquées à la main (seules les clés lues par phrases.py) -------------------------------------------------
def voyant(nom, note, **mesure):
    """Un voyant du garde-fou avec sa mesure."""
    return {"voyant": nom, "note": note, "mesure": mesure}


def fiche(groupe="NF", voyants=None, exclue=False, conditions=None, composantes=None, note=60.0):
    """Fiche minimale : groupe, note, parties, garde-fou."""
    if voyants is None:                                                       # industrie en bonne santé par défaut
        voyants = [voyant("trésorerie", 1.0, flux_positif=True, annees=None),
                   voyant("endettement", 1.0, tlmta=0.30),
                   voyant("intérêts", 1.0, couverture=8.0, sans_interets=False, ebitda_negatif=False)]
    conditions = conditions or [{"condition": "garde_fou", "remplie": True}, {"condition": "benefices", "remplie": True},
                                {"condition": "fonds_propres", "remplie": True}]
    return {"groupe": groupe, "note": {"sur_100": note}, "composantes": composantes or [],
            "garde_fou": {"voyants": voyants, "exclue": exclue, "conditions": conditions}}


def textes(liste, lg="fr"):
    """Phrases rendues dans une langue."""
    return [rendre(p, T[lg], lg) for p in liste]


# --- Textes ------------------------------------------------------------------------------------------------------------
def test_memes_textes_en_francais_et_en_anglais():
    assert set(T["fr"]) == set(T["en"])


# --- Point de vigilance (seuils de Mathys, affichage seulement) --------------------------------------------------------
@pytest.mark.parametrize("tlmta, statut", [(0.65, "vigilance"), (0.60, "vigilance"), (0.55, "bonne")])
def test_vigilance_dettes(tlmta, statut):
    v = [voyant("trésorerie", 1.0, flux_positif=True, annees=None), voyant("endettement", 1.0, tlmta=tlmta),
         voyant("intérêts", 1.0, couverture=8.0, sans_interets=False, ebitda_negatif=False)]
    assert sante(fiche(voyants=v))["statut"] == statut


@pytest.mark.parametrize("couverture, statut", [(3.5, "vigilance"), (4.5, "bonne")])
def test_vigilance_interets(couverture, statut):
    v = [voyant("intérêts", 1.0, couverture=couverture, sans_interets=False, ebitda_negatif=False)]
    assert sante(fiche(voyants=v))["statut"] == statut


def test_vigilance_tresorerie_et_financieres():
    flux_negatif = [voyant("trésorerie", 1.0, flux_positif=False, annees=3.0)]
    assert sante(fiche(voyants=flux_negatif))["statut"] == "vigilance"
    peu = [voyant("fonds propres / actif", 1.0, ratio=0.05)]
    assez = [voyant("fonds propres / actif", 1.0, ratio=0.07)]
    assert sante(fiche("FIN", voyants=peu))["statut"] == "vigilance"
    assert sante(fiche("FIN", voyants=assez))["statut"] == "bonne"


@pytest.mark.parametrize("note, couleur_formule, tlmta, attendu", [
    (1.0, "vert", 0.30, "vert"),       # peu de dettes : vert
    (1.0, "vert", 0.65, "orange"),     # vert pour la formule, mais seuil de vigilance franchi : montré orange
    (0.0, "orange", 0.85, "orange"),   # orange de la formule : orange
    (-0.5, "rouge", 0.95, "rouge"),    # rouge de la formule : rouge
])
def test_couleur_affichee_elargit_l_orange(note, couleur_formule, tlmta, attendu):
    from notabourse.phrases import couleur_affichage
    v = {"voyant": "endettement", "note": note, "couleur": couleur_formule, "mesure": {"tlmta": tlmta}}
    assert couleur_affichage(v) == attendu


def test_moyenne_montree_orange_sans_exclusion():
    from notabourse.phrases import couleur_moyenne_affichage
    v = [{"voyant": "endettement", "note": 1.0, "couleur": "vert", "mesure": {"tlmta": 0.65}}]
    f = fiche(voyants=v)
    f["garde_fou"]["couleur"] = "vert"                                        # la formule : vert, pas d'exclusion
    assert couleur_moyenne_affichage(f) == "orange"


def test_exclusion_avant_vigilance():
    cond = [{"condition": "garde_fou", "remplie": True}, {"condition": "benefices", "remplie": False},
            {"condition": "fonds_propres", "remplie": True}]
    s = sante(fiche(exclue=True, conditions=cond))
    assert s["statut"] == "exclue" and s["phrases"][0]["cle"] == "sante_exclue_benefices"


# --- Bilan : points forts et points faibles ----------------------------------------------------------------------------
def detail(ratio, valeur, centile):
    """Un ratio du détail d'une partie."""
    return {"ratio": ratio, "valeur": valeur, "centile": centile, "moyenne_secteur": None, "mediane_secteur": None}


def test_bilan_cite_les_ratios_en_cause():
    c = {"code": "R2", "nom": "bilan", "note": 75.0,
         "detail": [detail("TLMTA", 0.2, 90.0), detail("CASHMTA", 0.01, 10.0), detail("TAILLE", 5e11, 95.0)]}
    texte = [t.replace(" ", " ") for t in textes(phrases_bilan(fiche(), c))]   # espaces insécables lues comme des espaces
    assert texte[0] == "Bilan solide : peu de dettes et une très grande taille, mais peu de trésorerie de côté."
    assert texte[1].startswith("Sa trésorerie représente 1 %")


def test_bilan_fragile_malgre_un_point_fort():
    c = {"code": "R2", "nom": "bilan", "note": 15.0,
         "detail": [detail("TLMTA", 0.8, 5.0), detail("CASHMTA", 0.05, 50.0), detail("TAILLE", 5e11, 95.0)]}
    assert textes(phrases_bilan(fiche(), c), "en")[0] == "Fragile balance sheet: a lot of debt, despite a very large size."


# --- Croissance : valeur typique et bornes -----------------------------------------------------------------------------
def test_mediane_resiste_a_une_annee_hors_norme():
    assert _mediane([0.10, 9.0, 0.05]) == 0.10
    assert _mediane([0.10, 0.20]) == pytest.approx(0.15)
    assert _mediane([]) is None


def test_taux_borne_a_100_pourcents():
    assert _taux(2.5, "fr") == "> +100 %"                                # espace insécable avant « % »
    assert _taux(-3.0, "en") == "< −100%"                                # vrai signe moins
    assert _taux(0.123, "fr") == "+12,3 %"


def test_croissance_ventes_en_hausse_resultat_en_baisse():
    c = {"code": "G1", "nom": "croissance", "note": 50.0,
         "croissances": {"GS_CA": [0.10, 0.08, 0.12], "GS_EBITDA": [-0.20, -0.05, 0.03]}}
    assert phrases_croissance(fiche(), c)[0]["cle"] == "croiss_marges"


# --- Toutes les fiches du S&P 500 : aucune phrase ne manque, dans les deux langues -----------------------------------
def test_toutes_les_fiches_des_membres_se_lisent():
    from notabourse.calcul import charger_reference
    from notabourse.fiche import fiche_membre
    ref, cr = charger_reference()
    for s in ref.index:
        P = phrases(fiche_membre(s, ref, cr))
        for partie, liste in P.items():
            for p in (liste["phrases"] if partie == "sante" else liste):
                for lg in ("fr", "en"):
                    assert rendre(p, T[lg], lg)                               # texte non vide, aucune clé manquante


# --- Détail chiffré : le rang affiché suit la note --------------------------------------------------------------------
def test_rang_affiche_redonne_la_note_de_rentabilite():
    """Rentabilité : note = 100 x (rang - 5 %) / 90 %, bornée ; le rang affiché doit redonner la note exacte."""
    from notabourse.calcul import charger_reference
    from notabourse.fiche import fiche_membre
    ref, cr = charger_reference()
    for s in ref.index[:120]:                                                 # 120 membres suffisent (rapide)
        c = fiche_membre(s, ref, cr)["composantes"][0]                        # rentabilité
        if c["note"] is None or c["detail"][0]["centile"] is None:
            continue
        refaite = 100 * min(1, max(0, (c["detail"][0]["centile"] / 100 - 0.05) / 0.90))
        assert refaite == pytest.approx(c["note"], abs=1e-9)


# --- Page Méthode : mêmes parties en français et en anglais ------------------------------------------------------------
def test_page_methode_meme_structure_dans_les_deux_langues():
    pages = {lg: (SITE / "traductions" / f"methode_{lg}.md").read_text(encoding="utf-8") for lg in ("fr", "en")}
    titres = {lg: [l for l in p.splitlines() if l.startswith("### ")] for lg, p in pages.items()}
    lignes_tableau = {lg: sum(l.startswith("|") for l in p.splitlines()) for lg, p in pages.items()}
    assert len(titres["fr"]) == len(titres["en"]) == 9                       # « En bref » + 8 parties (prix comparé au secteur et rôle de l'IA ajoutés le 21/10/2026)
    assert lignes_tableau["fr"] == lignes_tableau["en"]
    assert "—" not in pages["fr"] + pages["en"]                               # règle de rédaction : pas de tiret cadratin
