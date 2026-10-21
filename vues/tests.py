"""Page « Backtesting » (20/10/2026, d'abord « Tests sur le passé ») : ce qu'aurait donné la note de 2010 à 2026 avec un portefeuille simulé,
résultats décevants compris. Graphiques et chiffres produits par la recherche (`Recherche_score/35_preuves_site.py`,
chiffres exacts dans `preuves_site/chiffres.json`), copiés dans images/tests/ ; aucune formule modifiée.

Le texte est dans traductions/tests_fr.md et traductions/tests_en.md. Une ligne {{graphique:NOM}} y place l'image
images/tests/NOM_fr.png (ou _en), suivie de l'avertissement obligatoire sur les performances simulées ;
{{graphique:NOM:sans_avertissement}} place l'image seule (graphique qui ne montre pas une performance).
"""
import re               # repérage des lignes {{graphique:...}}

import streamlit as st  # interface web

from vues.commun import SITE, textes

T = textes()                                                                  # textes de la langue choisie
L = st.session_state.get("langue", "fr")                                      # « fr » ou « en »
GRAPHIQUE = re.compile(r"^\{\{graphique:(\w+)(:sans_avertissement)?\}\}$")   # ligne qui appelle une image

st.title(T["page_tests"])
texte = (SITE / "traductions" / f"tests_{L}.md").read_text(encoding="utf-8")  # page écrite en Markdown
morceau = []                                                                  # texte en attente d'affichage
for ligne in texte.splitlines() + [""]:
    g = GRAPHIQUE.match(ligne.strip())
    if g is None:
        morceau.append(ligne)
        continue
    st.markdown("\n".join(morceau).replace("$", "\\$"))                       # texte avant l'image (« $ » : pas une formule)
    morceau = []
    st.image(str(SITE / "images" / "tests" / f"{g.group(1)}_{L}.png"), width=900)   # graphique (réduit sur téléphone)
    if not g.group(2):
        st.caption(T["avertissement_simule"])                                 # sous chaque graphique de performance
st.markdown("\n".join(morceau).replace("$", "\\$"))                           # fin de la page
