"""Page Méthode (cahier des charges §5) : la note, les quatre parties, le garde-fou, la comparaison au S&P 500, les
adaptations aux données Yahoo, le test d'acceptation et les limites. Sans chiffres de performance du backtest (choix de
Mathys).

Le texte est dans traductions/methode_fr.md et traductions/methode_en.md : on le corrige là, sans toucher au code.
"""
import streamlit as st  # interface web

from vues.commun import SITE, textes

T = textes()                                                                  # textes de la langue choisie
L = st.session_state.get("langue", "fr")                                      # « fr » ou « en »
st.title(T["page_methode"])
texte = (SITE / "traductions" / f"methode_{L}.md").read_text(encoding="utf-8")   # page écrite en Markdown
st.markdown(texte.replace("$", "\\$"))                                        # « $ » seul : pas une formule
