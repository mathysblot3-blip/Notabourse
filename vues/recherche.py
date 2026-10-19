"""Page principale : recherche d'une société, puis fiche de sa note (cahier des charges §3 et §4)."""
import pandas as pd                    # dates et tableaux
import plotly.graph_objects as go      # jauge de la note
import streamlit as st                 # interface web

from notabourse.calcul import charger_reference, noter_hors_indice, ratios_et_croissances
from notabourse.classement import charger_correspondance_yahoo
from notabourse.fiche import fiche_hors_indice, fiche_membre
from notabourse.phrases import phrases, rendre
from notabourse.sources import DonneesIndisponibles, cotations, table_cik_sec
from vues.commun import SITE, date, dollars, nombre, pct, textes

BLEU = "#5B8DEF"                                                              # couleur des barres, jauge, étoiles
COULEURS = {"vert": "#2E9E5B", "orange": "#E8912D", "rouge": "#D64545", None: "#4A4F5C"}   # réservées au garde-fou
VIOLET = "#8E7CC3"                                                            # bandeau « exclue » (pas une couleur du garde-fou)
JAUNE = "#C9A227"                                                             # point de vigilance (affichage seulement)
STATUTS = {"bonne": COULEURS["vert"], "vigilance": JAUNE, "exclue": VIOLET, "inconnue": COULEURS[None]}


# --- Données, gardées en mémoire (cache) ------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _reference(signature):
    """Référence S&P 500 ; `signature` (date de modification du fichier) force la relecture quand il change."""
    return charger_reference()


def reference():
    """Référence de la semaine (relue seulement si le robot l'a mise à jour)."""
    return _reference((SITE / "reference" / "reference.parquet").stat().st_mtime)


@st.cache_data(show_spinner=False)
def renvois_categories():
    """Autres catégories d'actions d'un membre (GOOG -> GOOGL) d'après membres_sp500.csv."""
    m = pd.read_csv(SITE / "reference" / "membres_sp500.csv")
    return m.dropna(subset=["autre_categorie_de"]).set_index("symbole")["autre_categorie_de"].to_dict()


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def propositions(texte):
    """Cotations proposées pour une recherche (24 heures en mémoire)."""
    return cotations(texte)


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def table_cik():
    """Table symbole -> CIK de la SEC (24 heures en mémoire) ; None si la SEC ne répond pas."""
    try:
        return table_cik_sec()
    except Exception:
        return None


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def calculer_fiche(symbole, signature):
    """Fiche d'une société : tirée de la référence pour un membre, calculée en direct sinon [M] ; 24 heures en mémoire."""
    ref, cr = _reference(signature)
    s = renvois_categories().get(symbole, symbole)                           # GOOG -> GOOGL
    if s in ref.index:
        return fiche_membre(s, ref, cr)
    D = pd.Timestamp.today().normalize()
    ligne, c = ratios_et_croissances(symbole, D, "direct", table_cik=table_cik(),
                                     correspondance=charger_correspondance_yahoo())
    if ligne["groupe"] is None:
        return {"erreur": "classement"}
    return fiche_hors_indice(noter_hors_indice(ligne, c, ref, cr), c, ref)


# --- Petits éléments d'affichage --------------------------------------------------------------------------------
ETOILE = "12,1.5 15.1,8.2 22.5,9 17,14 18.5,21.5 12,17.8 5.5,21.5 7,14 1.5,9 8.9,8.2"   # sommets d'une étoile


