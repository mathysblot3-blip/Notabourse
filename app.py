"""Point d'entrée du site NotaBourse. Lancer en local : .venv\\Scripts\\python.exe -m streamlit run app.py

Ce fichier ne fait que régler la page, la langue et la navigation entre les pages (cahier des charges §5) :
  - vues/recherche.py : recherche d'une société et fiche de sa note (page principale) ;
  - vues/methode.py : la méthode, résumée ;
  - vues/tests.py : backtesting, ce qu'aurait donné la note sur le passé (portefeuille simulé, en échantillon) ;
  - vues/sources.py : les articles et les données sur lesquels repose la méthode ;
  - vues/mentions.py : les mentions légales.
"""
import streamlit as st  # interface web

from vues.commun import ICONE, bouton_questions, langue, logo, pied_de_page, style, textes

LOGO = logo()                                                                 # logo de Mathys, s'il est là
st.set_page_config(page_title="Bourse à lunettes", page_icon=LOGO or str(ICONE), layout="wide")  # onglet, page large
if LOGO:
    st.logo(LOGO, size="large")                                               # en haut du menu
style()                                                                       # couleurs et filets du site
zone_questions = st.sidebar.container()                                       # place réservée sous le menu
langue()                                                                      # bouton FR / EN (français par défaut)
with zone_questions:
    bouton_questions()                                                        # « Questions ? » [M] 25/10/2026
T = textes()                                                                  # textes dans la langue choisie
pages = [st.Page("vues/recherche.py", title=T["page_recherche"], default=True),
         st.Page("vues/methode.py", title=T["page_methode"]),
         st.Page("vues/tests.py", title=T["page_tests"]),
         st.Page("vues/sources.py", title=T["page_sources"]),
         st.Page("vues/mentions.py", title=T["page_mentions"])]   # sans émojis : menu numéroté 01 à 05 [M]
page = st.navigation(pages)
if page.title != T["page_recherche"]:
    st.session_state["accueil_vide"] = False                               # espace seulement sur l'accueil
page.run()                                                                    # affiche la page choisie
pied_de_page()                                                                # mentions obligatoires
