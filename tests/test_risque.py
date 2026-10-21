r"""Tests de la barre du risque de faillite (notabourse/risque.py), affichage seulement.
Lancer depuis le dossier site : .venv\Scripts\python.exe -m pytest tests/test_risque.py"""
from notabourse.fiche import _garde_fou
from notabourse.risque import note_affichee, position_risque

BON = {"garde_fou": 1.0, "garde_fou_ok": True, "benefices_ok": True, "fonds_propres_ok": True, "gardee": True}


def fiche(tlmta=0.10, couverture=20.0, flux_positif=True, annees=None, exclusion=BON, notes=None):
    """Petite fiche d'une société industrielle : trois voyants et leurs mesures."""
    notes = notes or {"trésorerie": 1.0, "endettement": 1.0, "intérêts": 1.0}
    mesures = {"trésorerie": {"annees": annees, "flux_positif": flux_positif}, "endettement": {"tlmta": tlmta},
               "intérêts": {"couverture": couverture, "sans_interets": False, "ebitda_negatif": False},
               "benefices_inconnus": False}
    return {"groupe": "NF", "garde_fou": _garde_fou("NF", notes, mesures, exclusion)}


def test_saine_dans_le_vert():
    pos, statut = position_risque(fiche())
    assert statut == "bonne" and pos > 200 / 3


def test_point_de_vigilance_dans_l_orange():
    pos, statut = position_risque(fiche(tlmta=0.70))                          # 70 % de dettes : seuil d'affichage 60 %
    assert statut == "vigilance" and 100 / 3 < pos < 200 / 3


def test_plus_de_dettes_plus_a_gauche():
    assert position_risque(fiche(tlmta=0.85))[0] < position_risque(fiche(tlmta=0.65))[0]


def test_exclue_dans_le_rouge():
    exclue = {**BON, "benefices_ok": False, "gardee": False}                  # perte sur un des deux derniers exercices
    pos, statut = position_risque(fiche(exclusion=exclue))
    assert statut == "exclue" and pos < 100 / 3


def test_flux_negatif_jamais_vert():
    v = {"voyant": "trésorerie", "note": 1.0, "mesure": {"annees": 5.0, "flux_positif": False}}
    assert note_affichee(v) < 1 / 3                                           # 5 ans de trésorerie, mais l'activité
    pos, statut = position_risque(fiche(flux_positif=False, annees=5.0))      # consomme de l'argent : orange
    assert statut == "vigilance" and pos < 200 / 3


def test_etat_inconnu_sans_barre():
    f = fiche(notes={"trésorerie": None, "endettement": None, "intérêts": None})
    assert position_risque(f) == (None, "inconnue")
