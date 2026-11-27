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
    """Feuille de style ajoutée à chaque page : filets au-dessus des sections, menu numéroté 01 à 04 (à la place des
    émojis), bandeau du titre et bande défilante. Aucune ombre, aucun angle arrondi."""
    st.html(f"""<style>
    h1, h2, h3 {{ line-height: 1.05; letter-spacing: 0; }}
    [data-testid="stMainBlockContainer"] {{ padding-top: 4.5rem; }}         /* moins de vide en haut, mais sous
                                                                              l'en-tête de Streamlit (60 px) */
    [data-testid="stMainBlockContainer"] h3 {{ border-top: 1px solid {FILET}; padding-top: .8rem; margin-top: 1.8rem; }}
    [data-testid="stSidebarNavItems"] {{ counter-reset: rubrique; }}
    [data-testid="stSidebarNavLink"]::before {{ counter-increment: rubrique; content: counter(rubrique, decimal-leading-zero);
        font-family: 'Doto', monospace; font-weight: 900; color: {JAUNE}; margin-right: .7rem; }}
    .st-key-bouton_questions button {{ background: transparent; border: 0; padding: 0 8px; min-height: 32px; }}
    .st-key-bouton_questions button > div {{ justify-content: flex-start; }}  /* « Questions ? » aligné comme les
                                                                              entrées du menu */
    .st-key-bouton_questions button p {{ font-size: 14px; color: {TEXTE}; }}
    .st-key-bouton_questions button p::before {{ content: "?"; display: inline-block; width: 40px;
        font-family: 'Doto', monospace; font-weight: 900; font-size: 16px; color: {JAUNE}; }}   /* « ? » à points
                                                                              à la place du numéro */
    .st-key-bouton_questions button:hover {{ background: {SURFACE}; }}
    [data-testid="stDialog"] [data-testid="stTextInput"] {{ margin: 0; }}       /* fenêtre « Questions ? » : champ
                                                                              e-mail discret, pas le gros cadre */
    [data-testid="stDialog"] [data-testid="stTextInputRootElement"] {{ border: 1px solid {FILET} !important; }}
    [data-testid="stDialog"] [data-testid="stTextInput"] input {{ font-size: .9rem; padding: .4rem .6rem; }}
    [data-testid="stDialog"] [data-testid="stTextInput"] label p {{ font-size: .875rem; font-weight: 400;
        color: {TEXTE}; }}                                                    /* de la barre de recherche */
    [data-testid="stDialog"] [data-testid="InputInstructions"] {{ display: none; }}   /* pas d'indication en
                                                                              anglais (« Press Ctrl+Enter... ») */
    [data-testid="stSidebarNavItems"] li:nth-child(-n+2) [data-testid="stSidebarNavLink"] p {{ color: {JAUNE};
        font-weight: 700; }}                                                  /* Recherche et Classement, les deux
                                                                              pages principales, toujours en jaune
                                                                              et gras [M] 27/11/2026 */
    [data-testid="stSidebarNavItems"] li:nth-child(n+3) [data-testid="stSidebarNavLink"] p {{ opacity: .75; }}
                                                                              /* les autres, plus discrètes */
    [data-testid="stSidebarNavLink"][aria-current="page"] {{ background: {JAUNE}; }}   /* page ouverte : bloc
                                                                              jaune plein, comme le « B » du titre,
                                                                              pour ne pas la confondre avec les deux
                                                                              pages en jaune [M] 27/11/2026 */
    [data-testid="stSidebarNavLink"][aria-current="page"]:hover {{ background: {JAUNE}; }}   /* reste jaune au survol */
    [data-testid="stSidebarNavItems"] li [data-testid="stSidebarNavLink"][aria-current="page"] p {{ color: {FOND};
        font-weight: 700; opacity: 1; }}                                      /* texte sombre sur le jaune (règle
                                                                              plus précise que celles du dessus) */
    [data-testid="stSidebarNavLink"][aria-current="page"]::before {{ color: {FOND}; }}   /* numéro sombre aussi */
    hr {{ border-color: {FILET} !important; opacity: 1; }}
    [data-testid="stHeaderActionElements"] {{ display: none; }}               /* pas de petit lien après les titres */
    [data-testid="stSidebarLogo"] {{ height: 7.5rem !important; width: auto;
        max-width: 100%; }}                                         /* logo de Mathys bien visible */
    [data-testid="stSidebarHeader"] {{ height: auto; min-height: 9rem; padding-top: .9rem; position: relative;
        align-items: flex-start; }}                                 /* place pour le logo, rien de coupé */
    [data-testid="stSidebarHeader"] > :first-child {{ flex: 1; display: flex; justify-content: center; }}   /* logo seul
                                                                              (accueil) ou dans son lien (autres pages) */
    [data-testid="stSidebarCollapseButton"] {{ position: absolute; top: .6rem; right: .4rem; }}   /* logo centré
                                                                              sur la largeur du menu */
    [data-testid="stHeaderLogo"] {{ height: 2.9rem !important; width: auto; }}   /* menu replié : tient dans l'en-tête */
    .ba-presentation {{ min-height: 7.2rem; padding-top: .55rem; box-sizing: border-box; display: flex;
                        align-items: center; }}                          /* texte au milieu, entre la
                                                                              barre et l'avertissement */
    .ba-presentation p {{ font-size: 1.2rem; line-height: 1.55; margin: 0; }}   /* plus gros que le reste */
    [data-testid="stTextInput"] label p {{ font-size: 1.05rem; font-weight: 600; color: {JAUNE}; }}
    [data-testid="stTextInput"] {{ margin: 1.6rem 0 1.4rem; }}                /* recherche isolée : de l'air autour */
    [data-testid="stTextInputRootElement"] {{ border: 3px solid {JAUNE} !important; height: auto !important; }}
    [data-testid="stTextInput"] input {{ font-size: 1.1rem; padding: .5rem .8rem; }}   /* taille moyenne, bord épais */
    @media (max-width: 640px) {{ [data-testid="stTextInput"] input {{ font-size: .95rem; padding: .45rem .6rem; }} }}
    @media (max-width: 480px) {{                                              /* téléphone : tableaux resserrés pour */
        [data-testid="stMarkdownContainer"] table th, [data-testid="stMarkdownContainer"] table td {{
            font-size: .85rem; padding: .4rem .45rem; }}                      /* tenir sans défiler de côté (pages) */
        [data-testid="stTableStyledTable"] th, [data-testid="stTableStyledTable"] td {{
            font-size: .75rem; padding: .3rem .22rem; }} }}                   /* et sur la fiche */
    .ba-bandeau {{ display: block; padding: .22em .3em .18em; border: 1px solid {FILET}; margin: 0;
                   font-family: 'Doto', monospace; font-weight: 700; line-height: 1.05;
                   font-size: clamp(2rem, 5.6vw, 6rem); }}
    .ba-b {{ display: inline-block; padding: 0 .08em; margin-right: .06em; }}
    .ba-bande {{ overflow: hidden; white-space: nowrap; background: {SURFACE}; color: {JAUNE}; border: 1px solid {FILET};
                 border-top: 0; font-family: 'Doto', monospace; font-weight: 800; font-size: 1.15rem;
                 padding: .45rem 0; text-transform: uppercase; margin-bottom: .6rem; }}
    .ba-bande span {{ display: inline-block; padding-left: .8rem; animation: ba-defile 45s linear infinite; }}
    .ba-prix {{ position: relative; margin: .4rem 0 1rem; padding-top: 2.3rem; }}   /* barre du prix comparé au
                                                                              secteur : chère à gauche, bon marché à droite */
    .ba-prix-valeur {{ position: absolute; top: 0; line-height: 1.2; transform: translateX(-50%); font-family: 'Doto', monospace;
                       font-weight: 800; font-size: 1.05rem; color: {TEXTE}; white-space: nowrap; }}
    .ba-prix-barre {{ position: relative; height: 18px; border: 1px solid {FILET}; }}
    .ba-prix-seuil {{ position: absolute; top: 0; bottom: 0; width: 2px; margin-left: -1px; background: {FOND};
                      opacity: .55; }}                                        /* seuils +25 % et -20 % */
    .ba-prix-curseur {{ position: absolute; top: -7px; bottom: -7px; width: 6px; margin-left: -3px; background: {TEXTE};
                        box-shadow: 0 0 0 2px {FOND}; }}                      /* la société */
    .ba-prix-zones {{ display: flex; margin-top: .45rem; font-size: .8rem; color: {TEXTE}; }}
    .ba-prix-zones span {{ text-align: center; opacity: .7; }}
    .ba-prix-zones .ba-prix-actif {{ opacity: 1; font-weight: 700; }}       /* zone où se trouve la société */
    .ba-prix-seuils {{ position: relative; height: 1.1rem; font-size: .75rem; opacity: .75; }}
    .ba-prix.ba-barre-simple {{ padding-top: .7rem; }}                       /* barre sans chiffre (risque) */
    .ba-prix-avertissement {{ border: 1px solid {FILET}; border-left: 3px solid {JAUNE}; padding: .5rem .8rem;
                              margin: .2rem 0 .6rem; font-size: .9rem; }}       /* estimation : valeur peu fiable */
    .ba-prix-seuils span {{ position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; }}
    .st-key-fiche_titre h2 img {{ float: right; height: 1.15em; width: auto; max-width: 4em; object-fit: contain;
        margin: 0 0 .2em .6em; }}                                             /* fiche : nom à gauche, logo jaune (ou
                                                                              initiales) à droite [M] 20/11/2026 */
    .st-key-fiche_sous_titre img {{ height: .95em; width: auto; vertical-align: -0.12em; margin-right: .3em;
        outline: 1px solid {FILET}; }}                                        /* drapeau du pays, filet autour (le
                                                                              blanc du drapeau reste visible) */
    [data-testid="stMarkdownContainer"] p.ba-composante {{ margin: 0; font-size: 1.6rem; font-weight: 900;
        font-family: 'Doto', monospace; line-height: 1.2; overflow-wrap: normal; word-break: normal; }}
                                                                          /* police à points des titres [M] 20/11 ;
                                                                              26 px : « grand texte » WCAG, contraste 3 ;
                                                                              jamais coupé au milieu d'un mot */
    .ba-composante-ligne {{ display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap;
        gap: .2rem 1rem; }}                                                   /* nom à gauche, note à droite [M] 20/11 */
    [data-testid="stMarkdownContainer"] p.ba-composante-note {{ margin: 0; font-family: 'Doto', monospace;
        font-weight: 900; font-size: 1.9rem; line-height: 1.1; white-space: nowrap; }}   /* note en gros, 30 px */
    .ba-sur {{ font-size: 1rem; color: {TEXTE}; }}                            /* « / 100 » plus petit */
    .ba-composante-barre {{ height: 8px; background: {SURFACE}; margin: .4rem 0 .5rem; }}
    .ba-composante-barre > div {{ height: 100%; }}                            /* barre dans la couleur de la note */
    .st-key-courbe_menu [data-testid="stExpander"] details {{ border: 2px solid {JAUNE} !important;
        background: {SURFACE}; }}                                             /* menu « Courbe du cours » : cadre jaune,
                                                                              différent de « Détail des calculs » */
    .st-key-courbe_menu [data-testid="stExpander"] summary p {{ font-family: 'Doto', monospace; font-weight: 900;
        font-size: 1.15rem; color: {JAUNE}; text-transform: uppercase; }}
    .st-key-courbe_menu [data-testid="stExpander"] summary p::before {{ content: ""; display: inline-block;
        width: 1.2em; height: 1.2em; margin-right: .45em; vertical-align: -.22em; background: {JAUNE};
        -webkit-mask: url({ICONE_COURBE}) center / contain no-repeat;
        mask: url({ICONE_COURBE}) center / contain no-repeat; }}               /* icône de cours, en jaune */
    .st-key-courbe_menu [data-testid="stElementToolbar"] {{ display: none; }}   /* pas de boutons tableau,
                                                                              téléchargement... sur la courbe */
    .ba-courbe-tete {{ display: flex; align-items: baseline; flex-wrap: wrap; gap: .2rem 1rem; }}
    .ba-courbe-prix {{ font-family: 'Doto', monospace; font-weight: 900; font-size: 2rem; color: {CREME_TITRES}; }}
    .ba-courbe-var {{ font-weight: 700; font-size: 1.05rem; }}               /* +128 % en vert, −30 % en rouge */
    .ba-courbe-periode {{ font-weight: 400; color: {TEXTE}; }}
    .ba-lecteur-ecran {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0);
        white-space: nowrap; margin: -1px; }}                                 /* lu par les lecteurs d'écran, invisible */
    @media (max-width: 380px) {{ [data-testid="stMarkdownContainer"] p.ba-composante,
        .ba-num {{ font-size: 1.35rem !important; }} }}                       /* petit téléphone : tient sur une ligne */
    .ba-num {{ font-family: 'Doto', monospace; font-weight: 900; font-size: 1.6rem; color: {CREME_TITRES};
               margin-right: .7rem; }}                                   /* « 1) » crème, police des titres [M] 20/11 */
    [data-testid="stMainBlockContainer"] h1, [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3 {{ color: {CREME_TITRES}; }}     /* titres crème beige [M] 20/11/2026 */
    .st-key-pied_avertissement {{ border: 1px solid {CREME_TITRES} !important; padding: 1rem 1.2rem !important;
        margin-top: 2rem; text-align: center; }}                              /* avertissement centré dans un cadre
                                                                              crème [M] 20/11/2026 */
    .st-key-pied_avertissement [data-testid="stCaptionContainer"],
    .st-key-pied_avertissement p {{ margin: 0 !important; padding: 0; text-align: center; }}   /* centré, aucune
                                                                              marge en trop en bas */
    @keyframes ba-defile {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}
    @media (prefers-reduced-motion: reduce) {{ .ba-bande span {{ animation: none; }} }}
    </style>""")


def bandeau_titre(T):
    """Titre de la page d'accueil : « B » d'une couleur, « ourse à lunettes » de l'autre (B_EN_JAUNE), puis une bande
    défilante avec les noms des quatre composantes, comme un bandeau de cours de bourse. Textes du site seulement."""
    fond, b_fond, b_lettre, reste = ((JAUNE, FOND, JAUNE, FOND) if B_EN_JAUNE else (FOND, JAUNE, FOND, JAUNE))
    titre = T["titre"]                                                        # « Bourse à lunettes »
    mots = " · ".join(T[k] for k in ("rentabilite", "croissance", "bilan", "dynamique"))
    st.html(f'<h1 class="ba-bandeau" style="background:{fond}">'
            f'<span class="ba-b" style="background:{b_fond};color:{b_lettre}">{titre[0]}</span>'
            f'<span style="color:{CREME_LOGO}">{titre[1:5]}</span>'           # « ours » en crème : le jeu de mots
            f'<span style="color:{reste}">{titre[5:]}</span></h1>'
            f'<div class="ba-bande" aria-hidden="true"><span>{(mots + " · ") * 8}</span></div>')   # 2 moitiés égales :
                                                                              # le défilement boucle sans saut


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
