"""Page Classement (04/11/2026) : les grandes sociétés cotées du monde, classées par leur note.

Deux classements :
  1. les meilleures notes ;
  2. « Bien notées, moins chères que leur secteur » : notes de 50 ou plus et PER au moins 20 % sous celui du secteur,
     triées par la note (variante B de l'audit, choisie par Mathys le 17/11/2026 [M] ; remplace « note × facteur de
     prix » du 04/11/2026, dont 47 des 50 premières lignes étaient au plafond du facteur).
Des filtres communs aux deux : zone, pays (de A à Z), secteur, taille, puis dans « Plus d'options » : indice,
sociétés écartées, données complètes. Tri au choix, ou d'un clic sur le titre d'une colonne.
Données : reference/classement.parquet, construit chaque nuit par reference/construire_classement.py et rangé par le
robot dans la release « classement » du dépôt ; le site le télécharge de là (le fichier local sert aux essais).
"""
import io               # lire un fichier téléchargé sans l'écrire sur le disque
import logging          # erreurs notées dans le journal du serveur
import unicodedata      # lettres sans accent, pour trier les pays (Suède avant Suisse)

import pandas as pd     # tableaux de données
import requests         # téléchargement du classement
import streamlit as st  # interface web

from notabourse.constantes import PRIX_BON_MARCHE, PRIX_CHERE   # seuils du site
from notabourse.indices import INDICES, indices_de                # Nikkei 225, CAC 40...
from notabourse.pays import adresse_drapeau                       # petit drapeau servi par le site
from vues.commun import FILET, JAUNE, SITE, SURFACE, textes

