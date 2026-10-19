"""Tests du compteur Supabase (notabourse/compteur.py), sans Internet : la requête est interceptée.
Lancer depuis le dossier site : .\\.venv\\Scripts\\python.exe -m pytest tests
"""
from notabourse import compteur


class Reponse:
    """Fausse réponse HTTP."""
    status_code = 201


def test_envoi_avec_cle_publishable(monkeypatch):
    appels = []
    monkeypatch.setattr(compteur.requests, "post", lambda url, **k: appels.append((url, k)) or Reponse())
    code = compteur.envoyer("AAPL", "Apple Inc.", ("https://exemple.supabase.co/", "sb_publishable_abc"))
    url, k = appels[0]
    assert code == 201
    assert url == "https://exemple.supabase.co/rest/v1/recherches"
    assert k["json"] == {"symbole": "AAPL", "nom": "Apple Inc."}
    assert k["headers"]["apikey"] == "sb_publishable_abc" and "Authorization" not in k["headers"]
    assert k["headers"]["Prefer"] == "return=minimal"                         # la clé ne peut pas relire la ligne


def test_adresse_de_l_api_copiee_telle_quelle(monkeypatch):
    appels = []
    monkeypatch.setattr(compteur.requests, "post", lambda url, **k: appels.append(url) or Reponse())
    compteur.envoyer("AAPL", "Apple", ("https://exemple.supabase.co/rest/v1/", "sb_publishable_abc"))
    assert appels[0] == "https://exemple.supabase.co/rest/v1/recherches"


def test_ancienne_cle_anon_aussi_en_authorization():
    assert compteur.en_tetes("eyJhbGciOi")["Authorization"] == "Bearer eyJhbGciOi"


def test_longueurs_coupees_comme_la_table(monkeypatch):
    appels = []
    monkeypatch.setattr(compteur.requests, "post", lambda url, **k: appels.append(k) or Reponse())
    compteur.envoyer("X" * 50, "N" * 500, ("https://e.supabase.co", "sb_publishable_abc"))
    assert len(appels[0]["json"]["symbole"]) == 20 and len(appels[0]["json"]["nom"]) == 200


def test_panne_de_supabase_sans_erreur(monkeypatch):
    def panne(*a, **k):
        raise ConnectionError("Supabase en panne")
    monkeypatch.setattr(compteur.requests, "post", panne)
    assert compteur.envoyer("AAPL", "Apple", ("https://e.supabase.co", "sb_publishable_abc")) is None


def test_rien_n_est_envoye_sans_reglages(monkeypatch):
    monkeypatch.setattr(compteur, "reglages", lambda: None)
    monkeypatch.setattr(compteur.requests, "post", lambda *a, **k: (_ for _ in ()).throw(AssertionError("envoi")))
    assert compteur.envoyer("AAPL", "Apple") is None
    compteur.compter_recherche("AAPL", "Apple")                               # ne fait rien, sans erreur
