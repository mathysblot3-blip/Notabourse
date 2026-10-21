"""Constantes de la note NotaBourse : un seul endroit pour tous les seuils et paramètres.

Toutes les valeurs de la formule viennent de la recherche (formule C8) et ne doivent PAS être changées.
Nature de chaque valeur (voir CHOIX.md) : [R] reprise de la recherche (fichier cité), [M] avis de Mathys, [P] proposée.
"""
import pandas as pd  # tableaux de données (ici pour les durées)

# --- Poids de la note M (outils/note_m.py, POIDS_C7) [R] -------------------------------------------------------------
# Q1 = rentabilité, G1 = croissance, R2 = bilan et taille, M1 = dynamique (appelée D dans les documents).
# Les autres composantes de la formule d'origine ont un poids nul : elles ne comptent plus.
POIDS_C7 = {"Q1": 1, "Q2": 0, "V1": 0, "V2": 0, "G1": 1, "G2": 0, "R1": 0, "R2": 1, "M1": 1}
SOUS_SCORES = {"Q": ["Q1", "Q2"], "V": ["V1", "V2"], "G": ["G1", "G2"], "R": ["R1", "R2"], "M": ["M1"]}  # outils/score.py
COMPOSANTES = [k for liste in SOUS_SCORES.values() for k in liste]          # les 9 composantes, dans l'ordre
COMPOSANTES_C8 = ["Q1", "G1", "R2", "M1"]                                   # les 4 composantes qui comptent
MIN_COMPOSANTES = 7                                                         # outils/score.py (7 sur 9, moins les retirées)

# Noms affichés (jamais Q, G, R, D sur le site) [M] cahier des charges §4
NOMS_COMPOSANTES = {"Q1": "rentabilite", "G1": "croissance", "R2": "bilan", "M1": "dynamique"}

# --- Normalisation (conception_v2 §3) [R] ----------------------------------------------------------------------------
WINSOR_BAS, WINSOR_HAUT = 0.05, 0.95        # winsorisation aux 5e et 95e centiles (MSCI 2013 p. 4)
MIN_PAIRS_SECTEUR = 8                       # écart au secteur : au moins 8 autres valeurs, sinon le groupe

# --- Dynamique (outils/composantes.py) [R] ---------------------------------------------------------------------------
MIN_SEMAINES_M1 = 40                        # au moins 40 semaines dans la fenêtre
JOURS_FENETRE_DEBUT, JOURS_FENETRE_FIN = 251, 21   # semaines entre le 252e et le 22e jour de bourse avant la date
JOURS_COURS_RECENT = 10                     # dernier cours à plus de 10 jours de la veille : rien n'est calculé

# --- Régularité de la croissance (PERS, outils/composantes.py) [R] ---------------------------------------------------
POIDS_PERS = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}  # poids par bloc (LSV p. 12) : 5 pour le plus récent
PERS_BAS, PERS_HAUT = -0.30, 0.10            # bornes de la croissance corrigée, ramenée de -3 à +1
MOIS_RECENCE = 15                            # dernière période de moins de 15 mois
# Paramètres trimestriels de la recherche (servent au contrôle d'équivalence) [R]
PERS_TRIMESTRIEL = {"nb": 20, "minimum": 4, "jours_periode": 91.31, "taille_bloc": 4, "mois_fenetre": 20 * 3 + 6,
                    "frequence_civile": "Q", "decalage_civil_mois": 0}
# Version annuelle du site : 3 croissances sur 4 exercices, au moins 2, une année = un bloc [M] 19/10/2026
PERS_ANNUEL = {"nb": 3, "minimum": 2, "jours_periode": 365.25, "taille_bloc": 1, "mois_fenetre": 3 * 12 + 6,
               "frequence_civile": "Y", "decalage_civil_mois": 6}

