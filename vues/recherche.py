"""Page principale : recherche d'une société, puis fiche de sa note (cahier des charges §3 et §4)."""
import pandas as pd                    # dates et tableaux
import plotly.graph_objects as go      # jauge de la note
import streamlit as st                 # interface web

from notabourse.calcul import charger_reference, noter_hors_indice, ratios_et_croissances
from notabourse.classement import charger_correspondance_yahoo
from notabourse.constantes import ECHELLE_ETOILES, SEUILS_GARDE_FOU, SEUILS_VIGILANCE
from notabourse.fiche import fiche_hors_indice, fiche_membre
from notabourse.phrases import couleur_affichage, couleur_moyenne_affichage, phrases, rendre
from notabourse.sources import DonneesIndisponibles, cotations, table_cik_sec
from vues.commun import SITE, date, dollars, nombre, pct, textes

BLEU = "#5B8DEF"                                                              # couleur des barres, jauge, étoiles
COULEURS = {"vert": "#2E9E5B", "orange": "#E8912D", "rouge": "#D64545", None: "#4A4F5C"}   # réservées au garde-fou
VIOLET = "#8E7CC3"                                                            # bandeau « exclue » (pas une couleur du garde-fou)
STATUTS = {"bonne": COULEURS["vert"], "vigilance": COULEURS["orange"],        # point de vigilance : orange [M] 19/10
           "exclue": VIOLET, "inconnue": COULEURS[None]}


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
    if fmt == "pct2":
        return pct(x, L, 2)
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
    """Menu dépliant de la note : le calcul étape par étape avec les chiffres de la société (S, moyenne et écart-type
    du groupe, M, centile, étoiles), puis le rang dans le S&P 500, les membres proches et les dates des données."""
    n, cp, k = f["note"], f["comparaison"], f["calcul"]
    st.markdown(f"**{T['calcul_etapes']}**")
    if not f["membre"]:
        st.caption(T["calc_note_hors_indice"])
    presentes = [c["note"] for c in f["composantes"] if c["note"] is not None]   # notes de partie calculables
    st.markdown(T["calc_note_1"].format(groupe=T["groupe_" + f["groupe"]], nb=k["nb_groupe"]))
    st.markdown(T["calc_note_2"].format(detail=" + ".join(nombre(x, L, 1) for x in presentes), k=len(presentes),
                                        S=nombre(k["S"], L, 1)))
    st.markdown(T["calc_note_3"].format(S=nombre(k["S"], L, 1), m=nombre(k["S_moyenne_groupe"], L, 1),
                                        e=nombre(k["S_ecart_type_groupe"], L, 1), M=nombre(n["M"], L, 2)))
    st.markdown(T["calc_note_4"].format(n=k["nb_membres_notes"], note=nombre(n["sur_100"], L, 0)))
    if n["regle"] == "affichage":
        st.caption(T["calc_note_regle_affichage"])
    st.markdown(T["calc_note_5"])
    st.table(pd.DataFrame([{T["col_etoiles_note"]: str(minimum), T["col_etoiles"]: nombre(nb, L, 1)}
                           for minimum, nb in ECHELLE_ETOILES]))
    if cp:
        st.markdown(f"**{T['comparaison']}**  \n" + T["rang"].format(rang=cp["rang"], nb=cp["nb"]) + "  \n" +
                    T["moyenne_secteur_note"].format(x=nombre(cp["moyenne_secteur"], L, 0), n=cp["nb_secteur"]))
        st.markdown(f"**{T['proches']}**")
        st.table(pd.DataFrame([{"": p["symbole"], T["col_societe"]: p["nom"], T["note_sur_100"]: nombre(p["note"], L, 0)}
                               for p in cp["proches"]]))
    st.caption(T["dates_donnees"].format(exercice=date(f["dates"]["exercice"], L), cours=date(f["dates"]["cours"], L),
                                         reference=date(f["dates"]["reference"], L)))


def etapes_composante(f, c, T, L):
    """Texte « le calcul, étape par étape » d'une partie, avec les chiffres de la société."""
    note = "-" if c["note"] is None else nombre(c["note"], L, 0)
    secteur = T[f"secteur_{f['secteur']}"] if f["groupe"] != "FIN" else T["sous_" + f["sous_secteur"]]
    k = f["calcul"]
    if c["code"] == "Q1":
        v = c["detail"][0]["valeur"]
        cle = "calc_rent_fin" if f["groupe"] == "FIN" else "calc_rent_nf"
        return T[cle].format(v=pct(v, L, 1), secteur=secteur, note=note)
    if c["code"] == "G1":
        serie = lambda col: T["serie_" + col.split("_", 1)[1]]                # PERS_CA -> « ventes »
        pers = ", ".join(f"{serie(col)} {nombre(x, L, 2)}" for col, x in k["PERS"].items()) + " " + T["calc_pers_suffixe"]
        gs = ", ".join(f"{serie(col)} {pct(x, L, 0)}" for col, x in k["GS"].items()) + " " + T["calc_gs_suffixe"]
        return T["calc_croiss"].format(pers=pers, gs=gs, note=note)
    if c["code"] == "R2":
        return T["calc_bilan_" + f["groupe"]].format(note=note)
    m = k["M1"]                                                               # dynamique
    if m["brut"] is None:
        return T["calc_dyn_manquant"]
    etape4 = (T["calc_dyn_pos"].format(brut=nombre(m["brut"], L, 2)) if m["moyenne"] > 0 else
              T["calc_dyn_neg"].format(s=pct(m["s_med"], L, 2), brut=nombre(m["brut"], L, 2)))
    return T["calc_dyn"].format(moy=pct(m["moyenne"], L, 2), n=int(m["n"]), e=pct(m["ecart_type"], L, 2),
                                etape4=etape4, note=note)


