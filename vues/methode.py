"""Page Méthode (cahier des charges §5) : textes à rédiger après le test d'acceptation (étape d)."""
import streamlit as st  # interface web

from vues.commun import textes

T = textes()
st.title(T["page_methode"])
st.info(T["methode_bientot"])
