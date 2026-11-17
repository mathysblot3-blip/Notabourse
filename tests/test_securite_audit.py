r"""Tests des protections ajoutées après l'audit du 17/11/2026 (constats S-C01, S-C03, S-C04, S-C05 et 4.4).
Lancer depuis le dossier site : .\.venv\Scripts\python.exe -m pytest tests/test_securite_audit.py
"""
import importlib.util   # charger le script du mail sans le lancer
from pathlib import Path

import certifi          # fichier des autorités de certification
import pandas as pd     # tableaux

import notabourse       # noqa: F401  (le paquet applique le correctif des certificats à l'import)
from notabourse.limites import Compteur, MemoireEchecs

SITE = Path(__file__).resolve().parents[1]


def test_compteur_global_plafonne_puis_libere():
    c = Compteur(maximum=3, fenetre=60)
    assert [c.autoriser(t) for t in (0, 1, 2, 3)] == [True, True, True, False]   # 4e demande refusée
    assert c.autoriser(61)                                                    # la 1re est sortie de la fenêtre


def test_memoire_des_echecs_cinq_minutes():
    m = MemoireEchecs(duree=300)
    m.noter("apple", 1000)
    assert m.recent("apple", 1200) and not m.recent("apple", 1300) and not m.recent("autre", 1200)


def fonction_classement_valide():
    """Lit classement_valide dans la page sans la lancer (vues/classement.py est une page Streamlit)."""
    code = (SITE / "vues" / "classement.py").read_text(encoding="utf-8")
    debut, fin = code.index("COLONNES_CLASSEMENT ="), code.index("@st.cache_data(ttl=3600")
    espace = {"pd": pd}
    exec(code[debut:fin], espace)                                             # on ne compile que ce morceau
    return espace["classement_valide"], espace["COLONNES_CLASSEMENT"]


def test_classement_incomplet_refuse():
    valide, colonnes = fonction_classement_valide()
    bon = pd.DataFrame({c: [1.0] for c in colonnes})
    assert valide(bon)
    assert not valide(bon.drop(columns=["note"]))                             # colonne manquante
    assert not valide(bon.assign(note=float("nan")))                          # aucune société notée
    assert not valide(None)


def test_mail_avertit_et_reste_borne():
    spec = importlib.util.spec_from_file_location("resume_messages", SITE / "supabase" / "resume_messages.py")
    resume = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resume)
    ligne = {"id": "1", "cree_le": "2026-10-26T09:15:00+00:00", "type": "question", "message": "Bonjour",
             "email": None, "langue": "fr"}
    _, corps = resume.texte_du_mail([ligne], pd.Timestamp("2026-10-31"))
    assert corps.startswith(resume.AVERTISSEMENT) and 0 < resume.MAX_PAR_MAIL <= 500


def test_certificats_sans_accent():
    chemin = certifi.where()
    assert Path(chemin).exists() and chemin.isascii()                          # yfinance peut lire le fichier
