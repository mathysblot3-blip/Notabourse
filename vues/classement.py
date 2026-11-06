"""Page Classement (04/11/2026) : les grandes sociétés cotées du monde, classées par leur note.

Deux classements :
  1. les meilleures notes ;
  2. les meilleures notes et les moins chères : note × facteur de prix, où facteur = PER du secteur ÷ PER de la société,
     plafonné entre 0,67 et 1,5 [M] 04/11/2026 (valeurs : [P]).
Des filtres communs aux deux : zone, pays (de A à Z), secteur, taille, puis dans « Plus d'options » : indice,
sociétés écartées, données complètes. Tri au choix, ou d'un clic sur le titre d'une colonne.
Données : reference/classement.parquet, construit chaque nuit par reference/construire_classement.py et rangé par le
robot dans la release « classement » du dépôt ; le site le télécharge de là (le fichier local sert aux essais).
"""
import io               # lire un fichier téléchargé sans l'écrire sur le disque
import unicodedata      # lettres sans accent, pour trier les pays (Suède avant Suisse)

import pandas as pd     # tableaux de données
import requests         # téléchargement du classement
import streamlit as st  # interface web

from notabourse.constantes import PRIX_BON_MARCHE, PRIX_CHERE, WINSOR_BAS, WINSOR_HAUT   # seuils du site
from notabourse.indices import INDICES, indices_de                # Nikkei 225, CAC 40...
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
        "etoiles_min": "Étoiles au minimum", "ecartees": "Montrer les sociétés écartées pour risque de faillite",
        "completes": "Seulement les notes complètes (4 composantes sur 4)", "tri": "Trier par",
        "ordre": "Ordre", "decroissant": "Du plus haut au plus bas", "croissant": "Du plus bas au plus haut",
        "nombre": "Nombre de lignes", "tout": "Tous", "toutes": "Toutes",
        "taille_grande": "Grandes (plus de 10 Md$)", "taille_moyenne": "Moyennes (2 à 10 Md$)",
        "taille_petite": "Petites (moins de 2 Md$)",
        "indice_sp": "Membres du S&P 500", "indice_hors": "Hors S&P 500",
        "prix_bon_marche": "Bon marché", "prix_norme": "Dans la norme", "prix_chere": "Chère",
        "prix_pertes": "En perte (pas de PER)",
        "onglet_notes": "Meilleures notes", "onglet_prix": "Bonnes affaires",
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
        "etoiles_min": "Minimum stars", "ecartees": "Show companies excluded for bankruptcy risk",
        "completes": "Complete scores only (4 components out of 4)", "tri": "Sort by",
        "ordre": "Order", "decroissant": "Highest first", "croissant": "Lowest first",
        "nombre": "Number of rows", "tout": "All", "toutes": "All",
        "taille_grande": "Large (over $10bn)", "taille_moyenne": "Mid ($2bn to $10bn)",
        "taille_petite": "Small (under $2bn)",
        "indice_sp": "S&P 500 members", "indice_hors": "Outside the S&P 500",
        "prix_bon_marche": "Cheap", "prix_norme": "In line", "prix_chere": "Expensive",
        "prix_pertes": "Loss-making (no P/E)",
        "onglet_notes": "Best scores", "onglet_prix": "Good deals",
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
# Bornes du facteur de prix [M] 04/11/2026 (principe : un prix extrême ne doit pas emporter le classement).
# Valeurs [R] : la même winsorisation que la note, aux 5e et 95e centiles (MSCI 2013, Quality Indices Methodology,
# p. 4 ; constantes WINSOR_BAS et WINSOR_HAUT), appliquée au rapport PER / PER du secteur des membres du S&P 500, la
# population de référence de tout le site. Recalculées à chaque nouvelle référence. Pourquoi borner surtout le côté
# bon marché : Liu, Nissim et Thomas (2002, p. 153) notent que l'écart au prix donné par le multiple du secteur est
# borné d'un côté mais pas de l'autre ; le facteur peut donc devenir aussi grand qu'on veut.
FACTEUR_SECOURS = (1 / 1.5, 1.5)                                              # si trop peu de membres ont un prix


def virgule(x):
    """1.5 -> « 1,50 » en français, « 1.50 » en anglais."""
    texte = f"{x:.2f}"
    return texte.replace(".", ",") if st.session_state.get("langue", "fr") == "fr" else texte


def bornes_facteur(brut):
    """(plancher, plafond) du facteur = 1 / (95e et 5e centiles du rapport PER / PER du secteur des membres)."""
    garde = (brut["membre"].fillna(False).astype(bool) & brut["gardee"].fillna(False).astype(bool)
             & ~brut["perte"].fillna(True).astype(bool))                      # membres gardés et bénéficiaires
    membres = brut.loc[garde, "ratio_prix"].dropna()
    if len(membres) < 100:
        return FACTEUR_SECOURS
    return 1 / membres.quantile(WINSOR_HAUT), 1 / membres.quantile(WINSOR_BAS)


