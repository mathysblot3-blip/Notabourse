"""Éléments communs aux pages du site : langue, textes, formats des nombres, pied de page."""
import base64              # icône glissée dans le style (adresse « data: »)
import json                # lecture des fichiers de textes
from pathlib import Path   # chemins de fichiers

import streamlit as st    # interface web

from notabourse.formats import date, dollars, nombre, pct   # noqa: F401  (formats des nombres, repris par les pages)
from notabourse.messages import EMAIL_MAX, LONGUEUR_MAX, MESSAGES_PAR_VISITE, TYPES, envoyer_message, verifier

SITE = Path(__file__).resolve().parents[1]                                    # dossier site
URL_ISSUES = "https://github.com/mathysblot3-blip/notabourse/issues"         # dépôt public du site [M] 19/10/2026

# Couleurs du site « Bourse à lunettes » [M] 20/10/2026 : noir et jaune. Version sombre, demandée par Mathys le
# 20/10/2026 (le papier crème était trop clair) : fond charbon chaud, texte crème, jaune moutarde moins vif.
FOND = "#15140f"                                                              # charbon chaud : fond des pages
SURFACE = "#211f18"                                                           # un cran plus clair : champs, jauge
FILET = "#4d4838"                                                             # filets de 1 pixel
TEXTE = "#ebe4cf"                                                             # crème : texte courant
JAUNE = "#D8AE48"                                                             # jaune moutarde de la marque
CREME_LOGO = "#FFF9DB"                                                        # crème du museau de l'ours du logo
                                                                              # (teinte dominante mesurée sur logo.png)
CREME_TITRES = "#F3E5C1"                                                      # même crème, un peu plus beige : titres,
                                                                              # numéros, cadre (le crème du logo
                                                                              # paraissait trop blanc) [M] 20/11/2026
# Petite icône de cours (ligne qui monte, avec une flèche) devant « Courbe du cours » [M] 20/11/2026. Dessin SVG maison
# utilisé comme pochoir (« mask ») : il prend la couleur jaune du titre. Décorative : rien n'est lu par les lecteurs
# d'écran. (L'icône intégrée de Streamlit, essayée avant, ne s'affichait pas.)
ICONE_COURBE = ("data:image/svg+xml;base64," + base64.b64encode(
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2.8" '
    b'stroke-linecap="round" stroke-linejoin="round"><polyline points="2.5 18 9 11.5 13 15.5 21 7.5"/>'
    b'<polyline points="14.5 7.5 21 7.5 21 14"/></svg>').decode("ascii"))
B_EN_JAUNE = False   # titre : False = « B » sombre dans un carré jaune, puis « ourse à lunettes » en jaune, sur le fond
                     # sombre (calme, 8,8 pour 1) ; True = l'inverse, sur un bandeau jaune (plus de jaune à l'écran)

LOGOS = [SITE / "images" / "logo.png", SITE / "images" / "logo_provisoire.png"]   # logo définitif, sinon provisoire
ICONE = SITE / "images" / "icone.png"                                         # « B » à points, pour l'onglet


def logo():
    """Chemin du logo (le définitif de Mathys s'il existe, sinon le provisoire), ou None : le logo provisoire n'est
    jamais publié (licence inconnue, voir .gitignore), donc le site en ligne s'en passe."""
    return next((str(p) for p in LOGOS if p.exists()), None)


