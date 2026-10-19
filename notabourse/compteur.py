"""Compteur des recherches (étape e) : ajoute une ligne dans la table Supabase « recherches » à chaque fiche affichée.

Discret : si Supabase n'est pas réglé, est mal réglé ou en panne, le site marche quand même et n'affiche aucune erreur.
L'envoi se fait en arrière-plan, pour ne pas ralentir la page.
Clé utilisée : la clé PUBLIQUE de Supabase (« publishable », ou l'ancienne « anon »), lue dans les secrets, jamais
écrite dans le code. Avec elle, la table accepte seulement des ajouts (supabase/creer_table.sql) [P] P7 du plan.
Rien n'est enregistré sur le visiteur : seulement la date, le symbole et le nom de la société [M] 19/10/2026.
"""
import os         # variables d'environnement
import threading  # envoi en arrière-plan

import requests   # requêtes HTTP vers Supabase

DELAI = 5         # secondes d'attente au plus pour Supabase


def reglages():
    """(adresse du projet, clé publique) lues dans l'environnement ou dans les secrets Streamlit ; None si absentes."""
    url, cle = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_CLE")    # 1. environnement
    if not (url and cle):
        try:
            import streamlit as st                                            # 2. secrets de Streamlit
            url, cle = st.secrets.get("SUPABASE_URL"), st.secrets.get("SUPABASE_CLE")
        except Exception:                                                     # pas de Streamlit ou pas de secrets
            return None
    if not (url and cle):
        return None                                                           # compteur non réglé : rien à faire
    return url.rstrip("/"), cle


def en_tetes(cle):
    """En-têtes de la requête. Une clé « publishable » (sb_publishable_...) va dans « apikey » ; l'ancienne clé
    « anon » est un jeton (il commence par eyJ) qu'on met aussi dans « Authorization »."""
    entetes = {"apikey": cle, "Content-Type": "application/json",
               "Prefer": "return=minimal"}                                    # ne rien renvoyer : la clé ne peut pas lire
    if cle.startswith("eyJ"):
        entetes["Authorization"] = f"Bearer {cle}"
    return entetes


def envoyer(symbole, nom, regl=None):
    """Ajoute une ligne. Renvoie le code HTTP (201 = ligne ajoutée), ou None si rien n'est réglé ou en cas d'erreur."""
    regl = regl or reglages()
    if regl is None:
        return None
    url, cle = regl[0].strip().rstrip("/"), regl[1].strip()                   # adresse sans « / » final
    if url.endswith("/rest/v1"):                                              # adresse de l'API copiée telle quelle
        url = url[: -len("/rest/v1")]                                         # (Supabase l'affiche ainsi) : on la retire
    ligne ={"symbole": str(symbole)[:20], "nom": str(nom)[:200] if nom else None}   # longueurs permises par la table
    try:
        return requests.post(f"{url}/rest/v1/recherches", json=ligne, headers=en_tetes(cle), timeout=DELAI).status_code
    except Exception:                                                         # réseau, Supabase en pause... : silence
        return None


def compter_recherche(symbole, nom):
    """Compte une recherche en arrière-plan (la page n'attend pas la réponse de Supabase)."""
    regl = reglages()                                                         # lus ici : les secrets se lisent mal
    if regl is None:                                                          # depuis un autre fil d'exécution
        return
    threading.Thread(target=envoyer, args=(symbole, nom, regl), daemon=True).start()
