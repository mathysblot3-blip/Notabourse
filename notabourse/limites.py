"""Limite du nombre de calculs par visiteur (audit de sécurité du 19/10/2026) [P].

Chaque nouvelle société demande une dizaine de requêtes à Yahoo et à la SEC. Sans limite, un seul visiteur (ou un
programme) pourrait enchaîner des centaines de recherches : le site ralentirait pour tout le monde, Yahoo pourrait
bloquer le serveur, et le compteur Supabase se remplirait de lignes inutiles. Règle : au plus MAXIMUM nouvelles sociétés
par FENETRE secondes et par visite ; les sociétés déjà affichées pendant la visite ne comptent pas.
"""
import threading                 # verrou : plusieurs visiteurs peuvent compter en même temps
from collections import deque    # file des instants, du plus ancien au plus récent

MAXIMUM = 20        # nouvelles sociétés au plus...
FENETRE = 600       # ... par tranche de 10 minutes

# Plafonds GLOBAUX, tous visiteurs confondus (audit du 17/11/2026, constats S-C01 et S-C04) [P] : la limite par visite
# se remet à zéro quand on recharge la page ; ces compteurs-là sont partagés par tout le serveur et ne se remettent pas
# à zéro. Valeurs larges pour un usage normal, mais qui coupent un programme qui enchaînerait les demandes.
MAXIMUM_CALCULS_GLOBAL = 300     # nouvelles sociétés calculées par heure, pour tout le site
MAXIMUM_RECHERCHES_GLOBAL = 1500 # textes de recherche nouveaux envoyés à Yahoo par heure, pour tout le site
FENETRE_GLOBALE = 3600           # une heure
DUREE_ECHEC = 300                # une recherche qui vient d'échouer n'est pas relancée avant 5 minutes


def autoriser(horodatages, maintenant, maximum=MAXIMUM, fenetre=FENETRE):
    """horodatages : instants (en secondes) des nouveaux calculs de la visite. Renvoie (autorisé ?, liste à garder) :
    on oublie les calculs plus vieux que la fenêtre, puis on autorise s'il en reste moins que le maximum."""
    recents = [t for t in horodatages if maintenant - t < fenetre]           # calculs encore dans la fenêtre
    if len(recents) >= maximum:
        return False, recents                                                 # trop de calculs : refusé
    return True, recents + [maintenant]                                       # autorisé : on note ce calcul


class Compteur:
    """Compteur partagé par tous les visiteurs (un seul objet par serveur, gardé par st.cache_resource)."""

    def __init__(self, maximum, fenetre):
        self.maximum, self.fenetre = maximum, fenetre                         # plafond et durée de la fenêtre
        self.instants = deque()                                               # instants des demandes acceptées
        self.verrou = threading.Lock()                                        # une seule mise à jour à la fois

    def autoriser(self, maintenant):
        """Vrai (et la demande est comptée) s'il reste de la place dans la fenêtre ; faux sinon."""
        with self.verrou:
            while self.instants and maintenant - self.instants[0] >= self.fenetre:
                self.instants.popleft()                                       # on oublie les demandes trop anciennes
            if len(self.instants) >= self.maximum:
                return False                                                  # plafond atteint : refusé
            self.instants.append(maintenant)
            return True


class MemoireEchecs:
    """Retient les recherches qui viennent d'échouer, pour ne pas relancer Yahoo (et 25 s d'attente) à chaque saisie."""

    def __init__(self, duree=DUREE_ECHEC):
        self.duree, self.echecs, self.verrou = duree, {}, threading.Lock()

    def noter(self, texte, maintenant):
        """Retient l'échec de cette recherche à cet instant (la mémoire est bornée à 1 000 textes)."""
        with self.verrou:
            if len(self.echecs) >= 1000:
                self.echecs.clear()                                           # mémoire bornée : on repart de zéro
            self.echecs[texte] = maintenant

    def recent(self, texte, maintenant):
        """Vrai si cette recherche a échoué il y a moins de `duree` secondes."""
        with self.verrou:
            t = self.echecs.get(texte)
            return t is not None and maintenant - t < self.duree
