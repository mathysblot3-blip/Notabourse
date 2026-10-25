"""Messages des visiteurs (bouton « Questions ? » du menu) : questions, demandes et erreurs signalées [M] 25/10/2026.

Le message est vérifié ici, puis ajouté dans la table Supabase « messages » avec la clé PUBLIQUE du site (la même que
le compteur des recherches) : cette clé peut seulement ajouter, jamais lire (supabase/creer_table_messages.sql).
Chaque samedi, le robot GitHub les lit avec la clé secrète et les envoie par e-mail à Mathys
(supabase/resume_messages.py). Sans chiffre ni Streamlit ici : testable avec pytest.
"""
import re         # forme d'une adresse e-mail

import requests   # requêtes HTTP vers Supabase

from notabourse.compteur import DELAI, en_tetes, reglages

TYPES = ("question", "demande", "erreur")       # les trois sortes de messages, comme dans la table
LONGUEUR_MIN, LONGUEUR_MAX = 5, 2000            # longueur permise du message (mêmes bornes que la table) [P]
EMAIL_MAX = 200                                 # longueur maximale de l'adresse (idem)
MESSAGES_PAR_VISITE = 3                         # au plus 3 messages par visite, contre les envois en rafale [P]
FORME_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")   # quelque chose@quelque chose.quelque chose


def verifier(type_, texte, email):
    """Contrôle un message avant l'envoi. Renvoie (ligne prête à envoyer, None) si tout va bien, sinon (None, clé du
    texte d'erreur à montrer au visiteur)."""
    texte = (texte or "").strip()
    email = (email or "").strip()
    if type_ not in TYPES:
        return None, "msg_erreur_type"
    if len(texte) < LONGUEUR_MIN:
        return None, "msg_erreur_court"
    if len(texte) > LONGUEUR_MAX:
        return None, "msg_erreur_long"
    if email and (len(email) > EMAIL_MAX or not FORME_EMAIL.match(email)):
        return None, "msg_erreur_email"
    return {"type": type_, "message": texte, "email": email or None}, None


def envoyer_message(ligne, langue, regl=None):
    """Ajoute le message dans Supabase. Renvoie True s'il est bien enregistré, False sinon (Supabase non réglé, en
    panne ou refus) : le visiteur est alors prévenu que l'envoi a échoué."""
    regl = regl or reglages()
    if regl is None:
        return False
    url, cle = regl[0].strip().rstrip("/"), regl[1].strip()
    if url.endswith("/rest/v1"):                                              # adresse de l'API copiée telle quelle
        url = url[: -len("/rest/v1")]
    try:
        r = requests.post(f"{url}/rest/v1/messages", json={**ligne, "langue": langue},
                          headers=en_tetes(cle), timeout=DELAI)
        return r.status_code == 201                                           # 201 = ligne ajoutée
    except Exception:                                                         # réseau, Supabase en pause...
        return False
