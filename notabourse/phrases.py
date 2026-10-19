"""Phrases simples de la fiche, pour un visiteur qui ne connaît rien à la Bourse. AFFICHAGE SEULEMENT : rien ici ne
change la note ni l'exclusion [M] 19/10/2026.

Demande de Mathys : sous chaque partie de la fiche, une petite phrase sans vocabulaire compliqué qui dit si c'est bien
ou pas, choisie selon la valeur de chaque ratio de la partie (une quinzaine de phrases possibles par partie), et qui
cite le point fort ou le point faible en cause. Les détails chiffrés restent dans les menus dépliants.

Chaque phrase est un dictionnaire :
  cle     : nom du texte dans traductions/fr.json et en.json ;
  titre   : vrai pour la phrase principale (affichée en gras) ;
  valeurs : ce qu'on insère dans le texte, {nom: (valeur, format)} ; formats : voir _formater().
Seuils des phrases : proposés par Claude [P], à valider avec la maquette ; seuils du « point de vigilance » : choisis
par Mathys (constantes.SEUILS_VIGILANCE).
"""
from notabourse.constantes import SEUILS_VIGILANCE
from notabourse.formats import dollars, manquant, nombre, pct, pct_signe

# --- Seuils des phrases [P] --------------------------------------------------------------------------------------------
NIVEAUX = [(80, 5), (60, 4), (40, 3), (20, 2), (0, 1)]       # note d'une partie (sur 100) -> niveau 5 (très bon) à 1
NIVEAUX_NOTE = [(90, 6), (75, 5), (60, 4), (40, 3), (25, 2), (0, 1)]   # note globale -> niveau 6 à 1
FORT, FAIBLE = 70, 30            # un ratio est un point fort s'il bat 70 % de son groupe, un point faible sous 30 %
ROE_EXCEPTIONNEL = 0.40          # rentabilité des fonds propres d'au moins 40 % par an
ROE_FONDS_PROPRES_FAIBLES = 1.0  # au-delà de 100 %, les fonds propres sont plus petits que le bénéfice d'une année
CROISSANCE_FORTE = 0.15          # croissance moyenne d'au moins 15 % par an
CROISSANCE_NETTE = 0.05          # croissance moyenne d'au moins 5 % par an (sinon « lente »)
AVANCE_NETTE = 0.001             # écart moyen au S&P 500 (mesure de la note) : net au-delà de 0,1 % par semaine
NOTE_DYNAMIQUE_FORTE = 75        # en avance et note de la dynamique d'au moins 75 : « nettement battu »
NOTE_DYNAMIQUE_FAIBLE = 25       # en retard et note de la dynamique sous 25 : « nettement décroché »
TAUX_BORNE = 1.0                 # croissance affichée bornée à +-100 % (au-delà : « > +100 % »)
NB_POINTS_FORTS = 2              # santé financière : au plus 2 phrases rassurantes
PEU_DE_DETTES = 0.20             # dettes < 20 % de (dettes + capitalisation) : « très peu de dettes »
INTERETS_LARGES = 10.0           # résultat d'au moins 10 fois les intérêts : intérêts « largement couverts »
FONDS_PROPRES_ELEVES = 0.10      # financières : fonds propres d'au moins 10 % de l'actif
DN_EBITDA_PIRE = 1e5             # dette nette / EBITDA au-delà : EBITDA négatif (la recherche met 1 000 000)

# Séries de croissance de chaque groupe : (ventes ou revenus, résultat) ; les financières n'ont que leurs revenus
SERIES = {"NF": ("GS_CA", "GS_EBITDA"), "REIT": ("GS_CA", "PERS_FFOPA"), "FIN": ("GS_REV_FIN", None)}


def _p(cle, titre=False, **valeurs):
    """Une phrase : clé du texte, phrase principale ou non, valeurs à insérer."""
    return {"cle": cle, "titre": titre, "valeurs": valeurs}


def _niveau(note, echelle=NIVEAUX):
    """Niveau d'une note sur 100 d'après une échelle [(minimum, niveau), ...] rangée du plus haut au plus bas."""
    for minimum, niveau in echelle:
        if note >= minimum:
            return niveau
    return echelle[-1][1]


def _mediane(valeurs):
    """Valeur du milieu d'une liste de nombres (None si vide) : une année hors norme (résultat passé d'une perte à un
    bénéfice, taux de +900 %) ne fausse pas la croissance « typique »."""
    if not valeurs:
        return None
    v, k = sorted(valeurs), len(valeurs) // 2                                 # rangés ; position du milieu
    return v[k] if len(v) % 2 else (v[k - 1] + v[k]) / 2                      # nombre impair : le milieu ; pair : moyenne des deux


