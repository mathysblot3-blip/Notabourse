"""Limite du nombre de calculs par visiteur (audit de sécurité du 19/10/2026) [P].

Chaque nouvelle société demande une dizaine de requêtes à Yahoo et à la SEC. Sans limite, un seul visiteur (ou un
programme) pourrait enchaîner des centaines de recherches : le site ralentirait pour tout le monde, Yahoo pourrait
bloquer le serveur, et le compteur Supabase se remplirait de lignes inutiles. Règle : au plus MAXIMUM nouvelles sociétés
par FENETRE secondes et par visite ; les sociétés déjà affichées pendant la visite ne comptent pas.
"""
MAXIMUM = 20        # nouvelles sociétés au plus...
FENETRE = 600       # ... par tranche de 10 minutes


def autoriser(horodatages, maintenant, maximum=MAXIMUM, fenetre=FENETRE):
    """horodatages : instants (en secondes) des nouveaux calculs de la visite. Renvoie (autorisé ?, liste à garder) :
    on oublie les calculs plus vieux que la fenêtre, puis on autorise s'il en reste moins que le maximum."""
    recents = [t for t in horodatages if maintenant - t < fenetre]           # calculs encore dans la fenêtre
    if len(recents) >= maximum:
        return False, recents                                                 # trop de calculs : refusé
    return True, recents + [maintenant]                                       # autorisé : on note ce calcul
