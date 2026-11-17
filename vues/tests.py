"""Page « Backtesting » (20/10/2026, d'abord « Tests sur le passé ») : ce qu'aurait donné la note de 2010 à 2026 avec un portefeuille simulé,
résultats décevants compris. Graphiques et chiffres produits par la recherche (`Recherche_score/35_preuves_site.py`,
chiffres exacts dans `preuves_site/chiffres.json`), copiés dans images/tests/ ; aucune formule modifiée.

Le texte est dans traductions/tests_fr.md et traductions/tests_en.md. Une ligne {{graphique:NOM}} y place l'image
images/tests/NOM_fr.png (ou _en), suivie de l'avertissement obligatoire sur les performances simulées ;
{{graphique:NOM:sans_avertissement}} place l'image seule (graphique qui ne montre pas une performance).
"""
import base64           # transforme une image en texte pour l'insérer dans la page
import html             # protège les guillemets du texte alternatif
import re               # repérage des lignes {{graphique:...}}

import streamlit as st  # interface web

from vues.commun import SITE, textes

T = textes()                                                                  # textes de la langue choisie
L = st.session_state.get("langue", "fr")                                      # « fr » ou « en »
@st.cache_data(show_spinner=False)
def image_html(nom, langue, alt):
    """Balise <img> d'un graphique avec son texte alternatif (S-A02, WCAG 1.1.1) : st.image ne permet pas d'en écrire."""
    octets = (SITE / "images" / "tests" / f"{nom}_{langue}.png").read_bytes()    # contenu du fichier image
    donnees = base64.b64encode(octets).decode("ascii")                         # image convertie en texte
    alt = html.escape(alt, quote=True)                                        # les guillemets ne cassent pas la balise
    return (f'<img src="data:image/png;base64,{donnees}" alt="{alt}" '
            f'style="width:100%;max-width:900px;height:auto">')               # même taille maximale qu'avant (900 px)


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
    st.html(image_html(g.group(1), L, T["alt_" + g.group(1)]))                  # graphique avec texte alternatif
    if not g.group(2):
        st.caption(T["avertissement_simule"])                                 # sous chaque graphique de performance
st.markdown("\n".join(morceau).replace("$", "\\$"))                           # fin de la page