# --- 1. Note globale ---------------------------------------------------------------------------------------------------
def phrases_note(f):
    """Niveau de la note, part des membres du S&P 500 battus, point fort et point faible parmi les 4 parties."""
    n = f["note"]["sur_100"]
    if n is None:
        return [_p("note_aucune", True)]
    sortie = [_p(f"note_{_niveau(n, NIVEAUX_NOTE)}", True), _p("note_centile", x=(n / 100, "pct0"))]
    parties = [(c["note"], c["nom"]) for c in f["composantes"] if c["note"] is not None]   # (note, nom) calculables
    if len(parties) >= 2:
        meilleure, pire = max(parties), min(parties)                          # partie la mieux et la moins bien notée
        fort = meilleure[1] if meilleure[0] >= FORT else None
        faible = pire[1] if pire[0] <= FAIBLE else None
        if fort and faible:
            sortie.append(_p("note_fort_faible", fort=("nom_" + fort, "cle"), faible=("nom_" + faible, "cle")))
        elif fort:
            sortie.append(_p("note_fort", fort=("nom_" + fort, "cle")))
        elif faible:
            sortie.append(_p("note_faible", faible=("nom_" + faible, "cle")))
        else:
            sortie.append(_p("note_equilibree"))                              # ni point fort ni point faible marqué
    return sortie


# --- 2. Rentabilité ----------------------------------------------------------------------------------------------------
def phrases_rentabilite(f, c):
    """Rentabilité des fonds propres (financières : de l'actif), comparée au secteur, en part de l'argent gagnée par an."""
    fin = f["groupe"] == "FIN"
    d = c["detail"][0]                                                        # le seul ratio de la partie
    v, m, q = d["valeur"], d["mediane_secteur"], c["note"]                    # médiane : la moyenne est faussée
                                                                              # par quelques fonds propres minuscules
    if manquant(v) or q is None:
        return [_p("rent_inconnue", True)]
    if v < 0:
        tete = "rent_perte"                                                   # perte sur 12 mois
    elif not fin and v >= ROE_EXCEPTIONNEL and q >= 60:
        tete = "rent_exceptionnelle"
    else:
        tete = f"rent_{_niveau(q)}"                                           # comparée au secteur
    fmt = "pct1" if fin else "pct0"                                           # financières : une décimale (1,4 %)
    sortie = [_p(tete, True)]
    if v < 0:
        sortie.append(_p("rent_chiffre_perte_fin" if fin else "rent_chiffre_perte", x=(-v, fmt)))
    else:
        sortie.append(_p("rent_chiffre_fin" if fin else "rent_chiffre", x=(v, fmt)))
    if not manquant(m):
        sortie.append(_p("rent_moyenne_secteur", m=(m, fmt)))
    if not fin and v >= ROE_FONDS_PROPRES_FAIBLES:
        sortie.append(_p("rent_fonds_propres_faibles"))                       # ROE gonflé par des fonds propres réduits
    return sortie


