"""Tests des indices affichés sur la fiche (notabourse/indices.py)."""
from notabourse.indices import cle_nom, indices_de


def test_toyota_est_au_nikkei():
    assert "Nikkei 225" in indices_de("7203.T", "Toyota Motor Corporation")


def test_societe_reconnue_par_son_nom_sur_une_autre_cotation():
    # Allianz : ALV.DE dans la liste du DAX, ALV.VI dans le classement
    assert "DAX" in indices_de("ALV.VI", "Allianz SE")


def test_societe_sans_indice():
    assert indices_de("ZZZZ.ZZ", "Société inconnue") == []


def test_nom_simplifie():
    assert cle_nom("ASML Holding N.V.") == "asml"