def etoiles_html(nb):
    """Cinq étoiles dessinées en SVG, remplies de 0 à 100 % (demi-étoiles) : un dégradé à bord net coupe l'étoile pile
    au bon endroit (l'ancienne version, un caractère ★ colorié, se décalait selon la police)."""
    morceaux = []
    for i in range(5):
        rempli = max(0.0, min(1.0, nb - i)) * 100                              # part remplie de cette étoile (0 à 100 %)
        morceaux.append(
            f'<svg width="34" height="34" viewBox="0 0 24 24" style="margin-right:3px">'
            f'<defs><linearGradient id="etoile{i}">'                           # dégradé propre à cette étoile
            f'<stop offset="{rempli}%" stop-color="{BLEU}"/><stop offset="{rempli}%" stop-color="#3A3F4B"/>'
            f'</linearGradient></defs><polygon points="{ETOILE}" fill="url(#etoile{i})"/></svg>')
    return "".join(morceaux)


def jauge(note):
    """Jauge de 0 à 100 (plotly)."""
    fig = go.Figure(go.Indicator(mode="gauge+number", value=note, number={"suffix": " / 100", "font": {"size": 34}},
                                 gauge={"axis": {"range": [0, 100]}, "bar": {"color": BLEU},
                                        "bgcolor": "#1B1F2A", "borderwidth": 0}))
    fig.update_layout(height=190, margin=dict(l=20, r=20, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      font={"color": "#E8EAED"})
    return fig


def pastille(texte, couleur):
    """Petit encadré coloré (voyant du garde-fou)."""
    return (f'<div style="background:{COULEURS[couleur]};border-radius:8px;padding:10px 12px;margin-bottom:6px;'
            f'color:white">{texte}</div>')


def valeur_ratio(x, fmt, L):
    """Valeur d'un ratio selon son format (pourcentage, dollars, années)."""
    if fmt == "pct":
        return pct(x, L)
    if fmt == "usd":
        return dollars(x, L)
    return nombre(x, L, 1)


def mesure_voyant(v, T, L):
    """Phrase qui décrit la mesure d'un voyant."""
    m = v["mesure"] or {}
    if v["voyant"] == "trésorerie":
        if m.get("flux_positif"):
            return T["mesure_flux_positif"]
        return T["mesure_annees"].format(x=nombre(m["annees"], L, 1)) if m.get("annees") is not None else T["mesure_inconnue"]
    if v["voyant"] == "endettement":
        return T["mesure_tlmta"].format(x=pct(m.get("tlmta"), L, 0)) if m.get("tlmta") is not None else T["mesure_inconnue"]
    if v["voyant"] == "intérêts":
        if m.get("sans_interets"):
            return T["mesure_sans_interets"]
        if m.get("ebitda_negatif"):
            return T["mesure_ebitda_negatif"]
        c = m.get("couverture")
        return T["mesure_couverture"].format(x=nombre(c, L, 1)) if c is not None and pd.notna(c) else T["mesure_inconnue"]
    r = m.get("ratio")
    return T["mesure_ratio"].format(x=pct(r, L, 1)) if r is not None and pd.notna(r) else T["mesure_inconnue"]


def md(texte):
    """Texte sûr pour st.markdown : un « $ » seul serait lu comme le début d'une formule mathématique."""
    return texte.replace("$", "\\$")


def texte_phrases(liste, T, L):
    """Phrases simples à la suite : la principale en gras."""
    return " ".join(f"**{md(rendre(p, T, L))}**" if p["titre"] else md(rendre(p, T, L)) for p in liste)


def detail_note(f, T, L, dp):
    """Menu dépliant de la note : note M, jauge, rang dans le S&P 500, membres proches, dates des données."""
    n, cp = f["note"], f["comparaison"]
    c1, c2 = st.columns([1.4, 1])
    c1.plotly_chart(jauge(n["sur_100"]), width="stretch", config={"displayModeBar": False})
    c1.caption(T["aide_note_100"])
    c2.metric(T["note_m"], nombre(n["M"], L, 2), help=T["aide_note_m"])
    c2.caption(f"{nombre(n['etoiles'], L, 1)} / 5 ★")
    if cp:
        st.markdown(f"**{T['comparaison']}**  \n" + T["rang"].format(rang=cp["rang"], nb=cp["nb"]) + "  \n" +
                    T["moyenne_secteur_note"].format(x=nombre(cp["moyenne_secteur"], L, 0), n=cp["nb_secteur"]))
        st.markdown(f"**{T['proches']}**")
        st.table(pd.DataFrame([{"": p["symbole"], T["col_societe"]: p["nom"], T["note_sur_100"]: nombre(p["note"], L, 0)}
                               for p in cp["proches"]]))
    st.caption(T["dates_donnees"].format(exercice=date(f["dates"]["exercice"], L), cours=date(f["dates"]["cours"], L),
                                         reference=date(f["dates"]["reference"], L)))


def detail_composante(f, c, T, L, dp):
    """Menu dépliant d'une partie : ce qu'elle mesure, puis ses chiffres (ratios ou croissances annuelles)."""
    cle = f"phrase_{c['nom']}_fin" if f["groupe"] == "FIN" and c["nom"] in ("rentabilite", "bilan") else f"phrase_{c['nom']}"
    st.caption(T[cle] + (f" ({T['historique_court']})" if c["code"] == "G1" else ""))
    if c["code"] == "G1":
        if not c["croissances"]:
            st.write(T["donnees_insuffisantes"])
        for serie, taux in c["croissances"].items():
            st.markdown(f"**{T[serie]}** ({T['annees']}){dp}" + " ; ".join(pct(x, L) for x in taux))
    else:
        st.table(pd.DataFrame([{T["col_ratio"]: T[d["ratio"]], T["col_valeur"]: valeur_ratio(d["valeur"], d["format"], L),
                                T["col_moyenne_secteur"]: valeur_ratio(d["moyenne_secteur"], d["format"], L),
                                T["col_centile"]: nombre(d["centile"], L, 0)} for d in c["detail"]]))


def detail_sante(f, T, L, dp):
    """Menu dépliant de la santé financière : voyants du garde-fou, moyenne, conditions d'exclusion."""
    gf = f["garde_fou"]
    st.caption(T["phrase_garde_fou"])
    cols = st.columns(len(gf["voyants"]) + 1)
    for col, v in zip(cols, gf["voyants"]):
        note = "" if v["note"] is None else f" · {nombre(v['note'], L, 2)}"
        col.markdown(pastille(f"<b>{T['voyant_' + v['voyant']]}</b>{note}<br><small>{mesure_voyant(v, T, L)}</small>",
                              v["couleur"]), unsafe_allow_html=True)
    moy = "-" if gf["moyenne"] is None else nombre(gf["moyenne"], L, 2)
    cols[-1].markdown(pastille(f"<b>{T['moyenne_voyants']}</b><br>{moy}", gf["couleur"]), unsafe_allow_html=True)
    st.markdown(f"**{T['conditions']}**")
    for cnd in gf["conditions"]:
        etat = T["remplie"] if cnd["remplie"] else (T["donnee_manquante"] if cnd.get("donnee_manquante") else T["non_remplie"])
        st.markdown(f"- {T['cond_' + cnd['condition']]}{dp}**{etat}**")
    if gf["exclue"]:
        st.caption(T["explication_exclusion"])


def badge(texte, couleur):
    """Étiquette colorée (statut de santé financière)."""
    return (f'<span style="background:{couleur};color:white;border-radius:6px;padding:3px 10px;font-size:0.9rem;'
            f'font-weight:600">{texte}</span>')


def afficher_fiche(f, T, L, bourse=None):
    """Fiche épurée : en-tête, note et sa phrase, une ligne par partie avec sa phrase, santé financière ; tous les
    chiffres et explications de calcul sont dans des menus dépliants fermés [M] 19/10/2026."""
    dp = " : " if L == "fr" else ": "                                         # deux-points : espace avant en français
    P = phrases(f)                                                            # phrases simples de chaque partie
    secteur = T[f"secteur_{f['secteur']}"] + (f" ({T['sous_' + f['sous_secteur']]})" if f["groupe"] == "FIN" else "")
    # En-tête
    st.header(f"{f['nom']}")
    st.caption(f"**{f['symbole']}** · {bourse or f['bourse']} · {secteur} · {md(dollars(f['capitalisation_usd'], L))} · "
               f"{T['membre'] if f['membre'] else T['hors_indice']}")
    if f["garde_fou"]["exclue"]:                                              # bandeau « exclue », raisons dans Santé
        st.markdown(f'<div style="border:2px solid {VIOLET};border-radius:8px;padding:8px 14px;margin:4px 0 10px">'
                    f'<b>{T["av_exclue"]}</b></div>', unsafe_allow_html=True)
    # Note
    n = f["note"]
    if n["sur_100"] is None:
        st.info(T["pas_de_note"])
    else:
        st.markdown(f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">'
                    f'<div>{etoiles_html(n["etoiles"])}</div>'
                    f'<div style="font-size:2.4rem;font-weight:700;line-height:1">{nombre(n["sur_100"], L, 0)}'
                    f'<span style="font-size:1.1rem;font-weight:400;opacity:.7"> / 100</span></div></div>',
                    unsafe_allow_html=True)
        st.markdown(texte_phrases(P["note"], T, L))
        for a in f["avertissements"]:
            if a in ("partielle", "cotee_recente"):
                st.info(T["av_" + a])
        with st.expander(T["detail_note"]):
            detail_note(f, T, L, dp)
    # Les quatre parties
    st.subheader(T["composantes"])
    for c in f["composantes"]:
        g1, g2 = st.columns([1, 3])
        g1.markdown(f"**{T[c['nom']]}**")
        if c["note"] is None:
            g2.caption(T["donnees_insuffisantes"])
        else:
            g2.progress(c["note"] / 100, text=f"{nombre(c['note'], L, 0)} / 100")
        st.markdown(texte_phrases(P[c["code"]], T, L))
        with st.expander(T["detail_chiffre"]):
            detail_composante(f, c, T, L, dp)
    # Santé financière
    S = P["sante"]
    st.subheader(T["garde_fou"])
    st.markdown(badge(T["statut_" + S["statut"]], STATUTS[S["statut"]]), unsafe_allow_html=True)
    titres = [md(rendre(p, T, L)) for p in S["phrases"] if p["titre"]]
    points = [md(rendre(p, T, L)) for p in S["phrases"] if not p["titre"]]
    st.markdown("  \n".join(f"**{t}**" for t in titres) + "".join(f"\n- {p}" for p in points))
    with st.expander(T["detail_chiffre"]):
        detail_sante(f, T, L, dp)


# --- Page -----------------------------------------------------------------------------------------------------------
T = textes()
L = st.session_state.get("langue", "fr")
st.title(T["titre"])
st.caption(T["sous_titre"])
texte = st.text_input(T["champ_recherche"], placeholder=T["exemple_recherche"])
if texte.strip():
    try:
        props = propositions(texte.strip())
    except DonneesIndisponibles:
        st.info(T["erreur_donnees"])
        st.stop()
    if not props:
        st.info(T["aucun_resultat"])
        st.stop()
    libelles = [f"{p['nom']} · {p['symbole']} · {p['bourse']} · {p['devise'] or '?'}"
                + (f" ({T['cotation_principale']})" if p["principale"] else "") for p in props]
    i = st.selectbox(T["choisir_cotation"], range(len(props)), format_func=lambda k: libelles[k])
    with st.spinner(T["attente"]):
        try:
            fiche = calculer_fiche(props[i]["symbole"], (SITE / "reference" / "reference.parquet").stat().st_mtime)
        except DonneesIndisponibles:
            st.info(T["erreur_donnees"])
            st.stop()
    if fiche.get("erreur") == "classement":
        st.info(T["erreur_classement"])
    else:
        afficher_fiche(fiche, T, L, props[i]["bourse"])