def style():
    """Feuille de style ajoutée à chaque page : filets au-dessus des sections, menu numéroté (à la place des émojis),
    bandeau du titre et bande des quatre mots. Aucune ombre, aucun angle arrondi.

    Retouche « unslop » [P] 27/11/2026 (maquette) :
      - espacements sur une grille de 4 px (8, 12, 16, 24, 32, 48 ; 72 et 120 pour les hauteurs fixes) ;
      - 6 tailles de texte seulement [M] : 12, 14, 16, 20, 32 et 64 px ;
      - Inter en 400 et 600, la police à points (Doto) pour les titres et les chiffres clés seulement ;
      - un seul style de cadre (filet gris de 1 px) ; le jaune reste au titre, à la page ouverte, à la recherche, à la
        note et à la courbe ;
      - rien ne bouge en boucle."""
    st.html(f"""<style>
    h1, h2, h3 {{ line-height: 1.05; letter-spacing: 0; }}
    b, strong {{ font-weight: 600; }}                                         /* Inter : 400 et 600 seulement */
    [data-testid="stMainBlockContainer"] {{ padding-top: 4.5rem; }}          /* 72 px, sous l'en-tête de Streamlit (60 px) */
    [data-testid="stMainBlockContainer"] h3 {{ border-top: 1px solid {FILET}; padding-top: 12px; margin-top: 32px; }}
    /* Téléphone : titres plus petits, mais toujours dans les 6 tailles */
    @media (max-width: 640px) {{
        [data-testid="stMainBlockContainer"] h1 {{ font-size: 32px; }}
        [data-testid="stMainBlockContainer"] h2,
        [data-testid="stMainBlockContainer"] h3 {{ font-size: 20px; }} }}
    /* Paragraphes : environ 75 caractères par ligne au plus (38 em), les tableaux gardent toute la largeur */
    [data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] > p,
    [data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] > ul,
    [data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] > ol,
    [data-testid="stMainBlockContainer"] [data-testid="stCaptionContainer"] > p {{ max-width: 38em; }}

    /* --- Menu de gauche --- */
    [data-testid="stSidebarNavItems"] {{ counter-reset: rubrique; }}
    [data-testid="stSidebarNavLink"]::before {{ counter-increment: rubrique; content: counter(rubrique, decimal-leading-zero);
        font-family: 'Doto', monospace; font-weight: 900; color: {TEXTE}; opacity: .75; margin-right: 12px; }}
    [data-testid="stSidebarNavItems"] li:nth-child(-n+2) [data-testid="stSidebarNavLink"]::before {{ color: {JAUNE};
        opacity: 1; }}                                                        /* numéro de la couleur de son nom */
    [data-testid="stSidebarNavItems"] li:nth-child(-n+2) [data-testid="stSidebarNavLink"] p {{ color: {JAUNE};
        font-weight: 600; }}                                                  /* Recherche et Classement, les deux
                                                                              pages principales, toujours en jaune
                                                                              et gras [M] 27/11/2026 */
    [data-testid="stSidebarNavItems"] li:nth-child(n+3) [data-testid="stSidebarNavLink"] p {{ opacity: .75; }}
                                                                              /* les autres, plus discrètes */
    [data-testid="stSidebarNavLink"][aria-current="page"] {{ background: {JAUNE}; }}   /* page ouverte : bloc
                                                                              jaune plein [M] 27/11/2026 */
    [data-testid="stSidebarNavLink"][aria-current="page"]:hover {{ background: {JAUNE}; }}   /* reste jaune au survol */
    [data-testid="stSidebarNavItems"] li [data-testid="stSidebarNavLink"][aria-current="page"] p {{ color: {FOND};
        font-weight: 600; opacity: 1; }}                                      /* texte sombre sur le jaune */
    [data-testid="stSidebarNavItems"] li [data-testid="stSidebarNavLink"][aria-current="page"]::before {{
        color: {FOND}; opacity: 1; }}                                         /* numéro sombre aussi */
    .st-key-bouton_questions button {{ background: transparent; border: 0; padding: 0 8px; min-height: 32px; }}
    .st-key-bouton_questions button > div {{ justify-content: flex-start; }}  /* « Questions ? » aligné comme les
                                                                              entrées du menu */
    .st-key-bouton_questions button p {{ font-size: 14px; color: {TEXTE}; }}
    .st-key-bouton_questions button p::before {{ content: "?"; display: inline-block; width: 40px;
        font-family: 'Doto', monospace; font-weight: 900; font-size: 14px; color: {TEXTE}; opacity: .75; }}
                                                                              /* « ? » à la place du numéro */
    .st-key-bouton_questions button:hover {{ background: {SURFACE}; }}
    [data-testid="stSidebarLogo"] {{ height: 120px !important; width: auto; max-width: 100%; }}   /* logo bien visible */
    [data-testid="stSidebarHeader"] {{ height: auto; min-height: 144px; padding-top: 16px; position: relative;
        align-items: flex-start; }}                                 /* place pour le logo, rien de coupé */
    [data-testid="stSidebarHeader"] > :first-child {{ flex: 1; display: flex; justify-content: center; }}   /* logo seul
                                                                              (accueil) ou dans son lien (autres pages) */
    [data-testid="stSidebarCollapseButton"] {{ position: absolute; top: 8px; right: 8px; }}   /* logo centré
                                                                              sur la largeur du menu */
    [data-testid="stHeaderLogo"] {{ height: 48px !important; width: auto; }}   /* menu replié : tient dans l'en-tête */

    /* --- Fenêtre « Questions ? » --- */
    [data-testid="stDialog"] [data-testid="stTextInput"] {{ margin: 0; }}       /* champ e-mail discret, pas le gros
                                                                              cadre de la recherche */
    [data-testid="stDialog"] [data-testid="stTextInputRootElement"] {{ border: 1px solid {FILET} !important; }}
    [data-testid="stDialog"] [data-testid="stTextInput"] input {{ font-size: 14px; padding: 8px 12px; }}
    [data-testid="stDialog"] [data-testid="stTextInput"] label p {{ font-size: 14px; font-weight: 400;
        color: {TEXTE}; }}
    [data-testid="stDialog"] [data-testid="InputInstructions"] {{ display: none; }}   /* pas d'indication en
                                                                              anglais (« Press Ctrl+Enter... ») */
    hr {{ border-color: {FILET} !important; opacity: 1; }}
    [data-testid="stHeaderActionElements"] {{ display: none; }}               /* pas de petit lien après les titres */

    /* --- Menus dépliants : une ligne sous un filet, plus une pile de cadres [P] 27/11/2026 --- */
    [data-testid="stExpander"] details {{ border: 0 !important; border-top: 1px solid {FILET} !important;
        background: transparent; }}
    [data-testid="stExpander"] summary {{ padding: 12px 0; }}
    [data-testid="stExpanderDetails"] {{ padding: 0 0 16px; }}

    /* --- Accueil : titre, bande des quatre mots, présentation, recherche --- */
    .ba-bandeau {{ display: block; padding: 12px 16px; border: 1px solid {FILET}; margin: 0;
                   font-family: 'Doto', monospace; font-weight: 700; line-height: 1.05; font-size: 64px; }}
    .ba-b {{ display: inline-block; padding: 0 .08em; margin-right: .06em; }}   /* « B » dans son carré */
    .ba-bande {{ overflow: hidden; white-space: nowrap; background: {SURFACE}; color: {JAUNE}; border: 1px solid {FILET};
                 border-top: 0; font-family: 'Doto', monospace; font-weight: 800; font-size: 20px; line-height: 1.2;
                 padding: 8px 16px; margin-bottom: 8px; }}                    /* immobile, en casse normale [P] */
    /* Écran plus étroit : le titre tient sur une ligne, la bande passe à la ligne au lieu d'être coupée */
    @media (max-width: 1200px) {{ .ba-bandeau {{ font-size: 32px; padding: 8px 12px; }}
        .ba-bande {{ font-size: 16px; white-space: normal; }} }}
    body:has(.st-key-fiche_titre) .ba-bandeau {{ font-size: 20px; padding: 8px 12px; }}   /* fiche : titre réduit à
                                                                              une ligne, la société remonte [P] */
    body:has(.st-key-fiche_titre) .ba-bande {{ display: none; }}
    .ba-presentation {{ min-height: 112px; padding-top: 8px; box-sizing: border-box; display: flex;
                        align-items: center; }}                          /* texte au milieu, entre la
                                                                              barre et l'avertissement */
    .ba-presentation p {{ font-size: 20px; line-height: 1.5; margin: 0; max-width: 38em; }}
    .ba-presentation p + p {{ margin-top: 1.5em; }}                         /* une ligne vide (30 px) avant la
                                                                              dernière phrase [M] 27/11/2026 */
    [data-testid="stTextInput"] label p {{ font-size: 16px; font-weight: 600; color: {JAUNE}; }}
    [data-testid="stTextInput"] {{ margin: 24px 0; }}                         /* recherche isolée : de l'air autour */
    [data-testid="stTextInputRootElement"] {{ border: 3px solid {JAUNE} !important; height: auto !important; }}
    [data-testid="stTextInput"] input {{ font-size: 20px; padding: 8px 12px; }}   /* bord épais [M] */
    @media (max-width: 640px) {{ [data-testid="stTextInput"] input {{ font-size: 16px; padding: 8px; }} }}
    @media (max-width: 480px) {{                                              /* téléphone : tableaux resserrés pour */
        [data-testid="stMarkdownContainer"] table th, [data-testid="stMarkdownContainer"] table td {{
            font-size: 14px; padding: 8px; }}                                 /* tenir sans défiler de côté (pages) */
        [data-testid="stTableStyledTable"] th, [data-testid="stTableStyledTable"] td {{
            font-size: 12px; padding: 4px; }} }}                              /* et sur la fiche */

    /* --- Fiche : barres du risque et du prix --- */
    .ba-prix {{ position: relative; margin: 8px 0 16px; padding-top: 36px; }}   /* chère à gauche, bon marché à droite */
    .ba-prix-valeur {{ position: absolute; top: 0; line-height: 1.2; transform: translateX(-50%); font-family: 'Doto', monospace;
                       font-weight: 800; font-size: 20px; color: {TEXTE}; white-space: nowrap; }}
    .ba-prix-barre {{ position: relative; height: 16px; border: 1px solid {FILET}; }}
    .ba-prix-seuil {{ position: absolute; top: 0; bottom: 0; width: 2px; margin-left: -1px; background: {FOND};
                      opacity: .55; }}                                        /* seuils +25 % et -20 % */
    .ba-prix-curseur {{ position: absolute; top: -8px; bottom: -8px; width: 6px; margin-left: -3px; background: {TEXTE};
                        outline: 2px solid {FOND}; }}                         /* la société (liseré, pas une ombre) */
    .ba-prix-zones {{ display: flex; margin-top: 8px; font-size: 14px; color: {TEXTE}; }}
    .ba-prix-zones span {{ text-align: center; opacity: .7; }}
    .ba-prix-zones .ba-prix-actif {{ opacity: 1; font-weight: 600; }}       /* zone où se trouve la société */
    .ba-prix-seuils {{ position: relative; height: 20px; font-size: 12px; opacity: .75; }}
    .ba-prix.ba-barre-simple {{ padding-top: 12px; }}                        /* barre sans chiffre (risque) */
    .ba-prix-avertissement {{ border: 1px solid {FILET}; padding: 8px 12px; margin: 8px 0 12px;
                              font-size: 14px; max-width: 38em; }}            /* estimation : valeur peu fiable */
    .ba-prix-seuils span {{ position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; }}

    /* --- Fiche : en-tête, note, composantes --- */
    .st-key-fiche_titre h2 img {{ float: right; height: 1.15em; width: auto; max-width: 4em; object-fit: contain;
        margin: 0 0 4px 12px; }}                                              /* nom à gauche, logo jaune (ou
                                                                              initiales) à droite [M] 20/11/2026 */
    .st-key-fiche_sous_titre img {{ height: .95em; width: auto; vertical-align: -0.12em; margin-right: 4px;
        outline: 1px solid {FILET}; }}                                        /* drapeau du pays, filet autour (le
                                                                              blanc du drapeau reste visible) */
    @media (max-width: 640px) {{ [data-testid="stPlotlyChart"] .number {{ font-size: 32px !important; }} }}
                                                                              /* téléphone : « 96 » en 32 px, sinon il
                                                                              déborde sur l'arc de la jauge, plus petite */
    .st-key-composantes {{ gap: 48px; }}                                      /* entre deux composantes : 48 px */
    [class*="st-key-composante_"] {{ gap: 12px; }}                           /* dans une composante : 12 px */
    [data-testid="stMarkdownContainer"] p.ba-composante {{ margin: 0; font-size: 20px; font-weight: 900;
        font-family: 'Doto', monospace; line-height: 1.2; overflow-wrap: normal; word-break: normal; }}
                                                                          /* 20 px en police à points (900) : « grand
                                                                              texte » WCAG (gras dès 18,7 px), contraste 3 ;
                                                                              jamais coupé au milieu d'un mot */
    .ba-composante-ligne {{ display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap;
        gap: 4px 16px; }}                                                     /* nom à gauche, note à droite [M] 20/11 */
    [data-testid="stMarkdownContainer"] p.ba-composante-note {{ margin: 0; font-family: 'Doto', monospace;
        font-weight: 900; font-size: 32px; line-height: 1.1; white-space: nowrap; }}   /* note de la composante */
    .ba-sur {{ font-size: 14px; color: {TEXTE}; }}                            /* « / 100 » plus petit */
    .ba-composante-barre {{ height: 8px; background: {SURFACE}; margin: 8px 0 16px; }}   /* 16 px en bas : compense
                                                                              la marge de -16 px que Streamlit met sous
                                                                              chaque texte ; il reste les 12 px du bloc */
    .ba-composante-ligne:last-child {{ margin-bottom: 16px; }}               /* idem sans note (pas de barre) */
    .ba-composante-barre > div {{ height: 100%; }}                            /* barre dans la couleur de la note */
    .ba-num {{ font-family: 'Doto', monospace; font-weight: 900; font-size: 20px; color: {CREME_TITRES};
               margin-right: 12px; }}                                     /* « 1) » crème, police des titres [M] 20/11 */

    /* --- Fiche : les quatre composantes en bref, à gauche de la jauge [M] 27/11/2026 --- */
    .ba-mini {{ display: grid; grid-template-columns: 1fr auto; align-items: baseline; gap: 4px 12px;
        margin-bottom: 12px; }}                                               /* une composante par ligne */
    .ba-mini-nom {{ font-size: 16px; }}
    .ba-mini-note {{ font-family: 'Doto', monospace; font-weight: 900; font-size: 20px; }}
    .ba-mini-barre {{ grid-column: 1 / -1; height: 4px; background: {SURFACE}; }}
    .ba-mini-barre > div {{ height: 100%; }}

    /* --- Fiche : courbe du cours (cadre jaune [M]) --- */
    .st-key-courbe_menu [data-testid="stExpander"] details {{ border: 2px solid {JAUNE} !important;
        background: {SURFACE}; }}                                             /* menu « Courbe du cours » : cadre jaune,
                                                                              différent de « Détail des calculs » */
    .st-key-courbe_menu [data-testid="stExpander"] summary {{ padding: 12px 16px; }}
    .st-key-courbe_menu [data-testid="stExpanderDetails"] {{ padding: 0 16px 16px; }}
    .st-key-courbe_menu [data-testid="stExpander"] summary p {{ font-family: 'Doto', monospace; font-weight: 900;
        font-size: 20px; color: {JAUNE}; text-transform: uppercase; }}       /* en majuscules [M] */
    .st-key-courbe_menu [data-testid="stExpander"] summary p::before {{ content: ""; display: inline-block;
        width: 1.2em; height: 1.2em; margin-right: 8px; vertical-align: -.22em; background: {JAUNE};
        -webkit-mask: url({ICONE_COURBE}) center / contain no-repeat;
        mask: url({ICONE_COURBE}) center / contain no-repeat; }}               /* icône de cours, en jaune */
    .st-key-courbe_menu [data-testid="stElementToolbar"] {{ display: none; }}   /* pas de boutons tableau,
                                                                              téléchargement... sur la courbe */
    .ba-courbe-tete {{ display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 16px; }}
    .ba-courbe-prix {{ font-family: 'Doto', monospace; font-weight: 900; font-size: 32px; color: {CREME_TITRES}; }}
    .ba-courbe-var {{ font-weight: 600; font-size: 16px; }}                  /* +128 % en vert, −30 % en rouge */
    .ba-courbe-periode {{ font-weight: 400; color: {TEXTE}; }}
    .ba-lecteur-ecran {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0);
        white-space: nowrap; margin: -1px; }}                                 /* lu par les lecteurs d'écran, invisible */

    /* --- Titres et pied de page --- */
    [data-testid="stMainBlockContainer"] h1, [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3 {{ color: {CREME_TITRES}; }}     /* titres crème beige [M] 20/11/2026 */
    .st-key-pied_avertissement {{ border: 1px solid {CREME_TITRES} !important; padding: 16px 24px !important;
        margin-top: 48px; text-align: center; }}                              /* avertissement centré dans un cadre
                                                                              crème [M] 20/11/2026 */
    .st-key-pied_avertissement [data-testid="stCaptionContainer"],
    .st-key-pied_avertissement p {{ margin: 0 auto !important; padding: 0; text-align: center; }}   /* centré, aucune
                                                                              marge en trop en bas */
    .st-key-pied_avertissement [data-testid="stCaptionContainer"] > p {{ max-width: none; }}   /* une phrase par
                                                                              ligne, comme avant (pas de coupure) */
    </style>""")


