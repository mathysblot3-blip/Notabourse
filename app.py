"""Point d'entrée du site NotaBourse. Lancer en local : .venv\\Scripts\\python.exe -m streamlit run app.py

Ce fichier ne fait que régler la page, la langue et la navigation entre les deux pages (cahier des charges §5) :
  - vues/recherche.py : recherche d'une société et fiche de sa note (page principale) ;
  - vues/methode.py : la méthode, résumée ;
  - vues/mentions.py : les mentions légales.
"""
import streamlit as st  # interface web

from vues.commun import langue, pied_de_page, textes

st.set_page_config(page_title="NotaBourse", page_icon="⭐", layout="wide")  # titre de l'onglet, page large
langue()                                                                      # bouton FR / EN (français par défaut)
T = textes()                                                                  # textes dans la langue choisie
pages = [st.Page("vues/recherche.py", title=T["page_recherche"], icon="🔎", default=True),
         st.Page("vues/methode.py", title=T["page_methode"], icon="📘"),
         st.Page("vues/mentions.py", title=T["page_mentions"], icon="⚖️")]
st.navigation(pages).run()                                                    # affiche la page choisie
pied_de_page()                                                                # mentions obligatoires
