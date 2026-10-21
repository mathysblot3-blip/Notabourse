"""Tests du prix comparé au secteur (notabourse/prix.py), calcul repris de Recherche_score/36_per_secteur.py.
Lancer depuis le dossier site : .venv\\Scripts\\python.exe -m pytest tests/test_prix.py"""
import pandas as pd   # tableaux de données
import pytest         # outil de test

from notabourse import prix
from notabourse.prix import position_barre, prix_secteur


def reference(ep_secteur, ep_autres=(0.05, 0.05, 0.05, 0.05, 0.05)):
    """Petite référence : un secteur « BusEq » (E/P donnés) et un secteur « Hlth », tous dans le groupe NF."""
    lignes = [{"cik": f"A{i}", "groupe": "NF", "secteur": "BusEq", "EP": ep} for i, ep in enumerate(ep_secteur)]
    lignes += [{"cik": f"B{i}", "groupe": "NF", "secteur": "Hlth", "EP": ep} for i, ep in enumerate(ep_autres)]
    return pd.DataFrame(lignes).set_index("cik", drop=False)


def societe(ep, secteur="BusEq"):
    return {"cik": "X", "groupe": "NF", "secteur": secteur, "EP": ep}


def test_per_du_secteur_moyenne_harmonique():
    # PER des pairs : 10, 20, 40, 50 et 100 ; moyenne harmonique = 1 / moyenne(0,1 ; 0,05 ; 0,025 ; 0,02 ; 0,01)
    ref = reference([0.10, 0.05, 0.025, 0.02, 0.01])
    p = prix_secteur(societe(0.05), ref)
    assert p["per_secteur"] == pytest.approx(1 / 0.041)                       # 24,4 (la moyenne simple serait 44)
    assert p["nb_pairs"] == 5 and not p["repli_groupe"]


def test_les_pertes_sont_ecartees_du_secteur():
    ref = reference([0.05, 0.05, 0.05, 0.05, 0.05, -0.30, 0.0])              # une perte et un bénéfice nul
    p = prix_secteur(societe(0.05), ref)
    assert p["nb_pairs"] == 5 and p["per_secteur"] == pytest.approx(20.0)


def test_seuils_inclus():
    ref = reference([0.05] * 5)                                               # PER du secteur : 20
    assert prix_secteur(societe(1 / 25), ref)["verdict"] == "chere"           # 25 / 20 = 1,25 : chère (borne incluse)
    assert prix_secteur(societe(1 / 16), ref)["verdict"] == "bon_marche"      # 16 / 20 = 0,8 : bon marché (borne incluse)
    assert prix_secteur(societe(1 / 24.9), ref)["verdict"] == "norme"
    assert prix_secteur(societe(1 / 16.1), ref)["verdict"] == "norme"


def test_ecart_et_per():
    p = prix_secteur(societe(1 / 30), reference([0.05] * 5))
    assert p["per"] == pytest.approx(30) and p["ecart"] == pytest.approx(0.5)   # 30 / 20 - 1 = +50 %


def test_perte_de_la_societe():
    p = prix_secteur(societe(-0.02), reference([0.05] * 5))
    assert p["verdict"] == "pertes" and p["per"] is None and p["per_secteur"] == pytest.approx(20)


def test_moins_de_5_pairs_tout_le_groupe():
    ref = reference([0.10, 0.10, 0.10, -0.1], ep_autres=(0.05, 0.05, 0.05, 0.05, 0.05))   # 3 pairs bénéficiaires
    p = prix_secteur(societe(0.05), ref)
    assert p["repli_groupe"] and p["nb_pairs"] == 8                            # 3 + 5 membres bénéficiaires du groupe
    assert p["per_secteur"] == pytest.approx(1 / ((3 * 0.10 + 5 * 0.05) / 8))


def test_ancienne_reference_sans_colonne(monkeypatch):
    monkeypatch.setattr(prix, "table_secours", lambda: None)                   # pas de table de secours non plus
    ref = reference([0.05] * 5).drop(columns="EP")
    assert prix_secteur(societe(0.05), ref)["verdict"] == "reference_ancienne"


def test_ancienne_reference_table_de_secours(monkeypatch):
    secours = pd.DataFrame([{"groupe": "NF", "secteur": "BusEq", "date": "2026-10-21", "EP": 0.04, "nb_EP": 90,
                             "repli_EP": False, "SP": 0.2, "nb_SP": 95, "repli_SP": False}])
    monkeypatch.setattr(prix, "table_secours", lambda: secours)
    p = prix_secteur(societe(1 / 30), reference([0.05] * 5).drop(columns="EP"))
    assert p["per_secteur"] == pytest.approx(25) and p["secours"] == "2026-10-21" and not p["fiable"]


# --- Replis pour la société affichée [M] 21/10/2026 -------------------------------------------------------------------
def test_repli_dernier_exercice():
    s = {**societe(None), "EP_AFF": 1 / 30, "EP_ORIGINE": "exercice"}
    p = prix_secteur(s, reference([0.05] * 5))
    assert p["per"] == pytest.approx(30) and p["origine"] == "exercice" and not p["fiable"]


def test_repli_benefice_moyen_si_perte():
    s = {**societe(-0.01), "EP_AFF": 1 / 40, "EP_ORIGINE": "moyenne", "EP_NB_EXERCICES": 4}
    p = prix_secteur(s, reference([0.05] * 5))
    assert p["perte"] and p["origine"] == "moyenne" and p["nb_exercices"] == 4 and p["verdict"] == "chere"


def test_repli_ventes_si_perte_durable():
    ref = reference([0.05] * 5).assign(SP=0.25)                              # prix / ventes du secteur : 4
    s = {**societe(-0.01), "EP_AFF": -0.01, "EP_ORIGINE": "12_mois", "SP": 0.5}   # prix / ventes : 2
    p = prix_secteur(s, ref)
    assert p["mesure"] == "ventes" and p["per"] == pytest.approx(2) and p["per_secteur"] == pytest.approx(4)
    assert p["verdict"] == "bon_marche" and not p["fiable"]


def test_perte_sans_aucun_repli():
    p = prix_secteur({**societe(-0.01), "EP_AFF": -0.01, "EP_ORIGINE": "12_mois"}, reference([0.05] * 5))
    assert p["verdict"] == "pertes"


def test_cas_normal_fiable():
    assert prix_secteur(societe(0.05), reference([0.05] * 5))["fiable"]


def test_donnee_manquante():
    assert prix_secteur(societe(None), reference([0.05] * 5))["verdict"] == "manquant"


def test_barre_symetrique_et_bornee():
    assert position_barre(1.0) == pytest.approx(50)                           # comme le secteur : au milieu
    assert position_barre(1.25) == pytest.approx(100 - position_barre(0.8))   # seuils à la même distance du milieu
    assert position_barre(1.25) == pytest.approx(33.9, abs=0.05)
    assert position_barre(2.0) == pytest.approx(0) and position_barre(0.5) == pytest.approx(100)   # bords
    assert position_barre(11.0) == 0 and position_barre(0.1) == 100           # au-delà : collé au bord
    assert position_barre(None) is None


def test_repli_benefice_quasi_nul_passe_aux_ventes():
    ref = reference([0.05] * 5).assign(SP=0.25)
    s = {**societe(-0.15), "EP_AFF": 0.0003, "EP_ORIGINE": "moyenne", "EP_NB_EXERCICES": 4, "SP": 3.9}   # PER 3 000
    p = prix_secteur(s, ref)
    assert p["mesure"] == "ventes" and p["verdict"] == "bon_marche"