# --- Textes du prototype (passeront dans traductions/fr.json et en.json une fois la page validée) -------------------
TXT = {
    "fr": {
        "titre": "Classement",
        "fictif": "**Prototype : toutes les valeurs de cette page sont fictives.** Elles servent seulement à tester "
                  "l'affichage et les filtres.",
        "intro": "Les sociétés notées par Bourse à lunettes, des États-Unis, d'Europe, d'Asie et d'ailleurs, "
                 "classées par leur note sur 100. La note se lit toujours avec sa fiche : cliquez sur une ligne.",
        "filtres": "Filtres et tri", "recherche": "Nom ou symbole", "zone": "Zone", "pays": "Pays",
        "secteur": "Secteur", "taille": "Taille", "prix": "Prix comparé au secteur", "indice": "Indice",
        "etoiles_min": "Étoiles au minimum", "ecartees": "Montrer les sociétés écartées de la sélection (risque de faillite ou fonds propres négatifs)",
        "completes": "Seulement les notes complètes (4 composantes sur 4)", "tri": "Trier par",
        "ordre": "Ordre", "decroissant": "Du plus haut au plus bas", "croissant": "Du plus bas au plus haut",
        "nombre": "Nombre de lignes", "tout": "Tous", "toutes": "Toutes",
        "taille_grande": "Grandes (plus de 10 Md$)", "taille_moyenne": "Moyennes (2 à 10 Md$)",
        "taille_petite": "Petites (moins de 2 Md$)",
        "indice_sp": "Membres du S&P 500", "indice_hors": "Hors S&P 500",
        "prix_bon_marche": "Bon marché", "prix_norme": "Dans la norme", "prix_chere": "Chère",
        "prix_pertes": "En perte (pas de PER)",
        "onglet_notes": "Meilleures notes", "onglet_prix": "Bien notées, moins chères que leur secteur",
        "explication_notes": "Classement par la note sur 100 (rang parmi les sociétés notées).",
        "explication_prix": "**Score prix compris = note × facteur de prix.** Facteur = PER du secteur ÷ PER de la "
                            "société, borné entre 0,5 et 2 : une société notée 80 et 25 % moins chère que son "
                            "secteur obtient 80 × 1,33 = 107 ; la même, 25 % plus chère, obtient 80 × 0,8 = 64. "
                            "Les sociétés en perte n'ont pas de PER : elles ne figurent pas dans ce classement.",
        "prudence_prix": "Le prix comparé au secteur décrit, il ne prédit pas : de 2010 à 2026, les actions bon "
                         "marché n'ont fait que 1,2 point par an de mieux que les chères, un écart non significatif.",
        "note_min": "Note sur 100 au minimum", "resultats": "{n} sociétés correspondent aux filtres.",
        "aucune": "Aucune société ne correspond à ces filtres.",
        "col_rang": "Rang", "col_societe": "Société", "col_symbole": "Symbole", "col_pays": "Pays",
        "col_secteur": "Secteur", "col_note": "Note sur 100", "col_etoiles": "Étoiles",
        "col_prix": "Prix / secteur", "col_facteur": "Facteur prix", "col_score": "Score prix compris",
        "col_capi": "Capi. (Md$)", "aide_prix": "PER de la société ÷ PER du secteur, moins 1 : "
                                                         "+25 % = 25 % plus chère que son secteur.",
        "ecartee": "écartée", "fiche": "Fiche de {nom}", "fiche_bientot": "Dans la vraie page, ce bouton ouvrira "
                                                                         "la fiche complète de la société.",
        "ouvrir": "Ouvrir la fiche", "detail": "Afficher les 4 composantes de la note",
    },
    "en": {
        "titre": "Ranking",
        "fictif": "**Prototype: every value on this page is made up.** It is only here to test the layout and "
                  "the filters.",
        "intro": "Companies scored by Bourse à lunettes, from the United States, Europe, Asia and elsewhere, ranked "
                 "by their score out of 100. Always read a score with its sheet: click a row.",
        "filtres": "Filters and sorting", "recherche": "Name or ticker", "zone": "Region", "pays": "Country",
        "secteur": "Sector", "taille": "Size", "prix": "Price compared with the sector", "indice": "Index",
        "etoiles_min": "Minimum stars", "ecartees": "Show companies left out of the selection (bankruptcy risk or negative equity)",
        "completes": "Complete scores only (4 components out of 4)", "tri": "Sort by",
        "ordre": "Order", "decroissant": "Highest first", "croissant": "Lowest first",
        "nombre": "Number of rows", "tout": "All", "toutes": "All",
        "taille_grande": "Large (over $10bn)", "taille_moyenne": "Mid ($2bn to $10bn)",
        "taille_petite": "Small (under $2bn)",
        "indice_sp": "S&P 500 members", "indice_hors": "Outside the S&P 500",
        "prix_bon_marche": "Cheap", "prix_norme": "In line", "prix_chere": "Expensive",
        "prix_pertes": "Loss-making (no P/E)",
        "onglet_notes": "Best scores", "onglet_prix": "Well rated, cheaper than their sector",
        "explication_notes": "Ranked by the score out of 100 (rank among scored companies).",
        "explication_prix": "**Price-adjusted score = score × price factor.** Factor = sector P/E ÷ company P/E, "
                            "capped between 0.5 and 2: a company scored 80 and 25% cheaper than its sector gets "
                            "80 × 1.33 = 107; the same company, 25% more expensive, gets 80 × 0.8 = 64. "
                            "Loss-making companies have no P/E: they are not in this ranking.",
        "prudence_prix": "Price compared with the sector describes, it does not predict: from 2010 to 2026, cheap stocks "
                         "beat expensive ones by only 1.2 points a year, a gap that is not significant.",
        "note_min": "Minimum score out of 100", "resultats": "{n} companies match the filters.",
        "aucune": "No company matches these filters.",
        "col_rang": "Rank", "col_societe": "Company", "col_symbole": "Ticker", "col_pays": "Country",
        "col_secteur": "Sector", "col_note": "Score out of 100", "col_etoiles": "Stars",
        "col_prix": "Price vs sector", "col_facteur": "Price factor", "col_score": "Price-adjusted score",
        "col_capi": "Mkt cap ($bn)", "aide_prix": "Company P/E ÷ sector P/E, minus 1: +25% = 25% more "
                                                     "expensive than its sector.",
        "ecartee": "excluded", "fiche": "Sheet of {nom}", "fiche_bientot": "On the real page, this button will open "
                                                                        "the company's full sheet.",
        "ouvrir": "Open the sheet", "detail": "Show the 4 components of the score",
    },
}
# Pays de l'univers (reference/construire_classement.py) : code -> (nom français, nom anglais, zone)
PAYS = {"us": ("États-Unis", "United States", "amn"), "ca": ("Canada", "Canada", "amn"),
        "br": ("Brésil", "Brazil", "aml"), "mx": ("Mexique", "Mexico", "aml"), "ar": ("Argentine", "Argentina", "aml"),
        "cl": ("Chili", "Chile", "aml"),
        "fr": ("France", "France", "eur"), "de": ("Allemagne", "Germany", "eur"),
        "gb": ("Royaume-Uni", "United Kingdom", "eur"), "ch": ("Suisse", "Switzerland", "eur"),
        "nl": ("Pays-Bas", "Netherlands", "eur"), "se": ("Suède", "Sweden", "eur"), "it": ("Italie", "Italy", "eur"),
        "es": ("Espagne", "Spain", "eur"), "dk": ("Danemark", "Denmark", "eur"), "no": ("Norvège", "Norway", "eur"),
        "fi": ("Finlande", "Finland", "eur"), "be": ("Belgique", "Belgium", "eur"), "at": ("Autriche", "Austria", "eur"),
        "pt": ("Portugal", "Portugal", "eur"), "ie": ("Irlande", "Ireland", "eur"), "pl": ("Pologne", "Poland", "eur"),
        "gr": ("Grèce", "Greece", "eur"), "tr": ("Turquie", "Turkey", "eur"),
        "jp": ("Japon", "Japan", "asi"), "kr": ("Corée du Sud", "South Korea", "asi"),
        "hk": ("Hong Kong", "Hong Kong", "asi"), "cn": ("Chine", "China", "asi"), "tw": ("Taïwan", "Taiwan", "asi"),
        "in": ("Inde", "India", "asi"), "au": ("Australie", "Australia", "asi"),
        "nz": ("Nouvelle-Zélande", "New Zealand", "asi"), "sg": ("Singapour", "Singapore", "asi"),
        "id": ("Indonésie", "Indonesia", "asi"), "th": ("Thaïlande", "Thailand", "asi"),
        "my": ("Malaisie", "Malaysia", "asi"),
        "za": ("Afrique du Sud", "South Africa", "moa"), "il": ("Israël", "Israel", "moa"),
        "sa": ("Arabie saoudite", "Saudi Arabia", "moa"), "qa": ("Qatar", "Qatar", "moa")}
