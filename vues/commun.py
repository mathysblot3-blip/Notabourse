"""Éléments communs aux pages du site : langue, textes, formats des nombres, pied de page."""
import json                # lecture des fichiers de textes
from pathlib import Path   # chemins de fichiers

import streamlit as st    # interface web

from notabourse.formats import date, dollars, nombre, pct   # noqa: F401  (formats des nombres, repris par les pages)

SITE = Path(__file__).resolve().parents[1]                                    # dossier site
URL_ISSUES = "https://github.com/OWNER/notabourse/issues"                    # à remplacer quand le dépôt existera (étape d)


@st.cache_data
def _charger_textes(langue, signature):
    """Textes de l'interface dans une langue (traductions/fr.json ou en.json), gardés en mémoire ; `signature` (date de
    modification du fichier) force la relecture quand le fichier change."""
    return json.loads((SITE / "traductions" / f"{langue}.json").read_text(encoding="utf-8"))


def langue():
    """Langue choisie par le visiteur : français par défaut [M], bouton dans la barre latérale."""
    if "langue" not in st.session_state:
        st.session_state["langue"] = "fr"                                     # premier passage : français
    choix = st.sidebar.segmented_control("Langue / Language", ["FR", "EN"],
                                         default=st.session_state["langue"].upper(), key="choix_langue")
    if choix:                                                                 # un clic sur le bouton déjà choisi le vide
        st.session_state["langue"] = choix.lower()
    return st.session_state["langue"]


def textes():
    """Dictionnaire des textes de la langue choisie."""
    lg = st.session_state.get("langue", "fr")
    return _charger_textes(lg, (SITE / "traductions" / f"{lg}.json").stat().st_mtime)


def pied_de_page():
    """Mentions obligatoires (cahier des charges §6), en bas de chaque page."""
    T = textes()
    st.divider()
    st.caption(f"{T['mention_conseil']}  \n{T['mention_recherche']}  \n{T['mention_donnees']}  \n"
               f"{T['mention_auteur']} · [{T['signaler']}]({URL_ISSUES})")