# --- 3. Croissance -----------------------------------------------------------------------------------------------------
def phrases_croissance(f, c):
    """Croissance annuelle des ventes et du résultat : tendance, régularité, comparaison, chiffres moyens."""
    groupe, q = f["groupe"], c["note"]
    nom_ventes, nom_resultat = SERIES[groupe]
    ventes = [x for x in c["croissances"].get(nom_ventes, []) if not manquant(x)]       # du plus récent au plus ancien
    resultat = [x for x in c["croissances"].get(nom_resultat, []) if not manquant(x)] if nom_resultat else []
    if q is None or not (ventes or resultat):
        return [_p("croiss_inconnue", True)]
    vm, rm = _mediane(ventes), _mediane(resultat)                             # croissance typique par an
    toutes = ventes + resultat
    baisses = sum(x < 0 for x in toutes)                                      # années de baisse
    recente = any(s and s[0] < 0 for s in (ventes, resultat))                 # baisse sur le dernier exercice
    if (vm is None or vm < 0) and (rm is None or rm < 0):
        tete = "croiss_recul_fin" if groupe == "FIN" else "croiss_recul"
    elif vm is not None and rm is not None and vm >= 0 > rm:
        tete = "croiss_marges"                                                # ventes en hausse, résultat en baisse
    elif vm is not None and rm is not None and vm < 0 <= rm:
        tete = "croiss_redressement"                                          # ventes en baisse, résultat en hausse
    elif baisses == 0:
        typique = _mediane(toutes)
        tete = ("croiss_forte" if typique >= CROISSANCE_FORTE else
                "croiss_reguliere" if typique >= CROISSANCE_NETTE else "croiss_lente")
    elif recente:
        tete = "croiss_baisse_recente"
    else:
        tete = "croiss_irreguliere"
    sortie = [_p(tete, True)]
    if q >= FORT:
        sortie.append(_p("croiss_mieux"))                                     # comparée aux membres du même groupe
    elif q <= FAIBLE:
        sortie.append(_p("croiss_moins"))
    n = (max(len(ventes), len(resultat)) + 1, "entier")                       # exercices comparés (3 taux = 4 exercices)
    if vm is not None and rm is not None:
        sortie.append(_p("croiss_chiffres_reit" if groupe == "REIT" else "croiss_chiffres",
                         v=(vm, "taux"), r=(rm, "taux"), n=n))
    elif vm is not None:
        sortie.append(_p("croiss_chiffres_fin" if groupe == "FIN" else "croiss_chiffres_ventes", v=(vm, "taux"), n=n))
    else:
        sortie.append(_p("croiss_chiffres_ffo" if groupe == "REIT" else "croiss_chiffres_resultat", r=(rm, "taux"), n=n))
    return sortie


# --- 4. Bilan ----------------------------------------------------------------------------------------------------------
def _chiffre_bilan(d):
    """Phrase chiffrée d'un ratio du bilan (celui qui explique le mieux la note)."""
    v, r = d["valeur"], d["ratio"]
    if r == "DN_EBITDA":
        if v >= DN_EBITDA_PIRE:
            return _p("bilan_chiffre_DN_EBITDA_negatif")                      # résultat négatif
        if v <= 0:
            return _p("bilan_chiffre_DN_EBITDA_tresorerie")                   # plus de trésorerie que de dettes
        return _p("bilan_chiffre_DN_EBITDA", x=(v, "nombre1"))
    fmt = "usd" if r == "TAILLE" else "pct0"
    return _p(f"bilan_chiffre_{r}", x=(v, fmt))


def phrases_bilan(f, c):
    """Niveau du bilan, points forts et points faibles parmi ses ratios, puis le chiffre du ratio le plus parlant."""
    q = c["note"]
    if q is None:
        return [_p("bilan_inconnu", True)]
    niveau = _niveau(q)
    ratios = [d for d in c["detail"] if not manquant(d["valeur"]) and d["centile"] is not None]
    forts = [d for d in ratios if d["centile"] >= FORT]                       # mieux que 70 % du groupe
    faibles = [d for d in ratios if d["centile"] <= FAIBLE]                   # moins bien que 70 % du groupe
    positif = niveau >= 3                                                     # bilan au moins « correct »
    if forts and faibles:
        modele = "bilan_pos_forts_faibles" if positif else "bilan_neg_faibles_forts"
    elif forts:
        modele = "bilan_pos_forts" if positif else "bilan_neg_forts"
    elif faibles:
        modele = "bilan_pos_faibles" if positif else "bilan_neg_faibles"
    else:
        modele = "bilan_seul"
    sortie = [_p(modele, True, tete=(f"bilan_tete_{niveau}", "cle"),
                 forts=([f"fort_{d['ratio']}" for d in forts], "liste"),
                 faibles=([f"faible_{d['ratio']}" for d in faibles], "liste"))]
    if faibles:                                                               # le point le plus faible, chiffré
        sortie.append(_chiffre_bilan(min(faibles, key=lambda d: d["centile"])))
    elif forts:                                                               # sinon le point le plus fort
        sortie.append(_chiffre_bilan(max(forts, key=lambda d: d["centile"])))
    return sortie