ZONES = {"amn": ("Amérique du Nord", "North America"), "eur": ("Europe", "Europe"),
         "asi": ("Asie-Pacifique", "Asia-Pacific"), "aml": ("Amérique latine", "Latin America"),
         "moa": ("Moyen-Orient et Afrique", "Middle East and Africa")}
SECTEURS = ["BusEq", "Other", "FIN", "Manuf", "Hlth", "Shops", "Utils", "REIT", "NoDur", "Chems", "Enrgy", "Telcm",
            "Durbl"]                                                          # codes du site (secteur_<code> dans fr.json)
# Nom court de chaque secteur, pour le tableau seulement (le nom complet reste dans le filtre) [M] 04/11/2026
SECTEURS_COURTS = {"BusEq": ("Tech", "Tech"), "Other": ("Autres", "Other"), "FIN": ("Finance", "Finance"),
                   "Manuf": ("Industrie", "Industry"), "Hlth": ("Santé", "Health"), "Shops": ("Commerce", "Retail"),
                   "Utils": ("Serv. publics", "Utilities"), "REIT": ("Immobilier", "Real estate"),
                   "NoDur": ("Conso. courante", "Staples"), "Chems": ("Chimie", "Chemicals"),
                   "Enrgy": ("Énergie", "Energy"), "Telcm": ("Télécoms", "Telecom"),
                   "Durbl": ("Conso. durable", "Durables")}
COMPOSANTES = ["rentabilite", "croissance", "bilan", "dynamique"]           # noms des 4 composantes (fr.json)
# Le facteur de prix borné (note × PER du secteur ÷ PER de la société, 04/11/2026) est retiré le 17/11/2026 :
# variante B de l'audit, choisie par Mathys [M]. Le prix sert de filtre (seuil PRIX_BON_MARCHE), pas de multiplicateur.
NOTE_MIN_AFFAIRES = 50     # deuxième onglet : notes de 50 ou plus seulement [M] 04/11/2026