def bandeau_titre(T):
    """Titre de la page d'accueil : « B » d'une couleur, « ourse à lunettes » de l'autre (B_EN_JAUNE), puis une bande
    avec les noms des quatre composantes, comme un panneau de cours de bourse. Immobile et en casse normale [P]
    27/11/2026 (elle défilait en boucle, en majuscules). Textes du site seulement."""
    fond, b_fond, b_lettre, reste = ((JAUNE, FOND, JAUNE, FOND) if B_EN_JAUNE else (FOND, JAUNE, FOND, JAUNE))
    titre = T["titre"]                                                        # « Bourse à lunettes »
    mots = " · ".join(T[k] for k in ("rentabilite", "croissance", "bilan", "dynamique"))
    st.html(f'<h1 class="ba-bandeau" style="background:{fond}">'
            f'<span class="ba-b" style="background:{b_fond};color:{b_lettre}">{titre[0]}</span>'
            f'<span style="color:{CREME_LOGO}">{titre[1:5]}</span>'           # « ours » en crème : le jeu de mots
            f'<span style="color:{reste}">{titre[5:]}</span></h1>'
            f'<div class="ba-bande" aria-hidden="true">{mots}</div>')         # les 4 mots, une seule fois


@st.cache_data
def _charger_textes(langue, signature):
    """Textes de l'interface dans une langue (traductions/fr.json ou en.json), gardés en mémoire ; `signature` (date de
    modification du fichier) force la relecture quand le fichier change."""
    return json.loads((SITE / "traductions" / f"{langue}.json").read_text(encoding="utf-8"))