# --- Croissance lissée (GS, outils/composantes.py gs_lsv) [R], version annuelle [M] ----------------------------------
GS_RECHERCHE = {"nb": 5, "minimum": 2}       # recherche : 5 exercices
GS_ANNUEL = {"nb": 3, "minimum": 2}          # site : 3 croissances (4 exercices), au moins 2 [M] 19/10/2026
NB_EXERCICES = 4                             # exercices lus chez Yahoo [M] 19/10/2026

# --- Garde-fou noté de -1 à +1 (outils/garde_fou.py, candidat_c8.md) [R] ----------------------------------------------
VERT, ROUGE = 1 / 3, -1 / 3                  # bords de l'orange
SEUILS_GARDE_FOU = {                         # (seuil vert, seuil rouge) de chaque voyant
    "trésorerie": (2.0, 1.0),                # années de trésorerie si le flux d'exploitation est négatif
    "endettement": (0.80, 0.90),             # TLMTA
    "intérêts": (2.0, 1.0),                  # EBITDA / intérêts
    "fonds propres / actif": (0.05, 0.04),   # financières seulement
}

# --- Règles de données (conception_v2 §2.2, §9) ----------------------------------------------------------------------
JOURS_COTATION_MIN = 365                     # coté depuis moins de 12 mois : non noté dans la recherche [R]
SEUIL_DETTE_NULLE = 0.005                    # dette = 0 si aucune dette publiée et intérêts < 0,5 % de l'actif [R]
DN_EBITDA_PIRE = 1e6                         # dette nette / EBITDA quand l'EBITDA est négatif : le pire [R]

# --- Calcul daté (test d'acceptation) [M] 19/10/2026 -----------------------------------------------------------------
DELAI_TRIMESTRE = pd.Timedelta(days=45)      # un trimestre (ou semestre) n'est connu que 45 jours après sa fin
DELAI_EXERCICE = pd.Timedelta(days=75)       # un exercice n'est connu que 75 jours après sa fin

# --- Échelle des demi-étoiles (cahier des charges §4) [M] ; borne basse incluse [P] ---------------------------------
ECHELLE_ETOILES = [(95, 5.0), (90, 4.5), (80, 4.0), (70, 3.5), (55, 3.0), (40, 2.5), (30, 2.0), (20, 1.5), (10, 1.0),
                   (0, 0.5)]             # (note minimale sur 100, nombre d'étoiles)

# --- « Point de vigilance » : AFFICHAGE SEULEMENT, ni la note ni l'exclusion ne changent [M] 19/10/2026 -------------
# Le garde-fou de la formule ne signale presque rien (493 membres sur 500 en vert) ; ces seuils plus stricts servent
# seulement à prévenir le visiteur d'un point faible (« seuils moyens » : 37 des 410 membres gardés signalés).
SEUILS_VIGILANCE = {
    "endettement": 0.60,                     # dettes / (dettes + capitalisation) à partir de 60 %
    "intérêts": 4.0,                         # EBITDA inférieur à 4 fois les intérêts
    "fonds propres / actif": 0.06,           # financières : fonds propres inférieurs à 6 % de l'actif
}                                            # trésorerie : tout flux d'exploitation négatif est signalé

# --- Prix comparé au secteur : indicateur À PART, hors de la note [M] 21/10/2026 -------------------------------------
# Repris de Recherche_score/36_per_secteur.py et indicateur_per_secteur.md [R]
PRIX_BON_MARCHE = 0.80                       # PER / PER du secteur <= 0,8 : bon marché (écart de -20 % ou moins)
PRIX_CHERE = 1.25                            # PER / PER du secteur >= 1,25 : chère (écart de +25 % ou plus) ; 1 / 0,8
PRIX_MIN_PAIRS = 5                           # au moins 5 membres bénéficiaires dans le secteur, sinon tout le groupe
PRIX_BORNE_BARRE = 2.0                       # barre : de « 2 fois plus cher » à « 2 fois moins cher » que le secteur [P]
PRIX_PER_MAX_REPLI = 100.0                   # repli sur un bénéfice ancien ou moyen : au-delà d'un PER de 100 (bénéfice
                                             # quasi nul), on passe au prix / ventes, plus parlant [P] 21/10/2026