URL_CLASSEMENT = ("https://github.com/mathysblot3-blip/Notabourse/releases/download/classement/"
                  "classement.parquet")                                      # rangé là par le robot de nuit
FICHIER_LOCAL = SITE / "reference" / "classement.parquet"                     # essais en local


COLONNES_CLASSEMENT = ["symbole", "nom", "pays", "secteur", "note", "Q1", "G1", "R2", "M1", "nb_composantes", "gardee",
                       "capi_usd", "ratio_prix", "perte", "membre", "date_lecture"]   # colonnes lues par la page


def classement_valide(t):
    """Vrai si le fichier a toutes les colonnes dont la page a besoin et au moins une société notée (audit S-C05) :
    un fichier partiel ou d'une autre forme est refusé au lieu de faire planter la page."""
    return (isinstance(t, pd.DataFrame) and set(COLONNES_CLASSEMENT) <= set(t.columns)
            and bool(t["note"].notna().any()))


@st.cache_data(ttl=3600, show_spinner=False)                                  # relu au plus une fois par heure
def charger_classement(signature):
    """Classement : fichier local s'il existe (essais), sinon celui du robot (release GitHub).
    `signature` change toutes les heures ou quand le fichier local change : force la relecture.
    Lève une erreur si le fichier est absent ou incomplet : Streamlit ne garde pas les erreurs en mémoire, donc une panne
    passagère n'est plus affichée pendant une heure (audit S-C05, 17/11/2026)."""
    if FICHIER_LOCAL.exists():
        t = pd.read_parquet(FICHIER_LOCAL)
    else:
        r = requests.get(URL_CLASSEMENT, timeout=30)
        r.raise_for_status()
        t = pd.read_parquet(io.BytesIO(r.content))
    if not classement_valide(t):
        raise ValueError("classement incomplet ou d'une autre forme")
    return t


def preparer(brut):
    """Colonnes utilisées par la page, à partir du fichier : sociétés notées seulement."""
    t = brut[brut["note"].notna() & brut["secteur"].isin(SECTEURS)].copy()
    t["note"] = t["note"].round()                                             # note affichée : entier
    for code, nom in zip(["Q1", "G1", "R2", "M1"], COMPOSANTES):
        t[nom] = t[code].round().astype("Int64")                              # composantes : entiers
    t["capi"] = t["capi_usd"] / 1e9                                           # milliards de dollars
    t["ecartee"] = ~t["gardee"].fillna(True).astype(bool)                     # écartée pour risque de faillite
    t["sp500"] = t["membre"].fillna(False).astype(bool)
    t["accessible"] = t["accessible"].fillna(True).astype(bool) if "accessible" in t.columns else True
    t["pays"] = t["pays"].where(t["pays"].isin(list(PAYS)), "us")
    t["zone"] = t["pays"].map(lambda p: PAYS[p][2])
    t["symbole_fiche"] = t["symbole"]                                         # clic : fiche de cette société
    return t.reset_index(drop=True)


def sans_accent(texte):
    """« Suède » -> « suede » : ordre alphabétique français (les accents ne comptent pas)."""
    return "".join(c for c in unicodedata.normalize("NFD", texte.lower()) if unicodedata.category(c) != "Mn")


def categorie_prix(ratio):
    """Bon marché, dans la norme, chère ou en perte, avec les seuils du site (0,8 et 1,25)."""
    if pd.isna(ratio):
        return "pertes"
    return "bon_marche" if ratio <= PRIX_BON_MARCHE else ("chere" if ratio >= PRIX_CHERE else "norme")


def taille(capi):
    """Grande, moyenne ou petite capitalisation (milliards de dollars)."""
    return "grande" if capi > 10 else ("moyenne" if capi >= 2 else "petite")