# --- 5. Dynamique ------------------------------------------------------------------------------------------------------
def phrases_dynamique(f, c):
    """Avance ou retard sur le S&P 500 en un an (sans le dernier mois), et régularité de cette avance.

    La mesure est celle de la note : écart hebdomadaire au S&P 500, hausses extrêmes neutralisées et chutes extrêmes
    plafonnées (fonction tente). Ce n'est pas la performance réelle de l'action : la phrase ne donne donc pas de
    pourcentage, seulement le sens (avance ou retard), sa force (note de la partie) et sa régularité."""
    detail = {d["ratio"]: d for d in c["detail"]}
    a, q = detail["ECART_HEBDO"]["valeur"], c["note"]
    if manquant(a) or q is None:
        return [_p("dyn_inconnue", True)]
    if a >= AVANCE_NETTE:                                                     # en avance
        niveau = 5 if q >= NOTE_DYNAMIQUE_FORTE else 4
    elif a > -AVANCE_NETTE:                                                   # à peu près comme le marché
        niveau = 3
    else:                                                                     # en retard
        niveau = 2 if q >= NOTE_DYNAMIQUE_FAIBLE else 1
    sens = "pos" if niveau >= 4 else ("neutre" if niveau == 3 else "neg")
    centile = detail["ECART_TYPE_HEBDO"]["centile"]                                    # haut = régulière (peu d'écarts)
    regularite = ("reg" if centile is not None and centile >= FORT else
                  "irr" if centile is not None and centile <= FAIBLE else "aucune")
    return [_p("dyn_modele", True, tete=(f"dyn_{niveau}", "cle"), suite=(f"dyn_suite_{sens}_{regularite}", "cle"))]


# --- 6. Santé financière (garde-fou et point de vigilance) -----------------------------------------------------------
def _vigilance_du_voyant(v):
    """Phrase de vigilance d'un voyant s'il franchit un seuil d'affichage de Mathys (SEUILS_VIGILANCE), sinon None."""
    m = v["mesure"] or {}
    if v["voyant"] == "endettement" and not manquant(m.get("tlmta")) and m["tlmta"] >= SEUILS_VIGILANCE["endettement"]:
        return _p("sante_dettes", x=(m["tlmta"], "pct0"))
    if v["voyant"] == "intérêts":
        if m.get("ebitda_negatif"):
            return _p("sante_interets_negatif")                               # résultat négatif avec des intérêts
        if not m.get("sans_interets") and not manquant(m.get("couverture")) and \
                m["couverture"] < SEUILS_VIGILANCE["intérêts"]:
            return _p("sante_interets", x=(m["couverture"], "nombre1"))
    if v["voyant"] == "trésorerie" and not m.get("flux_positif") and not manquant(m.get("annees")):
        return _p("sante_tresorerie", x=(m["annees"], "nombre1"))             # l'activité consomme de l'argent
    if v["voyant"] == "fonds propres / actif" and not manquant(m.get("ratio")) and \
            m["ratio"] < SEUILS_VIGILANCE["fonds propres / actif"]:
        return _p("sante_fonds_propres", x=(m["ratio"], "pct1"))
    return None


def _points_de_vigilance(f):
    """Points faibles de santé financière d'après les seuils d'affichage de Mathys (SEUILS_VIGILANCE)."""
    return [p for p in (_vigilance_du_voyant(v) for v in f["garde_fou"]["voyants"]) if p]


def couleur_affichage(v):
    """Couleur MONTRÉE d'un voyant (affichage seulement) [M] 19/10/2026 : la zone orange est élargie jusqu'aux seuils
    de vigilance pour prévenir plus tôt. Rouge = rouge de la formule ; orange = orange de la formule OU seuil de
    vigilance franchi ; vert sinon. La formule (et donc l'exclusion) garde ses propres couleurs."""
    if v["note"] is None:
        return None                                                           # voyant incalculable : gris
    if v["couleur"] == "rouge":
        return "rouge"
    if v["couleur"] == "orange" or _vigilance_du_voyant(v):
        return "orange"
    return "vert"


def couleur_moyenne_affichage(f):
    """Couleur MONTRÉE de la moyenne des voyants : celle de la formule si elle est orange ou rouge (exclusion) ;
    orange si un voyant est montré orange ou rouge ; vert sinon."""
    gf = f["garde_fou"]
    if gf["couleur"] in (None, "orange", "rouge"):
        return gf["couleur"]
    montrees = [couleur_affichage(v) for v in gf["voyants"]]
    return "orange" if any(c in ("orange", "rouge") for c in montrees) else "vert"


