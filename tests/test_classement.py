"""Tests du classement mondial (reference/construire_classement.py) : doublons, échecs, membres à part."""
import sys                   # chemin d'import
from pathlib import Path     # chemins de fichiers

import pandas as pd          # tableaux de données

SITE = Path(__file__).resolve().parents[1]                                    # dossier du site
sys.path.insert(0, str(SITE / "reference"))
sys.path.insert(0, str(SITE))
import construire_classement as cc  # noqa: E402


def test_meme_societe_cotee_deux_fois_reconnue():
    # « ASML Holding N.V. » et « ASML Holding NV » : la même clé, donc une seule ligne dans l'univers
    assert cc.cle_nom("ASML Holding N.V.") == cc.cle_nom("ASML Holding NV") == "asml"
    assert cc.cle_nom("Toyota Motor Corporation") != cc.cle_nom("Honda Motor Co., Ltd.")


def _univers(*symboles):
    return pd.DataFrame({"symbole": list(symboles)})


def test_un_echec_ne_remplace_jamais_une_note_valable():
    ancienne = {k: None for k in cc.COLONNES}
    ancienne.update({"symbole": "AAA", "note": 80.0, "membre": False, "date_lecture": pd.Timestamp("2026-11-01"),
                     "date_essai": pd.Timestamp("2026-11-01")})
    t = cc.assembler(pd.DataFrame([ancienne]), [{"symbole": "AAA", "date_essai": pd.Timestamp("2026-11-04"),
                                                 "echec": True}], [], _univers("AAA"))
    ligne = t.set_index("symbole").loc["AAA"]
    assert ligne["note"] == 80.0                                              # la note reste
    assert ligne["date_essai"] == pd.Timestamp("2026-11-04")                  # l'essai raté est daté


def test_societe_sortie_de_l_univers_retiree_et_membres_ajoutes():
    vieille = {k: None for k in cc.COLONNES}
    vieille.update({"symbole": "OLD", "note": 50.0, "membre": False})
    membre = {k: None for k in cc.COLONNES}
    membre.update({"symbole": "AAPL", "note": 70.0, "membre": True})
    t = cc.assembler(pd.DataFrame([vieille]), [], [membre], _univers("NEW"))
    assert set(t["symbole"]) == {"AAPL"}                                      # OLD n'est plus dans l'univers
    assert bool(t["membre"].iloc[0])


def test_echec_d_une_societe_jamais_lue_garde_une_ligne_relisible():
    # une société ratée à sa première lecture : ligne « erreur » sans note, case « membre » vide mais lisible
    t = cc.assembler(pd.DataFrame(columns=cc.COLONNES), [{"symbole": "NEW", "date_essai": pd.Timestamp("2026-11-04"),
                                                          "echec": True}], [], _univers("NEW"))
    assert t.loc[0, "statut"] == "erreur" and pd.isna(t.loc[0, "note"])
    assert not t["membre"].fillna(False).astype(bool).any()                   # ce que lisent la page et le robot


def test_capitalisation_en_pence_non_divisee():
    # Yahoo donne la capitalisation en livres même si le cours est en pence : seul le cours est divisé par 100
    assert cc.CENTIMES["GBp"] == ("GBP", 100)
    assert cc.dollars_par_unite("USD") == 1.0