# --- Textes ajoutés par la deuxième version (04/11/2026), mêmes règles que TXT -------------------------------------
TXT["fr"].update({
    "fictif": "Prototype : valeurs fictives.", "en_perte": "en perte",
    "seuil": "Seules les sociétés de plus de 1 milliard de dollars de capitalisation sont classées.",
    "accessibles": "Seulement les actions accessibles depuis la France",
    "aide_accessibles": "Sociétés cotées en Europe ou aux États-Unis, ou à Francfort pour les autres : on les trouve "
                        "en général chez les courtiers français. C'est une approximation : vérifie chez ton courtier.",
    "aide_pays": "Code du pays de la bourse principale (FR France, US États-Unis, GB Royaume-Uni, DE Allemagne, "
                 "JP Japon, CN Chine...). Les membres du S&P 500 sont classés aux États-Unis.",
    "aide_facteur": "Multiplie la note : 1,00 = même prix que son secteur ; plafond {haut} (au moins {moins} % "
                    "moins chère) ; plancher {bas} (au moins {plus} % plus chère).",
    "mise_a_jour": "{n} sociétés notées. Chacune est relue environ une fois par semaine ; dernière lecture le {date}.",
    "indisponible": "Le classement n'est pas disponible pour le moment. Réessayez un peu plus tard.", "filtrer": "Filtrer", "recherche": "Rechercher une société",
    "ouvrir": "Ouvrir la fiche : {nom}", "plus": "Plus d'options", "effacer": "Effacer les filtres", "actifs": "{n} sociétés · {k} filtre(s) actif(s)",
    "taille_grande": "Grandes", "taille_moyenne": "Moyennes", "taille_petite": "Petites",
    "aide_taille": "Capitalisation : grandes plus de 10 Md$, moyennes 2 à 10 Md$, petites moins de 2 Md$.",
    "tri": "Trier les meilleures notes par",
    "explication_prix": "Sociétés notées 50 ou plus et au moins 20 % moins chères que leur secteur (PER de la "
                        "société sous 0,8 fois celui du secteur), triées par leur note sur 100. Ce n'est pas une "
                        "liste d'achats.",
    "prudence_prix": "Le prix décrit, il ne prédit pas : de 2010 à 2026, les actions bon marché n'ont fait que "
                     "1,2 point par an de mieux que les chères (écart non significatif). Sociétés en perte ou notées moins de 50 exclues.",
})
TXT["en"].update({
    "fictif": "Prototype: made-up values.", "en_perte": "loss",
    "seuil": "Only companies with a market cap above $1 billion are ranked.",
    "accessibles": "Only stocks available from France",
    "aide_accessibles": "Companies listed in Europe or the United States, or in Frankfurt for the others: French brokers "
                        "usually offer them. This is an approximation: check with your broker.",
    "aide_pays": "Country code of the main exchange (FR France, US United States, GB United Kingdom, DE Germany, "
                 "JP Japan, CN China...). S&P 500 members are listed under the United States.",
    "aide_facteur": "Multiplies the score: 1.00 = same price as its sector; cap {haut} (at least {moins}% "
                    "cheaper); floor {bas} (at least {plus}% more expensive).",
    "mise_a_jour": "{n} companies scored. Each one is reread about once a week; last read on {date}.",
    "indisponible": "The ranking is not available right now. Please try again a little later.", "filtrer": "Filter", "recherche": "Search for a company",
    "ouvrir": "Open the page: {nom}", "plus": "More options", "effacer": "Clear filters", "actifs": "{n} companies · {k} active filter(s)",
    "taille_grande": "Large", "taille_moyenne": "Mid", "taille_petite": "Small",
    "aide_taille": "Market cap: large over $10bn, mid $2bn to $10bn, small under $2bn.",
    "tri": "Sort the best scores by",
    "explication_prix": "Companies scored 50 or more and at least 20% cheaper than their sector (P/E below 0.8 times "
                        "the sector's), sorted by score out of 100. This is not a shopping list.",
    "prudence_prix": "Price describes, it does not predict: from 2010 to 2026, cheap stocks beat expensive ones by "
                     "only 1.2 points a year (not significant). Loss-making companies and scores below 50 left out.",
})
CLES_FILTRES = ["cl_zones", "cl_pays", "cl_secteurs", "cl_tailles", "cl_indice", "cl_ecartees",
                "cl_completes", "cl_accessibles"]                                               # remis à zéro par « Effacer les filtres »


def effacer_filtres():
    """Remet tous les filtres à leur valeur de départ (appelé par le bouton, avant l'affichage suivant)."""
    for k in CLES_FILTRES:
        st.session_state.pop(k, None)                                         # clé retirée : valeur par défaut