def _points_forts_sante(f):
    """Points rassurants (seulement quand il n'y a ni exclusion ni point de vigilance)."""
    sortie = []
    for v in f["garde_fou"]["voyants"]:
        m = v["mesure"] or {}
        if v["voyant"] == "endettement" and not manquant(m.get("tlmta")) and m["tlmta"] < PEU_DE_DETTES:
            sortie.append(_p("sante_peu_dettes", x=(m["tlmta"], "pct0")))
        elif v["voyant"] == "intérêts":
            if m.get("sans_interets"):
                sortie.append(_p("sante_sans_interets"))
            elif not manquant(m.get("couverture")) and m["couverture"] >= INTERETS_LARGES:
                sortie.append(_p("sante_interets_larges", x=(m["couverture"], "nombre0")))
        elif v["voyant"] == "trésorerie" and m.get("flux_positif"):
            sortie.append(_p("sante_flux_positif"))
        elif v["voyant"] == "fonds propres / actif" and not manquant(m.get("ratio")) and m["ratio"] >= FONDS_PROPRES_ELEVES:
            sortie.append(_p("sante_fonds_propres_eleves", x=(m["ratio"], "pct0")))
    return sortie


def sante(f):
    """Statut de santé financière (bonne, vigilance, exclue, inconnue) et ses phrases."""
    gf = f["garde_fou"]
    points = _points_de_vigilance(f)
    if gf["exclue"]:                                                          # exclusion de la formule : d'abord
        raisons = []
        for cnd in gf["conditions"]:
            if cnd["remplie"]:
                continue
            if cnd["condition"] == "benefices":
                raisons.append("sante_exclue_benefices_inconnus" if cnd.get("donnee_manquante") else "sante_exclue_benefices")
            else:
                raisons.append(f"sante_exclue_{cnd['condition']}")            # garde_fou ou fonds_propres
        return {"statut": "exclue", "phrases": [_p(r, True) for r in raisons] + points}
    if points:                                                                # gardée, mais un point faible
        titre = "sante_vigilance_1" if len(points) == 1 else "sante_vigilance_n"
        return {"statut": "vigilance", "phrases": [_p(titre, True)] + points}
    if all(v["note"] is None for v in gf["voyants"]):
        return {"statut": "inconnue", "phrases": [_p("sante_inconnue", True)]}
    titre = "sante_bonne_fin" if f["groupe"] == "FIN" else "sante_bonne"
    return {"statut": "bonne", "phrases": [_p(titre, True)] + _points_forts_sante(f)[:NB_POINTS_FORTS]}


# --- Ensemble de la fiche ----------------------------------------------------------------------------------------------
PAR_PARTIE = {"Q1": phrases_rentabilite, "G1": phrases_croissance, "R2": phrases_bilan, "M1": phrases_dynamique}


def phrases(f):
    """Toutes les phrases d'une fiche : note globale, chacune des 4 parties (par code), santé financière."""
    sortie = {"note": phrases_note(f), "sante": sante(f)}
    for c in f["composantes"]:
        sortie[c["code"]] = PAR_PARTIE[c["code"]](f, c)
    return sortie


# --- Texte final dans une langue ---------------------------------------------------------------------------------------
def _taux(x, langue_):
    """Taux de croissance avec son signe, borné à +-100 % : au-delà, le chiffre n'a plus de sens (base proche de zéro)."""
    if x > TAUX_BORNE:
        return "> " + pct_signe(TAUX_BORNE, langue_, 0)                       # « > +100 % »
    if x < -TAUX_BORNE:
        return "< " + pct_signe(-TAUX_BORNE, langue_, 0)                      # « < -100 % »
    return pct_signe(x, langue_, 1)


def _formater(valeur, fmt, T, langue_):
    """Une valeur insérée dans une phrase, mise en forme selon son format."""
    if fmt == "cle":
        return T[valeur]                                                      # un mot traduit
    if fmt == "liste":                                                        # « a, b et c » / « a, b and c »
        mots = [T[k] for k in valeur]
        if len(mots) <= 1:
            return "".join(mots)                                              # aucun mot ou un seul
        return ", ".join(mots[:-1]) + f" {T['et']} " + mots[-1]               # le dernier après « et »
    formats = {"pct0": lambda x: pct(x, langue_, 0), "pct1": lambda x: pct(x, langue_, 1),
               "pct_signe": lambda x: pct_signe(x, langue_, 1), "taux": lambda x: _taux(x, langue_),
               "nombre0": lambda x: nombre(x, langue_, 0),
               "nombre1": lambda x: nombre(x, langue_, 1), "entier": lambda x: str(int(x)),
               "usd": lambda x: dollars(x, langue_)}
    return formats[fmt](valeur)


def rendre(phrase, T, langue_):
    """Texte d'une phrase dans la langue choisie (T : dictionnaire des textes de cette langue)."""
    valeurs = {nom: _formater(v, fmt, T, langue_) for nom, (v, fmt) in phrase["valeurs"].items()}
    return T[phrase["cle"]].format(**valeurs)