NOTE_MIN_AFFAIRES = 50     # « Bonnes affaires » : notes de 50 ou plus seulement [M] 04/11/2026


URL_CLASSEMENT = ("https://github.com/mathysblot3-blip/Notabourse/releases/download/classement/"
                  "classement.parquet")                                      # rangé là par le robot de nuit
FICHIER_LOCAL = SITE / "reference" / "classement.parquet"                     # essais en local


@st.cache_data(ttl=3600, show_spinner=False)                                  # relu au plus une fois par heure
def charger_classement(signature):
    """Classement : fichier local s'il existe (essais), sinon celui du robot (release GitHub). None si indisponible.
    `signature` change toutes les heures ou quand le fichier local change : force la relecture."""
    try:
        if FICHIER_LOCAL.exists():
            return pd.read_parquet(FICHIER_LOCAL)
        r = requests.get(URL_CLASSEMENT, timeout=30)
        r.raise_for_status()
        return pd.read_parquet(io.BytesIO(r.content))
    except Exception:
        return None                                                           # la page le dit au visiteur


def preparer(brut):
    """Colonnes utilisées par la page, à partir du fichier : sociétés notées seulement."""
    t = brut[brut["note"].notna() & brut["secteur"].isin(SECTEURS)].copy()
    t["note"] = t["note"].round()                                             # note affichée : entier
    for code, nom in zip(["Q1", "G1", "R2", "M1"], COMPOSANTES):
        t[nom] = t[code].round().astype("Int64")                              # composantes : entiers
    t["capi"] = t["capi_usd"] / 1e9                                           # milliards de dollars
    t["ecartee"] = ~t["gardee"].fillna(True).astype(bool)                     # écartée pour risque de faillite
    t["sp500"] = t["membre"].fillna(False).astype(bool)
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
    "aide_pays": "Code du pays de la bourse principale (FR France, US États-Unis, GB Royaume-Uni, DE Allemagne, "
                 "JP Japon, CN Chine...). Les membres du S&P 500 sont classés aux États-Unis.",
    "aide_facteur": "Multiplie la note : 1,00 = même prix que son secteur ; plafond {haut} (au moins {moins} % "
                    "moins chère) ; plancher {bas} (au moins {plus} % plus chère).",
    "mise_a_jour": "{n} sociétés notées. Chacune est relue environ une fois par semaine ; dernière lecture le {date}.",
    "indisponible": "Le classement n'est pas disponible pour le moment. Réessayez un peu plus tard.", "filtrer": "Filtrer", "recherche": "Rechercher une société",
    "plus": "Plus d'options", "effacer": "Effacer les filtres", "actifs": "{n} sociétés · {k} filtre(s) actif(s)",
    "taille_grande": "Grandes", "taille_moyenne": "Moyennes", "taille_petite": "Petites",
    "aide_taille": "Capitalisation : grandes plus de 10 Md$, moyennes 2 à 10 Md$, petites moins de 2 Md$.",
    "tri": "Trier les meilleures notes par",
    "explication_prix": "Note × facteur de prix (PER du secteur ÷ PER de la société). Exemple : notée 80 et 25 % "
                        "moins chère que son secteur : 80 × 1,33 = 107. Facteur plafonné à {haut} ({moins} % moins "
                        "chère ou plus) et à {bas} ({plus} % plus chère ou plus) : les 5 % des membres du S&P 500 "
                        "les moins chers et les 5 % les plus chers, la même règle que pour la note (MSCI, 2013). Un "
                        "prix extrême vient souvent d'un bénéfice exceptionnel ou d'une donnée douteuse.",
    "prudence_prix": "Le prix décrit, il ne prédit pas : de 2010 à 2026, les actions bon marché n'ont fait que "
                     "1,2 point par an de mieux que les chères (écart non significatif). Sociétés en perte ou notées moins de 50 exclues.",
})
TXT["en"].update({
    "fictif": "Prototype: made-up values.", "en_perte": "loss",
    "seuil": "Only companies with a market cap above $1 billion are ranked.",
    "aide_pays": "Country code of the main exchange (FR France, US United States, GB United Kingdom, DE Germany, "
                 "JP Japan, CN China...). S&P 500 members are listed under the United States.",
    "aide_facteur": "Multiplies the score: 1.00 = same price as its sector; cap {haut} (at least {moins}% "
                    "cheaper); floor {bas} (at least {plus}% more expensive).",
    "mise_a_jour": "{n} companies scored. Each one is reread about once a week; last read on {date}.",
    "indisponible": "The ranking is not available right now. Please try again a little later.", "filtrer": "Filter", "recherche": "Search for a company",
    "plus": "More options", "effacer": "Clear filters", "actifs": "{n} companies · {k} active filter(s)",
    "taille_grande": "Large", "taille_moyenne": "Mid", "taille_petite": "Small",
    "aide_taille": "Market cap: large over $10bn, mid $2bn to $10bn, small under $2bn.",
    "tri": "Sort the best scores by",
    "explication_prix": "Score × price factor (sector P/E ÷ company P/E). Example: scored 80 and 25% cheaper than "
                        "its sector: 80 × 1.33 = 107. Factor capped at {haut} ({moins}% cheaper or more) and {bas} "
                        "({plus}% more expensive or more): the cheapest 5% and the most expensive 5% of S&P 500 "
                        "members, the same rule as for the score (MSCI, 2013). An extreme price often comes from a "
                        "one-off profit or a doubtful figure.",
    "prudence_prix": "Price describes, it does not predict: from 2010 to 2026, cheap stocks beat expensive ones by "
                     "only 1.2 points a year (not significant). Loss-making companies and scores below 50 left out.",
})
CLES_FILTRES = ["cl_zones", "cl_pays", "cl_secteurs", "cl_tailles", "cl_indice", "cl_ecartees",
                "cl_completes"]                                               # remis à zéro par « Effacer les filtres »


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
brut = charger_classement((FICHIER_LOCAL.stat().st_mtime if FICHIER_LOCAL.exists() else 0,
                           pd.Timestamp.now().floor("h")))                     # relu chaque heure