# --- Page ---------------------------------------------------------------------------------------------------------
st.session_state.setdefault("cl_nombre", 50)                                 # valeurs de départ données ici, pas
                                                                              # dans le champ : ainsi gardée d'une
                                                                              # page à l'autre sans avertissement
T = textes()                                                                  # textes du site (secteurs, composantes)
L = st.session_state.get("langue", "fr")
X = TXT[L]                                                                    # textes du prototype
i_lg = 0 if L == "fr" else 1                                                  # colonne du nom de pays et de zone

st.html(f"""<style>
.st-key-cl_filtres {{ background: {SURFACE}; border-left: 3px solid {JAUNE} !important; }}   /* zone des filtres :
                                                       toujours visible, différente des « détails » repliables */
.st-key-cl_filtres_titre p {{ font-family: 'Doto', monospace; font-weight: 900; color: {JAUNE}; font-size: 1.15rem;
    margin: 0; text-transform: uppercase; }}
@media (max-width: 480px) {{ [data-testid="stMainBlockContainer"] h1 {{ font-size: 2.6rem; }} }}   /* titre sur une
                                                       ligne sur téléphone */
</style>""")
st.title(X["titre"])
try:
    brut = charger_classement((FICHIER_LOCAL.stat().st_mtime if FICHIER_LOCAL.exists() else 0,
                               pd.Timestamp.now().floor("h")))                 # relu chaque heure
except Exception:
    logging.exception("Classement indisponible")                              # détail dans le journal du serveur
    brut = None
if brut is None:
    st.info(X["indisponible"])                                                # robot pas encore passé, ou panne
    st.stop()
t = preparer(brut)
lues = brut.loc[~brut["membre"].fillna(False).astype(bool), "date_lecture"]
st.caption(X["mise_a_jour"].format(n=len(t), date=pd.Timestamp(lues.max() if lues.notna().any()
                                                                else brut["date_lecture"].max()).strftime("%d/%m/%Y")))
t["prix"] = t["ratio_prix"].map(categorie_prix)                               # catégorie de prix
t["taille"] = t["capi"].map(taille)
t["ecart_prix"] = (t["ratio_prix"] - 1) * 100                                 # +25 = 25 % plus chère que le secteur
t["prix_txt"] = [X["en_perte"] if perte else ("-" if pd.isna(e) else f"{e:+.0f} %")   # texte affiché
                 for e, perte in zip(t["ecart_prix"], t["perte"].fillna(False))]
t["code_pays"] = t["pays"].str.upper()                                       # FR, US, JP... (codes ISO)
DRAPEAUX = {p: adresse_drapeau(p) for p in PAYS}                              # une adresse par pays [M] 20/11/2026
t["drapeau"] = t["pays"].map(DRAPEAUX)                                        # image affichée devant le code
t["secteur_court"] = t["secteur"].map(lambda s: SECTEURS_COURTS[s][i_lg])