def detail_composante(f, c, T, L, dp):
    """Menu dépliant d'une partie : ce qu'elle mesure, le calcul étape par étape, puis ses chiffres."""
    cle = f"phrase_{c['nom']}_fin" if f["groupe"] == "FIN" and c["nom"] in ("rentabilite", "bilan") else f"phrase_{c['nom']}"
    st.markdown(f"**{T['ce_que_mesure']}**{dp}" + T[cle] + (f" ({T['historique_court']})" if c["code"] == "G1" else ""))
    st.markdown(f"**{T['calcul_etapes']}**")
    st.markdown(md(etapes_composante(f, c, T, L)))
    st.markdown(f"**{T['chiffres_societe']}**")
    if c["code"] == "G1":
        if not c["croissances"]:
            st.write(T["donnees_insuffisantes"])
        for serie, taux in c["croissances"].items():
            st.markdown(f"**{T[serie]}** ({T['annees']}){dp}" + " ; ".join(pct(x, L) for x in taux))
    else:
        st.table(pd.DataFrame([{T["col_ratio"]: T[d["ratio"]], T["col_valeur"]: valeur_ratio(d["valeur"], d["format"], L),
                                T["col_moyenne_secteur"]: valeur_ratio(d["moyenne_secteur"], d["format"], L),
                                T["col_centile"]: nombre(d["centile"], L, 0)} for d in c["detail"]]))
        if any(d.get("en_ecart") for d in c["detail"]):
            st.caption(T["note_rang_ecart"])                                  # rang sur l'écart au secteur, comme la note


def seuils_voyant(nom, T, L):
    """Seuils affichés d'un voyant : (vert de la formule, rouge de la formule, orange du site), tirés des constantes."""
    vert, rouge = SEUILS_GARDE_FOU[nom]                                       # seuils de la formule (inchangés)
    if nom == "trésorerie":
        ans = lambda x: T["unite_an" if x == 1 else "unite_ans"].format(x=nombre(x, L, 0))
        return (T["ou_plus"].format(x=ans(vert)) + T["ou_flux_positif"], T["ou_moins"].format(x=ans(rouge)),
                T["flux_negatif"])
    if nom == "endettement":
        return (T["ou_moins"].format(x=pct(vert, L, 0)), T["ou_plus"].format(x=pct(rouge, L, 0)),
                T["ou_plus"].format(x=pct(SEUILS_VIGILANCE[nom], L, 0)))
    if nom == "intérêts":
        fois = lambda x: T["unite_fois"].format(x=nombre(x, L, 0))
        return (T["ou_plus"].format(x=fois(vert)), T["ou_moins"].format(x=fois(rouge)),
                T["moins_de"].format(x=fois(SEUILS_VIGILANCE[nom])))
    return (T["ou_plus"].format(x=pct(vert, L, 0)), T["ou_moins"].format(x=pct(rouge, L, 0)),   # fonds propres / actif
            T["moins_de"].format(x=pct(SEUILS_VIGILANCE[nom], L, 0)))


def detail_sante(f, T, L, dp):
    """Menu dépliant de la santé financière : voyants (couleurs du site), calcul étape par étape, seuils, conditions."""
    gf = f["garde_fou"]
    cols = st.columns(len(gf["voyants"]) + 1)
    for col, v in zip(cols, gf["voyants"]):
        note = "" if v["note"] is None else f" · {nombre(v['note'], L, 2)}"
        col.markdown(pastille(f"<b>{T['voyant_' + v['voyant']]}</b>{note}<br><small>{mesure_voyant(v, T, L)}</small>",
                              couleur_affichage(v)), unsafe_allow_html=True)
    moy = "-" if gf["moyenne"] is None else nombre(gf["moyenne"], L, 2)
    cols[-1].markdown(pastille(f"<b>{T['moyenne_voyants']}</b><br>{moy}", couleur_moyenne_affichage(f)),
                      unsafe_allow_html=True)
    st.markdown(f"**{T['calcul_etapes']}**")
    st.markdown(T["calc_sante_1"])
    lignes = []
    for v in gf["voyants"]:
        vert, rouge, orange = seuils_voyant(v["voyant"], T, L)
        lignes.append({T["col_voyant"]: T["voyant_" + v["voyant"]], T["col_mesure"]: T["mesure_nom_" + v["voyant"]],
                       T["col_vert"]: vert, T["col_rouge"]: rouge, T["col_orange_site"]: orange})
    st.table(pd.DataFrame(lignes))
    st.markdown(T["calc_sante_2"].format(moy=moy))
    st.markdown(T["calc_sante_3"])
    for cnd in gf["conditions"]:
        etat = T["remplie"] if cnd["remplie"] else (T["donnee_manquante"] if cnd.get("donnee_manquante") else T["non_remplie"])
        st.markdown(f"- {T['cond_' + cnd['condition']]}{dp}**{etat}**")
    st.markdown(T["calc_sante_4"])
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
        c1, c2 = st.columns([1, 1.2], vertical_alignment="center")          # étoiles | jauge en demi-cercle [M]
        c1.markdown(etoiles_html(n["etoiles"]), unsafe_allow_html=True)
        c1.caption(f"{nombre(n['etoiles'], L, 1)} / 5 · {T['note_m']}{dp}{nombre(n['M'], L, 2)}", help=T["aide_note_m"])
        c2.plotly_chart(jauge(n["sur_100"]), width="stretch", config={"displayModeBar": False})
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