def code_langue_page(lg):
    """Petit script qui écrit la langue (fr ou en) dans l'attribut lang de la page (S-A01, WCAG 3.1.1)."""
    lg = lg if lg in ("fr", "en") else "fr"                                   # seules valeurs permises
    # Le script s'exécute dans un cadre de même origine que la page : il peut modifier le <html> du parent.
    return f"<script>window.parent.document.documentElement.lang = '{lg}';</script>"


def appliquer_langue_page(lg):
    """Fait passer l'attribut lang de la page de « en » (valeur de Streamlit) à la langue choisie."""
    st.components.v1.html(code_langue_page(lg), height=0)                     # cadre invisible de hauteur nulle


def langue():
    """Langue choisie par le visiteur : français par défaut [M], bouton dans la barre latérale."""
    if "langue" not in st.session_state:
        st.session_state["langue"] = "fr"                                     # premier passage : français
    choix = st.sidebar.segmented_control("Langue / Language", ["FR", "EN"],
                                         default=st.session_state["langue"].upper(), key="choix_langue")
    if choix:                                                                 # un clic sur le bouton déjà choisi le vide
        st.session_state["langue"] = choix.lower()
    appliquer_langue_page(st.session_state["langue"])                         # S-A01 : lang="fr" ou lang="en"
    return st.session_state["langue"]


