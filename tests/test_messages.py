r"""Tests du bouton « Questions ? » (notabourse/messages.py) et du mail du samedi (supabase/resume_messages.py).
Aucun accès au réseau : Supabase et Gmail ne sont jamais appelés ici.
Lancer depuis le dossier site : .venv\Scripts\python.exe -m pytest tests/test_messages.py"""
import importlib.util                 # charger le script du robot comme un module
from datetime import datetime, timezone
from pathlib import Path

from notabourse import messages
from notabourse.messages import LONGUEUR_MAX, envoyer_message, verifier

SITE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("resume_messages", SITE / "supabase" / "resume_messages.py")
resume = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resume)


# --- Contrôles avant l'envoi -------------------------------------------------------------------------------------------
def test_message_correct_sans_email():
    ligne, erreur = verifier("question", "  Comment est calculée la note ?  ", "")
    assert erreur is None and ligne == {"type": "question", "message": "Comment est calculée la note ?", "email": None}


def test_message_correct_avec_email():
    ligne, erreur = verifier("erreur", "Le chiffre d'affaires d'Apple est faux.", " nom@exemple.fr ")
    assert erreur is None and ligne["email"] == "nom@exemple.fr"


def test_message_trop_court_ou_trop_long():
    assert verifier("demande", "abc", "")[1] == "msg_erreur_court"
    assert verifier("demande", "x" * (LONGUEUR_MAX + 1), "")[1] == "msg_erreur_long"


def test_email_invalide():
    for email in ("nom", "nom@exemple", "nom @exemple.fr", "a@b.c" + "x" * 200):
        assert verifier("question", "Une vraie question.", email)[1] == "msg_erreur_email"


def test_type_inconnu():
    assert verifier("pub", "Achetez mes produits.", "")[1] == "msg_erreur_type"


def test_envoi_impossible_sans_reglages(monkeypatch):
    monkeypatch.setattr(messages, "reglages", lambda: None)                    # Supabase non réglé
    ligne, _ = verifier("question", "Une vraie question.", "")
    assert envoyer_message(ligne, "fr") is False                               # le visiteur sera prévenu


# --- Mail du samedi ----------------------------------------------------------------------------------------------------
MAINTENANT = datetime(2026, 10, 31, 6, 0, tzinfo=timezone.utc)


def test_mail_sans_message():
    objet, corps = resume.texte_du_mail([], MAINTENANT)
    assert "aucun message" in objet and "31/10/2026" in objet and "fonctionne" in corps


def test_mail_avec_messages():
    lignes = [{"id": "1", "cree_le": "2026-10-26T09:15:00+00:00", "type": "question", "message": "Pourquoi 50 ?",
               "email": None, "langue": "fr"},
              {"id": "2", "cree_le": "2026-10-27T18:00:00Z", "type": "erreur", "message": "Chiffre faux.",
               "email": "nom@exemple.fr", "langue": "en"}]
    objet, corps = resume.texte_du_mail(lignes, MAINTENANT)
    assert "2 messages" in objet
    assert "1. Question · 26/10/2026 09:15" in corps and "pas d'e-mail laissé" in corps and "Pourquoi 50 ?" in corps
    assert "2. Erreur signalée · 27/10/2026 18:00" in corps and "nom@exemple.fr" in corps


def test_robot_sans_reglages_ne_fait_rien(monkeypatch):
    for nom in ("SUPABASE_URL", "SUPABASE_CLE_SECRETE", "GMAIL_ADRESSE", "GMAIL_MOT_DE_PASSE"):
        monkeypatch.delenv(nom, raising=False)
    assert resume.reglages() is None and resume.main() == 0                    # aucun appel réseau, pas d'échec


def test_robot_lit_les_secrets_du_depot():
    robot = (SITE / ".github" / "workflows" / "reference_hebdo.yml").read_text(encoding="utf-8")
    for nom in ("SUPABASE_URL", "SUPABASE_CLE_SECRETE", "GMAIL_ADRESSE", "GMAIL_MOT_DE_PASSE"):
        assert f"{nom}: ${{{{ secrets.{nom} }}}}" in robot                    # jamais de valeur écrite en clair
