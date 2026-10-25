"""Mail du samedi : envoie à Mathys les messages reçus par le bouton « Questions ? » depuis le dernier envoi
[M] 25/10/2026. Lancé chaque samedi par le robot GitHub (.github/workflows/reference_hebdo.yml), ou à la main.

Étapes :
  1. lit les messages pas encore envoyés dans la table Supabase « messages » (clé SECRÈTE de Supabase : elle seule peut
     lire la table) ;
  2. les envoie en un seul e-mail depuis l'adresse Gmail de Mathys vers elle-même (mot de passe d'application Google) ;
  3. marque ces messages comme envoyés, puis efface ceux de plus de 12 mois (durée annoncée dans les mentions légales).
Un mail part chaque semaine, même sans message, pour montrer que tout fonctionne [P].

Réglages lus dans l'environnement (secrets du dépôt GitHub, jamais dans le code) :
  SUPABASE_URL, SUPABASE_CLE_SECRETE, GMAIL_ADRESSE, GMAIL_MOT_DE_PASSE
Lancer à la main depuis le dossier site (après avoir défini ces quatre variables) :
  .venv\\Scripts\\python.exe supabase\\resume_messages.py
"""
import os                             # variables d'environnement
import smtplib                        # envoi d'e-mail
import sys                            # chemin d'import, code de sortie
from datetime import datetime, timedelta, timezone   # dates
from email.message import EmailMessage               # mise en forme de l'e-mail
from pathlib import Path              # chemins de fichiers

import requests                       # requêtes HTTP vers Supabase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))                 # dossier site
from notabourse.compteur import en_tetes  # noqa: E402  (mêmes en-têtes que le compteur)

DELAI = 30                            # secondes d'attente au plus pour Supabase
CONSERVATION = timedelta(days=365)    # messages effacés au bout de 12 mois [M] 25/10/2026
TYPES = {"question": "Question", "demande": "Demande", "erreur": "Erreur signalée"}


def reglages():
    """Les quatre réglages, ou None s'il en manque un (le robot s'arrête alors sans erreur)."""
    noms = ["SUPABASE_URL", "SUPABASE_CLE_SECRETE", "GMAIL_ADRESSE", "GMAIL_MOT_DE_PASSE"]
    valeurs = {n: (os.environ.get(n) or "").strip() for n in noms}
    manquants = [n for n, v in valeurs.items() if not v]
    if manquants:
        print("Réglages manquants : " + ", ".join(manquants) + ". Aucun mail envoyé.", flush=True)
        return None
    url = valeurs["SUPABASE_URL"].rstrip("/")
    if url.endswith("/rest/v1"):                                              # adresse de l'API copiée telle quelle
        url = url[: -len("/rest/v1")]
    valeurs["SUPABASE_URL"] = url
    return valeurs


def entetes_secrets(cle):
    """En-têtes avec la clé secrète : une clé « secret » (sb_secret_...) va dans « apikey » ; l'ancienne clé
    « service_role » est un jeton (eyJ...) qu'on met aussi dans « Authorization »."""
    entetes = en_tetes(cle)
    entetes["Prefer"] = "return=representation"                               # renvoyer les lignes concernées
    return entetes


def lire_nouveaux(r):
    """Messages pas encore envoyés, du plus ancien au plus récent."""
    rep = requests.get(f"{r['SUPABASE_URL']}/rest/v1/messages",
                       params={"envoye": "eq.false", "order": "cree_le.asc", "select": "*"},
                       headers=entetes_secrets(r["SUPABASE_CLE_SECRETE"]), timeout=DELAI)
    rep.raise_for_status()                                                    # erreur : le robot s'arrête, GitHub prévient
    return rep.json()


def texte_du_mail(messages, maintenant):
    """(objet, corps) de l'e-mail, en texte simple."""
    jour = maintenant.strftime("%d/%m/%Y")
    if not messages:
        return (f"Bourse à lunettes : aucun message cette semaine ({jour})",
                "Aucun message reçu par le bouton « Questions ? » depuis le dernier envoi.\n\n"
                "Ce mail part chaque samedi pour montrer que tout fonctionne.")
    lignes = []
    for i, m in enumerate(messages, 1):
        date = datetime.fromisoformat(m["cree_le"].replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
        email = m.get("email") or "pas d'e-mail laissé"
        lignes.append(f"{i}. {TYPES.get(m['type'], m['type'])} · {date} (heure UTC) · langue {m.get('langue') or '?'}"
                      f" · {email}\n{m['message']}\n")
    nb = len(messages)
    objet = f"Bourse à lunettes : {nb} message{'s' if nb > 1 else ''} ({jour})"
    corps = (f"{nb} message{'s' if nb > 1 else ''} reçu{'s' if nb > 1 else ''} par le bouton « Questions ? » depuis le "
             f"dernier envoi.\n\n" + "\n".join(lignes) +
             "\nPour répondre : écrire à l'adresse laissée par le visiteur. Messages effacés au bout de 12 mois.")
    return objet, corps


def envoyer_mail(r, objet, corps):
    """Envoie l'e-mail depuis le Gmail de Mathys vers lui-même (connexion chiffrée SSL, port 465)."""
    mail = EmailMessage()
    mail["Subject"], mail["From"], mail["To"] = objet, r["GMAIL_ADRESSE"], r["GMAIL_ADRESSE"]
    mail.set_content(corps)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=DELAI) as serveur:
        serveur.login(r["GMAIL_ADRESSE"], r["GMAIL_MOT_DE_PASSE"].replace(" ", ""))   # le mot de passe d'application
        serveur.send_message(mail)                                                    # s'affiche avec des espaces


def marquer_envoyes(r, messages):
    """Marque les messages envoyés, pour ne pas les renvoyer samedi prochain."""
    if not messages:
        return
    ids = ",".join(m["id"] for m in messages)
    rep = requests.patch(f"{r['SUPABASE_URL']}/rest/v1/messages", params={"id": f"in.({ids})"},
                         json={"envoye": True}, headers=entetes_secrets(r["SUPABASE_CLE_SECRETE"]), timeout=DELAI)
    rep.raise_for_status()


def effacer_anciens(r, maintenant):
    """Efface les messages de plus de 12 mois. Renvoie leur nombre."""
    limite = (maintenant - CONSERVATION).isoformat()
    rep = requests.delete(f"{r['SUPABASE_URL']}/rest/v1/messages", params={"cree_le": f"lt.{limite}"},
                          headers=entetes_secrets(r["SUPABASE_CLE_SECRETE"]), timeout=DELAI)
    rep.raise_for_status()
    return len(rep.json())


def main():
    r = reglages()
    if r is None:
        return 0                                                              # pas encore réglé : rien à faire
    maintenant = datetime.now(timezone.utc)
    messages = lire_nouveaux(r)
    objet, corps = texte_du_mail(messages, maintenant)
    envoyer_mail(r, objet, corps)                                             # d'abord le mail...
    marquer_envoyes(r, messages)                                              # ...puis seulement les marquer
    effaces = effacer_anciens(r, maintenant)
    print(f"Mail envoyé : {len(messages)} message(s) ; {effaces} message(s) de plus de 12 mois effacé(s).", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
