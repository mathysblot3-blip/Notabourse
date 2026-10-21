"""Page Sources (20/10/2026) : articles du corpus, textes consultés, méthodes statistiques, méthodologies d'indices,
données, puis droits, licences et marques. Liste fournie par Mathys ; références contrôlées auprès de Crossref le
20/10/2026, versions lues relevées dans les PDF de Documentation/.

Le texte est dans traductions/sources_fr.md et traductions/sources_en.md : on le corrige là, sans toucher au code.
"""
import streamlit as st  # interface web

from vues.commun import SITE, textes

T = textes()                                                                  # textes de la langue choisie
L = st.session_state.get("langue", "fr")                                      # « fr » ou « en »
st.title(T["page_sources"])
texte = (SITE / "traductions" / f"sources_{L}.md").read_text(encoding="utf-8")   # page écrite en Markdown
st.markdown(texte.replace("$", "\\$"))                                        # « $ » seul : pas une formule
