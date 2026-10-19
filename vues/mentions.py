"""Page Mentions légales (19/10/2026) : éditeur, hébergement, licence, avertissement financier, données personnelles et
cookies, droit applicable. Choix de Mathys : éditeur non professionnel anonyme (LCEN, article 1-1, II), contact par
GitHub, déclaration d'intérêts générale, cookies de l'hébergeur signalés.

Le texte est dans traductions/mentions_fr.md et traductions/mentions_en.md : on le corrige là, sans toucher au code.
"""
import streamlit as st  # interface web

from vues.commun import SITE, textes

T = textes()                                                                  # textes de la langue choisie
L = st.session_state.get("langue", "fr")                                      # « fr » ou « en »
st.title(T["page_mentions"])
texte = (SITE / "traductions" / f"mentions_{L}.md").read_text(encoding="utf-8")  # page écrite en Markdown
st.markdown(texte.replace("$", "\\$"))                                        # « $ » seul : pas une formule