if brut is None or brut["note"].notna().sum() == 0:
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
if completes:
    f = f[f["nb_composantes"] == 4]
actifs = sum(bool(v) for v in (zones, pays, secteurs, tailles, indice != "tout", ecartees,
                                completes))                                   # nombre de filtres choisis
h.markdown(X["actifs"].format(n=len(f), k=actifs))


# --- Tableau commun aux deux onglets ------------------------------------------------------------------------------
def colonnes(avec_score):
    """Réglages d'affichage des colonnes (titres, barres, formats)."""
    c = {"rang": st.column_config.NumberColumn(X["col_rang"], width=45),
         "nom": st.column_config.TextColumn(X["col_societe"], width=160),   # la note reste visible sur téléphone
         "code_pays": st.column_config.TextColumn(X["col_pays"], help=X["aide_pays"], width=55),
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
             + ["code_pays", "secteur_court"] + (COMPOSANTES if detail else []) + ["prix_txt", "capi"])
    choix = st.dataframe(tableau[ordre], column_config=colonnes(avec_score), hide_index=True, width="stretch",
                         row_height=44, height=min(42 + 44 * len(tableau), 750),   # lignes plus hautes, plus lisibles
                         on_select="rerun", selection_mode="single-cell", key=cle)   # un clic sur une case
    cases = choix.selection.get("cells", [])                                  # case cliquée (ou aucune)
    if cases:                                                                 # un clic : analyse complète de la
        ligne = cases[0][0] if isinstance(cases[0], (list, tuple)) else cases[0]["row"]   # société, page Recherche
        st.session_state["ouvrir_symbole"] = tableau.iloc[int(ligne)]["symbole_fiche"]   # [M] 04/11/2026
        st.switch_page("vues/recherche.py")


onglet1, onglet2 = st.tabs([X["onglet_notes"], X["onglet_prix"]])

with onglet1:
    g = f.sort_values([tri, "note"], ascending=[bool(croissant), False], na_position="last").copy()
    g["rang"] = range(1, len(g) + 1)
    afficher(g, "cl_tableau1", avec_score=False)
    st.caption(X["seuil"])                                                    # [M] 04/11/2026

with onglet2:
    g = f[f["ratio_prix"].notna() & (f["note"] >= NOTE_MIN_AFFAIRES)].copy()   # une note faible mais très bon
    bas, haut = bornes_facteur(brut)                                          # 95e et 5e centiles des membres
    g["facteur"] = (1 / g["ratio_prix"]).clip(bas, haut)                          # marché ne passe pas devant ;
    g["score_prix"] = (g["note"] * g["facteur"]).round()                          # PER secteur ÷ PER société, borné
    g["facteur_txt"] = g["facteur"].map(lambda v: "× " + virgule(v))
    g = g.sort_values(["score_prix", "note"], ascending=False)
    g["rang"] = range(1, len(g) + 1)
    chiffres = {"haut": virgule(haut), "bas": virgule(bas), "moins": round(100 * (1 - 1 / haut)),
                "plus": round(100 * (1 / bas - 1))}                           # bornes dites au visiteur
    X = {**X, "aide_facteur": X["aide_facteur"].format(**chiffres)}           # aide du titre de la colonne
    afficher(g, "cl_tableau2", avec_score=True)
    st.markdown(X["explication_prix"].format(**chiffres))                     # explications sous le tableau [M]
    st.caption(X["prudence_prix"])
    st.caption(X["seuil"])