# --- Filtres : un cadre toujours visible, les plus utiles en premier ----------------------------------------------
TRIS = {"note": X["col_note"], **{k: T[k] for k in COMPOSANTES}, "ecart_prix": X["col_prix"], "capi": X["col_capi"]}
with st.container(border=True, key="cl_filtres"):
    st.container(key="cl_filtres_titre").markdown(X["filtrer"])               # titre « FILTRER »
    a, b = st.columns(2)                                                      # 4 menus déroulants, 2 par ligne
    zones = a.multiselect(X["zone"], sorted(ZONES, key=lambda z: sans_accent(ZONES[z][i_lg])),   # de A à Z
                          format_func=lambda z: ZONES[z][i_lg], key="cl_zones", filter_mode=None, placeholder=X["toutes"])
    pays_possibles = sorted((p for p in PAYS if not zones or PAYS[p][2] in zones),
                            key=lambda p: sans_accent(PAYS[p][i_lg]))         # pays des zones choisies, de A à Z
    pays = b.multiselect(X["pays"], pays_possibles, format_func=lambda p: PAYS[p][i_lg], key="cl_pays", filter_mode=None,
                         placeholder=X["tout"])
    c, d = st.columns(2)
    secteurs = c.multiselect(X["secteur"], sorted(SECTEURS, key=lambda s: sans_accent(T[f"secteur_{s}"])),   # A à Z
                             format_func=lambda s: T[f"secteur_{s}"], key="cl_secteurs", filter_mode=None, placeholder=X["tout"])
    tailles = d.multiselect(X["taille"], ["grande", "moyenne", "petite"], format_func=lambda k: X[f"taille_{k}"],
                            key="cl_tailles", filter_mode=None, help=X["aide_taille"], placeholder=X["toutes"])
    accessibles = st.toggle(X["accessibles"], key="cl_accessibles", help=X["aide_accessibles"])   # [M] 06/11/2026
    h, i, j = st.columns(3, vertical_alignment="center")
    with i.popover(X["plus"], width="stretch"):                               # options moins courantes, à part
        indice = st.selectbox(X["indice"], ["tout", "sp", "hors", *INDICES], key="cl_indice", filter_mode=None,
                              format_func=lambda k: X["toutes"] if k == "tout" else X.get(f"indice_{k}", k))
        tri = st.selectbox(X["tri"], list(TRIS), format_func=lambda k: TRIS[k], key="cl_tri1", filter_mode=None)
        croissant = st.selectbox(X["ordre"], [False, True], key="cl_ordre1", filter_mode=None,
                                 format_func=lambda v: X["croissant"] if v else X["decroissant"])
        nombre = st.selectbox(X["nombre"], [25, 50, 100, "tout"], key="cl_nombre", filter_mode=None,
                              format_func=lambda k: X["toutes"] if k == "tout" else str(k))
        ecartees = st.toggle(X["ecartees"], key="cl_ecartees")
        completes = st.toggle(X["completes"], key="cl_completes")
        detail = st.toggle(X["detail"], key="cl_detail")
    j.button(X["effacer"], on_click=effacer_filtres, width="stretch", key="cl_effacer")

f = t                                                                         # on applique chaque filtre choisi
if zones:
    f = f[f["zone"].isin(zones)]
if pays:
    f = f[f["pays"].isin(pays)]
if secteurs:
    f = f[f["secteur"].isin(secteurs)]
if tailles:
    f = f[f["taille"].isin(tailles)]
if indice == "sp":
    f = f[f["sp500"]]
elif indice == "hors":
    f = f[~f["sp500"]]
elif indice != "tout":                                                        # Nikkei 225, CAC 40... [M] 06/11/2026
    f = f[[indice in indices_de(s, n) for s, n in zip(f["symbole"], f["nom"])]]
if not ecartees:
    f = f[~f["ecartee"]]
if accessibles:
    f = f[f["accessible"]]
if completes:
    f = f[f["nb_composantes"] == 4]
actifs = sum(bool(v) for v in (zones, pays, secteurs, tailles, indice != "tout", ecartees,
                                completes, accessibles))                                   # nombre de filtres choisis
h.markdown(X["actifs"].format(n=len(f), k=actifs))


# --- Tableau commun aux deux onglets ------------------------------------------------------------------------------
def colonnes(avec_score):
    """Réglages d'affichage des colonnes (titres, barres, formats)."""
    c = {"rang": st.column_config.NumberColumn(X["col_rang"], width=45),
         "nom": st.column_config.TextColumn(X["col_societe"], width=160),   # la note reste visible sur téléphone
         "drapeau": st.column_config.ImageColumn(X["col_pays"], help=X["aide_pays"], width=45),   # drapeau [M] 20/11
         "code_pays": st.column_config.TextColumn(" ", width=40),             # code à côté du drapeau
         "secteur_court": st.column_config.TextColumn(X["col_secteur"], width=125),
         "note": st.column_config.ProgressColumn(X["col_note"], min_value=0, max_value=100, format="%d", width=110),
         "prix_txt": st.column_config.TextColumn(X["col_prix"], help=X["aide_prix"], width=95),
         "capi": st.column_config.NumberColumn(X["col_capi"], format="%.1f", width=95)}
    c.update({k: st.column_config.NumberColumn(T[k], width=85) for k in COMPOSANTES})
    if avec_score:
        c["facteur_txt"] = st.column_config.TextColumn(X["col_facteur"], help=X["aide_facteur"], width=90)
        c["score_prix"] = st.column_config.ProgressColumn(X["col_score"], min_value=0, max_value=150, format="%d",
                                                          width=130)
    return c