def textes():
    """Dictionnaire des textes de la langue choisie."""
    lg = st.session_state.get("langue", "fr")
    return _charger_textes(lg, (SITE / "traductions" / f"{lg}.json").stat().st_mtime)


def pied_de_page():
    """Mentions obligatoires (cahier des charges §6), en bas de chaque page."""
    T = textes()
    with st.container(border=True, key="pied_avertissement"):                # dans un cadre [M] 20/11/2026
        st.caption(f"{T['mention_conseil']}  \n{T['mention_recherche']}  \n{T['mention_donnees']}  \n"
                   f"{T['mention_auteur']} · {T['contact_pied']}")          # plus de lien GitHub [M] 25/10/2026


# --- Bouton « Questions ? » : questions, demandes et erreurs, sans passer par GitHub [M] 25/10/2026 ---------------
CLES_FORMULAIRE = ("msg_choix_type", "msg_choix_texte", "msg_choix_email")   # champs vidés pour un nouveau message


def _contenu_fenetre(T):
    """Contenu de la fenêtre : type, message, e-mail facultatif, envoi ; puis remerciement."""
    L = st.session_state.get("langue", "fr")
    envoyes = st.session_state.get("messages_envoyes", 0)                    # messages envoyés pendant cette visite
    if st.session_state.get("message_ok"):                                    # message tout juste envoyé
        st.success(T["msg_merci"])
        if envoyes < MESSAGES_PAR_VISITE and st.button(T["msg_autre"]):
            st.session_state["message_ok"] = False
            for cle in CLES_FORMULAIRE:                                       # formulaire vide pour le suivant
                st.session_state.pop(cle, None)
            st.rerun(scope="fragment")
        return
    if envoyes >= MESSAGES_PAR_VISITE:                                        # limite contre les envois en rafale
        st.info(T["msg_limite"])
        return
    st.markdown(T["msg_intro"])
    with st.form("formulaire_message", border=False):                        # rien n'est envoyé avant le bouton
        type_ = st.radio(T["msg_type"], TYPES, format_func=lambda x: T["msg_type_" + x], horizontal=True,
                         key="msg_choix_type")
        texte = st.text_area(T["msg_texte"], max_chars=LONGUEUR_MAX, height=150, key="msg_choix_texte",
                             placeholder=T["msg_texte_exemple"])
        email = st.text_input(T["msg_email"], max_chars=EMAIL_MAX, key="msg_choix_email",
                              placeholder=T["msg_email_exemple"])
        st.caption(T["msg_donnees"])
        envoi = st.form_submit_button(T["msg_envoyer"], type="primary")
    if envoi:
        ligne, erreur = verifier(type_, texte, email)                         # contrôles avant l'envoi
        if erreur:
            st.error(T[erreur])
        elif envoyer_message(ligne, L):                                       # enregistré chez Supabase
            st.session_state["messages_envoyes"] = envoyes + 1
            st.session_state["message_ok"] = True
            st.rerun(scope="fragment")                                        # affiche le remerciement
        else:
            st.error(T["msg_echec"])


def bouton_questions():
    """Bouton « Questions ? » sous le menu : ouvre une fenêtre par-dessus la page, qui reste en place derrière."""
    T = textes()

    @st.dialog(T["msg_titre"], width="medium")                               # titre dans la langue choisie
    def fenetre():
        _contenu_fenetre(T)

    if st.button(T["msg_bouton"], key="bouton_questions", width="stretch"):
        st.session_state["message_ok"] = False                                # chaque ouverture : formulaire
        fenetre()