def afficher(tableau, cle, avec_score):
    """Numérote, coupe au nombre de lignes voulu et affiche ; un clic sur une ligne montre son résumé."""
    if tableau.empty:
        st.info(X["aucune"])
        return
    if nombre != "tout":
        tableau = tableau.head(int(nombre or 50))
    ordre = (["rang", "nom"]                                                 # l'essentiel à gauche : visible
             + (["score_prix", "note", "facteur_txt"] if avec_score else ["note"])   # sans défiler sur téléphone
             + ["drapeau", "code_pays", "secteur_court"] + (COMPOSANTES if detail else []) + ["prix_txt", "capi"])
    zone_bouton = st.container()                                              # place réservée AU-DESSUS du tableau :
    # sous un tableau de 750 pixels, le bouton n'était pas visible après le clic et le lien paraissait cassé
    # (signalé par Mathys le 20/11/2026)
    choix = st.dataframe(tableau[ordre], column_config=colonnes(avec_score), hide_index=True, width="stretch",
                         row_height=44, height=min(42 + 44 * len(tableau), 750),   # lignes plus hautes, plus lisibles
                         on_select="rerun", selection_mode="single-cell", key=cle)   # un clic sur une case
    cases = choix.selection.get("cells", [])                                  # case cliquée (ou aucune)
    if cases:                                                                 # une case choisie : on propose un bouton
        ligne = cases[0][0] if isinstance(cases[0], (list, tuple)) else cases[0]["row"]   # (S-A04, WCAG 3.2.2)
        choisie = tableau.iloc[int(ligne)]                                    # la société de la ligne choisie
        # Avant : le simple choix d'une case (ou une flèche du clavier) changeait de page. Maintenant, seul ce
        # bouton, que le visiteur déclenche exprès, ouvre la fiche : la sélection ne change plus rien d'elle-même.
        bouton = dict(key=cle + "_ouvrir", type="primary", icon=":material/arrow_forward:")   # jaune, bien visible
        if zone_bouton.button(X["ouvrir"].format(nom=choisie["nom"]), **bouton):   # au-dessus du tableau
            st.session_state["ouvrir_symbole"] = choisie["symbole_fiche"]     # [M] 04/11/2026
            st.switch_page("vues/recherche.py")


onglets = [X["onglet_notes"], X["onglet_prix"]]
if st.session_state.get("cl_onglet") not in onglets:                          # langue changée : nom de l'onglet
    st.session_state.pop("cl_onglet", None)                                   # inconnu, retour au premier
onglet1, onglet2 = st.tabs(onglets, key="cl_onglet", on_change="rerun")       # onglet gardé d'une page à l'autre [M]

with onglet1:
    g = f.sort_values([tri, "note"], ascending=[bool(croissant), False], na_position="last").copy()
    g["rang"] = range(1, len(g) + 1)
    afficher(g, "cl_tableau1", avec_score=False)
    st.caption(X["seuil"])                                                    # [M] 04/11/2026

with onglet2:
    # Variante B [M] 17/11/2026 : note de 50 ou plus ET au moins 20 % moins chère que son secteur (même seuil que la
    # zone « bon marché » de la fiche), triée par la note. Plus de multiplication note × prix : le prix filtre, il ne
    # classe pas (le facteur saturait : 47 des 50 premières lignes au plafond, audit 3.4).
    g = f[f["ratio_prix"].notna() & (f["note"] >= NOTE_MIN_AFFAIRES) & (f["ratio_prix"] <= PRIX_BON_MARCHE)].copy()
    g = g.sort_values(["note", "ratio_prix"], ascending=[False, True])        # à note égale, la moins chère d'abord
    g["rang"] = range(1, len(g) + 1)
    afficher(g, "cl_tableau2", avec_score=False)                              # mêmes colonnes que le 1er onglet
    st.markdown(X["explication_prix"])                                        # explications sous le tableau [M]
    st.caption(X["prudence_prix"])
    st.caption(X["seuil"])
