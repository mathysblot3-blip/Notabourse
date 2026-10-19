# Choix de conception du site NotaBourse

Statut : **provisoire, à valider par Mathys (étape a, 19/10/2026)**. Ce tableau est écrit **avant** tout calcul de note
et avant le test d'acceptation : il ne sera pas réglé sur le résultat de ce test. Une seule correction après le
contrôle à la main (résultat d'exploitation, ligne marquée), décidée par Mathys le 19/10/2026.

Nature de chaque choix : **[R]** repris tel quel de la recherche (fichier cité) ; **[M]** avis de Mathys (date) ;
**[P]** proposé par Claude, à valider ; **[T]** résultat de test.

## 1. Principe

| Choix | Nature |
|---|---|
| La formule C8 n'est pas modifiée : les fonctions de calcul sont copiées de la recherche à l'identique (`outils/composantes.py`, `outils/note_m.py`, `outils/garde_fou.py`, `outils/score.py`, `10_score.py` avec les options W1, V10, V9) | [M] 19/10/2026 |
| Seules adaptations : les données (Yahoo Finance au lieu de la SEC), la croissance annuelle, la règle d'affichage « note dès 2 composantes » | [M] 19/10/2026 |
| Un contrôle d'équivalence (dans le dépôt de recherche, `33_equivalence_site.py`) vérifie que le code du site redonne exactement les notes de recherche à partir des mêmes ratios | [P] |

## 2. Postes comptables : correspondance SEC → Yahoo

Ordre de repli de gauche à droite (« → ») ; « 0 si absent » reprend la règle de la recherche pour les postes d'événement
(conception_v2 §9). (flux) = tableau des flux de trésorerie, (résultat) = compte de résultat, (bilan) = bilan.

| Poste | Recherche (conception_v2 §2.3, `outils/panel.py`) | Yahoo | Écart connu |
|---|---|---|---|
| CA | Revenues et étiquettes voisines | Total Revenue → Operating Revenue (résultat) | Aucun attendu |
| Revenus des financières | Revenues, sinon produits d'intérêts + hors intérêts | Total Revenue → Operating Revenue | Yahoo donne en général le produit net bancaire |
| Bénéfice net part du groupe | NetIncomeLossAvailableToCommonStockholdersBasic → NetIncomeLoss | Net Income Common Stockholders → Net Income | Aucun attendu |
| Activités abandonnées | IncomeLossFromDiscontinuedOperations..., 0 si absent | Net Income Discontinuous Operations, 0 si absent | Aucun attendu |
| Résultat consolidé | ProfitLoss → NetIncomeLoss, moins activités abandonnées | Net Income Including Noncontrolling Interests → Net Income, moins activités abandonnées | Aucun attendu |
| Impôts différés | DeferredIncomeTaxExpenseBenefit, 0 si absent | Deferred Income Tax (flux), 0 si absent | Souvent absent hors États-Unis |
| E* (Gray-Vogel) | bénéfice part du groupe − abandonnées + impôts différés | même formule | Aucun |
| Plus-values de placements | GainLossOnInvestments..., signées comme un gain, 0 si absent | − Gain Loss On Investment Securities (flux : un gain y est négatif), 0 si absent | Signe à contrôler à la main |
| Plus-values de cession | GainLossOnDispositionOfAssets..., 0 si absent | − Gain Loss On Sale Of PPE (flux), 0 si absent | Idem |
| Dépréciations | AssetImpairmentCharges..., 0 si absent | Asset Impairment Charge (flux) → Impairment Of Capital Assets (résultat), 0 si absent | Idem |
| D&A | flux : DepreciationDepletionAndAmortization... ; jamais le droit d'utilisation | Depreciation And Amortization → Depreciation Amortization Depletion → Depreciation (flux) → Reconciled Depreciation (résultat) | Comptes IFRS : l'amortissement des droits d'utilisation (IFRS 16) est inclus et ne peut pas être retiré |
| Résultat d'exploitation ajusté | OperatingIncomeLoss − (plus-values de cession − dépréciations) | Operating Income (résultat déjà nettoyé des éléments exceptionnels par Yahoo), sans autre retraitement [M] 19/10/2026 | Contrôle à la main : retirer à nouveau les dépréciations les compterait deux fois (LVMH +720 M€) ; le « tel que publié » de Yahoo manque pour Airbus et TotalEnergies et contient les réévaluations d'immeubles d'Unibail |
| EBITDA | résultat d'exploitation ajusté + D&A ; D&A absent : manquant | même formule ; D&A absent : manquant | IFRS 16 (ligne D&A) |
| Intérêts | InterestExpense → InterestExpenseDebt → InterestAndDebtExpense ; repli intérêts payés | Interest Expense → Interest Expense Non Operating (résultat) ; repli Interest Paid Supplemental Data → valeur absolue de Interest Paid Cfo, Interest Paid Cff (flux) | Apple ne publie plus ses intérêts depuis 2024 : voyant incalculable, comme dans la recherche si l'étiquette manque |
| Flux d'exploitation | ...ContinuingOperations → NetCashProvidedByUsedInOperatingActivities | Cash Flow From Continuing Operating Activities → Operating Cash Flow | Aucun attendu |
| Actif | Assets | Total Assets | Aucun |
| Actif des financières | Assets − SeparateAccountAssets | Total Assets | Comptes séparés des assureurs vie non retirés (approximation) |
| Passif | Liabilities | Total Liabilities Net Minority Interest | Aucun attendu |
| Dettes de location simple | OperatingLeaseLiability, 0 si absent | Capital Lease Obligations (bilan), 0 si absent | Yahoo mêle locations simples et financières, et ne les donne pas toujours (Apple depuis 2024) |
| Passif ajusté | passif − dettes de location simple | même formule | Ligne précédente |
| Fonds propres | StockholdersEquity ; repli de l'exclusion : actif − passif − minoritaires | Stockholders Equity ; même repli avec Minority Interest | Aucun attendu |
| Trésorerie | CashCashEquivalentsAndShortTermInvestments, sinon trésorerie + placements à court terme | Cash Cash Equivalents And Short Term Investments → Cash And Cash Equivalents + Other Short Term Investments | Aucun attendu |
| Dette (foncières) | court + long terme + crédit-bail ; dette nulle si aucune étiquette et intérêts < 0,5 % de l'actif | Total Debt − Capital Lease Obligations ; Total Debt absent et intérêts < 0,5 % de l'actif : 0 | Idem location |
| Goodwill et incorporels (banques) | Goodwill, IntangibleAssetsNetExcludingGoodwill | Goodwill, Other Intangible Assets (repli : Goodwill And Other Intangible Assets), 0 si absent | Aucun attendu |
| Moins-value latente des titres détenus jusqu'à l'échéance (banques) | juste valeur − coût amorti ; 0 si absent | indisponible chez Yahoo : 0 | La recherche faisait de même quand le poste manquait |
| Gains latents (AOCI, financières hors banques) | AccumulatedOtherComprehensiveIncome..., 0 si absent | Gains Losses Not Affecting Retained Earnings, 0 si absent | Aucun attendu |
| Actions diluées (FFO par action) | WeightedAverageNumberOfDilutedSharesOutstanding | Diluted Average Shares (résultat) | Aucun attendu |
| Capitalisation | actions × cours non ajusté de la veille | marketCap de Yahoo converti en dollars ; calcul daté : × cours de la veille de la date / cours du jour (P4) | Actions supposées constantes entre la date et aujourd'hui (calcul daté seulement) |
| Cours | clôtures ajustées des dividendes et divisions | `history(auto_adjust=True)`, converties en dollars jour par jour | Effet de change inclus pour les actions hors dollar [M] |
| Marché | S&P 500 dividendes réinvestis | ^SP500TR | Aucun |

## 3. Ratios (définitions de la recherche, inchangées)

| Ratio | Définition | Source |
|---|---|---|
| ROE | bénéfice part du groupe TTM / fonds propres ; manquant si fonds propres ≤ 0 | [R] `12_variantes.py` |
| ROA des financières | (E* − plus-values de placements) TTM / actif des financières | [R] `09_composantes.py` |
| TLMTA | passif ajusté / (passif ajusté + capitalisation) | [R] `09_composantes.py` |
| CASHMTA | trésorerie / (passif ajusté + capitalisation) | [R] |
| Taille | capitalisation (dollars) | [R] |
| Dette nette / EBITDA (foncières) | (dette − trésorerie) / EBITDA TTM ; EBITDA ≤ 0 : 10⁶ (le pire) ; manquant si un poste manque | [R] |
| Fonds propres / actif (financières) | banques : (fonds propres − goodwill − incorporels + moins-value latente) / actif ; autres : (fonds propres − AOCI) / actif | [R] |
| FFO par action (foncières) | (résultat consolidé + D&A − plus-values de cession − plus-values de placements + dépréciations) / actions diluées | [R] `09_composantes.py` |
| Banques, assurances, autres | SIC 6000-6199, 6300-6399, reste des financières | [R] `09_composantes.py` |

## 4. Périodes

| Choix | Nature |
|---|---|
| TTM (12 derniers mois) d'un poste : somme des 4 derniers trimestres s'ils se suivent, s'ils contiennent ce poste et si le dernier est postérieur au dernier exercice ; sinon le dernier exercice (comme la recherche quand aucun 10-Q ne suit le 10-K). Les sociétés qui publient par semestre (LVMH, Nestlé, Unibail) n'ont pas de trimestres chez Yahoo : TTM = dernier exercice | [P] (la recherche : exercice + cumul de l'exercice en cours − cumul de l'an passé, équivalent) |
| Plus de 15 mois depuis la fin de la dernière période : poste manquant | [R] conception_v2 §2.2 |
| Bilan : le plus récent **complet** (actif, dettes et fonds propres présents), trimestriel, semestriel ou annuel ; si aucun n'est complet, le plus récent. Tous les postes viennent de la même date | [R] « dernier bilan déposé », adapté [M] 19/10/2026 : au premier passage du robot, Yahoo a renvoyé pour 21 membres un bilan de juin à moitié rempli (7 notes déplacées de plus de 5 points, Gartner 42 → 10) |
| Exercices : les 4 plus récents où la série existe | [M] 19/10/2026 (4 exercices) |
| Calcul daté (test d'acceptation) : cours jusqu'à la veille de la date ; une période n'est retenue que si son rapport (10-Q, 10-K...) a été déposé à la SEC avant la date, d'après l'index des dépôts (métadonnées seulement) ; sans dépôt SEC : trimestres clos au moins 45 jours avant, exercices au moins 75 jours avant | [M] 19/10/2026 |

## 5. Dollars

| Choix | Nature |
|---|---|
| Montants des comptes (devise `financialCurrency`) convertis en dollars au cours de change de la date ; les ratios d'une même devise n'en dépendent pas | [M] (montants en dollars), cours de la date [P] |
| Cours en pence (GBp), cents sud-africains (ZAc) et agorot (ILA) divisés par 100 avant conversion | [P] |
| Croissances calculées dans la devise des comptes (aucun effet de change) | [P] |

## 6. Groupes et secteurs

| Choix | Nature |
|---|---|
| Code SIC de la SEC (data.sec.gov) quand la société y dépose ; groupes et secteurs Fama-French par les fonctions de recherche `groupe_de`, `secteur_de` | [M] 19/10/2026 ; [R] `08_panel_point_in_time.py` |
| Sinon : table « industrie Yahoo → groupe, secteur, sous-secteur » construite sur les membres du S&P 500 (étape b) | [M] 19/10/2026 |

## 7. Croissance annuelle (composante Croissance)

| Choix | Nature |
|---|---|
| Régularité : calcul PERS de la recherche sur des croissances annuelles (taux symétrique, moins la médiane du groupe pour la même année, année = fin d'exercice − 6 mois, borné de −3 à +1), poids 5, 4, 3, au moins 2 croissances, dernier exercice de moins de 15 mois | [M] 19/10/2026 |
| Niveau : calcul GS de la recherche (centile de la croissance, poids 6 − j), limité aux 3 dernières croissances, au moins 2 | [M] 19/10/2026 |
| Assemblage inchangé : industrie CA + EBITDA ; foncières CA + FFO par action (régularité), CA + EBITDA (niveau) ; financières revenus | [R] `10_score.py` |
| Société hors indice : ses croissances sont traitées comme si elle était ajoutée au groupe des membres (médianes, centiles, voisins des bases négatives), sans changer les valeurs des membres, comme dans le contrôle « un de côté » de la recherche | [P] |

## 8. Affichage

| Choix | Nature |
|---|---|
| Note globale dès 2 composantes, dynamique comprise ou non, avertissement « note peu fiable : données manquantes » | [M] cahier des charges |
| Société cotée depuis moins de 12 mois : même règle (note dès 2 composantes) | [M] 19/10/2026 |
| Membre du S&P 500 : note de la référence hebdomadaire ; autre société : comparée aux membres | [M] 19/10/2026 |
| Étoiles d'après la note arrondie affichée, borne basse incluse | [P] (P5) |

## 9. Contrôle à la main (étape a, 19/10/2026)

| Société | Contrôle | Résultat |
|---|---|---|
| Apple | Ratios Yahoo datés au 31/08/2026 face aux ratios SEC de la recherche | Identiques à 0,1 % près (ROE, endettement, trésorerie, EBITDA, flux d'exploitation, dynamique) |
| JPMorgan | Idem | Identiques, sauf fonds propres / actif (6,2 % contre 7,5 %) : la recherche n'avait pas retiré le goodwill de JPMorgan (poste combiné à la SEC) ; le site suit la définition |
| LVMH | Données Yahoo face au communiqué annuel 2025 de LVMH (27/01/2026) | Ventes 80 807 M€ et résultat net part du groupe 10 878 M€ identiques ; dette − trésorerie 6 842 M€ contre une dette financière nette publiée de 6 857 M€ |
| Petite valeur | Claranova (ALCLA.PA), choisie par Mathys le 19/10/2026 | Exercice 2025 vide chez Yahoo : rentabilité et TTM manquants, cas « données insuffisantes » |

Détail des comparaisons avec la recherche : dépôt de recherche, `resultats/controle_main_site.md` (non publié : il contient
des ratios de recherche).

## 10. Référence S&P 500 (étape b, 19/10/2026)

| Choix | Nature |
|---|---|
| Membres : page Wikipédia « List of S&P 500 companies » (symbole, CIK) | [M] cahier des charges |
| Une ligne par société (CIK) ; pour les sociétés à plusieurs catégories d'actions, la première listée par Wikipédia (catégorie A : GOOGL, FOXA, NWSA) ; les autres catégories (GOOG, FOX, NWS) renvoient vers elle | [R] conception_v2 §2.1 (une ligne par CIK) ; mêmes catégories que la recherche au 31/08/2026 [T] |
| Membres notés entre eux avec le calcul de la recherche ; affichage dès 2 composantes pour ceux que la recherche ne note pas (4 scissions récentes au 19/10/2026) | [R] et [M] |
| Fichiers publics : ratios, taux de croissance, notes et voyants seulement, aucun montant de comptes | [M] 19/10/2026 |
| Échecs de téléchargement : valeurs de la semaine précédente (2 semaines au plus), arrêt si plus de 10 % d'échecs | [P] P6, validée avec le plan |
| Table industrie Yahoo → groupe, secteur, sous-secteur : majorité des membres de l'industrie ; en cas d'égalité ou sans membre, un code SIC représentatif classé par les fonctions de la recherche (`reference/construire_correspondance.py`, détail dans `reference/correspondance_yahoo.md`) ; Credit Services : financière, banque (SIC 6141) ; promotion et immobilier diversifié : industrie (SIC 6552, 6500) ; Financial Data & Stock Exchanges : financière, autres (majorité). Table figée | [M] 19/10/2026 |

Contrôle (19/10/2026) : 500 sociétés, dont 411 industrielles, 62 financières et 27 foncières, la même répartition que la
recherche au 31/08/2026 ; 90 membres exclus (recherche au 31/08/2026 : 92), dont 49 pour pertes et 36 pour fonds
propres négatifs.

## 11. Fiche épurée, phrases simples et point de vigilance (étape d, 19/10/2026)

Affichage seulement : rien dans cette partie ne change la note ni l'exclusion.

| Choix | Nature |
|---|---|
| Fiche épurée : étoiles, note sur 100 et une phrase ; une ligne par partie avec sa phrase ; les chiffres, voyants, note M, jauge, rang et membres proches sont dans des menus dépliants fermés | [M] 19/10/2026 |
| Sous chaque partie, une phrase sans vocabulaire boursier, choisie selon la valeur de chaque ratio de la partie (une quinzaine de phrases possibles par partie), qui cite le point fort ou le point faible en cause (`notabourse/phrases.py`) | [M] 19/10/2026 |
| « Point de vigilance » jaune pour une société gardée qui a : dettes ≥ 60 % de (dettes + capitalisation), EBITDA < 4 fois les intérêts, flux d'exploitation négatif, ou (financières) fonds propres < 6 % de l'actif. Référence du 19/10 : 37 des 410 membres gardés signalés. Raison : le garde-fou de la formule laisse 493 membres sur 500 en vert | [M] 19/10/2026 (« seuils moyens ») |
| Seuils des phrases : niveaux 80 / 60 / 40 / 20 pour une partie, 90 / 75 / 60 / 40 / 25 pour la note ; point fort au-dessus du 70e centile du groupe, point faible sous le 30e ; rentabilité « exceptionnelle » dès 40 % ; croissance forte dès 15 % par an, nette dès 5 % ; écart au marché net au-delà de 5 % | [P] |
| Rentabilité : la phrase compare à la médiane du secteur, pas à la moyenne (moyenne du ROE en technologie et équipements : 260 %, faussée par quelques fonds propres minuscules ; médiane : 23 %). Le tableau chiffré garde la moyenne du cahier des charges §4 | [P] |
| Croissance « typique » = médiane des taux annuels, affichée bornée à ± 100 % (une base proche de zéro donne des taux absurdes : Boeing, résultat d'exploitation −964 % en moyenne) | [P] |
| Dynamique : la phrase ne donne aucun pourcentage, car la mesure de la note neutralise les hausses extrêmes et plafonne les chutes extrêmes (fonction `tente`) : ce n'est pas la performance réelle de l'action. Le détail montre l'écart moyen et l'écart-type par semaine, tels que la note les utilise | [P] |
| Demi-étoiles dessinées en SVG (le caractère ★ colorié se décalait selon la police) | [P] |
| Jauge en demi-cercle gardée dans la vue principale, à côté des étoiles | [M] 19/10/2026 |
| Rang « mieux que … % de son groupe » de la rentabilité et des fonds propres des financières : calculé sur l'écart à la moyenne du secteur, comme la note (il redonne la note de rentabilité à 10⁻¹⁴ près sur les 463 membres notés) | [P] |
| Menus « Le calcul en détail » : ce que mesure la partie, le calcul étape par étape avec les chiffres de la société (note : S, moyenne et écart-type des S du groupe, M, centile, échelle des étoiles ; croissance : régularité et niveau ; dynamique : écart moyen, écart-type, t ou ampleur du retard ; santé : formule des voyants et leurs seuils) | [M] 19/10/2026 |
| Zone orange élargie à l'affichage : un voyant est montré orange dès le seuil du point de vigilance (dettes 60 %, EBITDA moins de 4 fois les intérêts, flux d'exploitation négatif, financières 6 % de fonds propres), rouge seulement au rouge de la formule ; la moyenne est montrée orange si un voyant l'est ; l'étiquette « Point de vigilance » passe en orange. La formule et l'exclusion ne changent pas. Référence du 19/10 : 65 voyants montrés orange | [M] 19/10/2026 |

## 12. Page Méthode (étape d, 19/10/2026)

| Choix | Nature |
|---|---|
| Contenu : la note, les quatre parties, le garde-fou, la comparaison au S&P 500, les adaptations aux données Yahoo, les limites ; sans chiffres de performance du backtest | [M] cahier des charges §5 |
| Résultat du test d'acceptation et tableau des écarts à la recherche | [M] plan validé (étape d) |
| Limites : l'échec de la première formule sur le test réservé et le fait que la formule actuelle a été construite en connaissant cette période, dit sans chiffre | [P], brouillon à valider |
| Sources : articles cités par la recherche pour chaque partie et vérifiés dans son corpus (`conception_v2.md`, `rapport.md`) | [R] |
| Texte en Markdown (`traductions/methode_fr.md`, `methode_en.md`), modifiable sans toucher au code | [P] |

## 13. Compteur des recherches (étape e, 19/10/2026)

| Choix | Nature |
|---|---|
| Table Supabase `recherches` : date, symbole, nom ; aucune donnée sur le visiteur | [M] cahier des charges (date, symbole, nom) |
| Clé publique avec la règle « insertion seule » : ni lecture, ni modification, ni effacement avec cette clé | [P] P7, validée avec le plan |
| Compteur visible par Mathys seul (tableau de bord Supabase), pas affiché sur le site | [M] 19/10/2026 |
| Une ligne par société et par visite (pas à chaque clic), envoi en arrière-plan, silence en cas de panne | [P] |
| Requête directe à l'API de Supabase avec `requests` (déjà installé), sans bibliothèque de plus | [P] |

## 14. Robot hebdomadaire (étape f, 19/10/2026)

| Choix | Nature |
|---|---|
| GitHub Actions, chaque samedi à 06:00 UTC, plus un lancement à la main | [P] P8, validée avec le plan |
| Étapes : construction, contrôle (`reference/controler_reference.py`), tests, publication des 4 fichiers de `reference/` ; un échec n'efface rien et déclenche un courriel de GitHub | [P] P6, validée avec le plan |
| Seuils du contrôle : au moins 480 membres, 90 % présents, 85 % notés, groupes d'au moins 300 / 40 / 15 sociétés (19/10/2026 : 411 / 62 / 27), aucun montant brut | [P] |
| Les courriels d'échec vont à la personne qui a créé le robot (documentation GitHub, « Notifications for workflow runs », lue le 19/10/2026) | sourcé |
| Règle des 60 jours sans activité (dépôt public) : confirmée par la documentation GitHub (« Disabling and enabling a workflow », lue le 19/10/2026), qui ne définit pas l'activité : effet des commits du robot incertain | sourcé, incertain |
| Bibliothèque `supabase` retirée de `requirements.txt` (le compteur passe par `requests`) | [P] |
| Licence MIT pour le code ; elle ne couvre pas les données de Yahoo et de la SEC | [M] 19/10/2026 (« MIT si gratuite ») |
| Auteur des commits : adresse privée de GitHub (`…@users.noreply.github.com`), jamais l'adresse personnelle | [M] 19/10/2026 |

## 15. Mise en ligne (étape g, 19/10/2026)

| Choix | Nature |
|---|---|
| Streamlit Community Cloud, Python 3.12, secrets (SEC, Supabase) collés dans les réglages de l'application | [M] cahier des charges ; procédure de la documentation Streamlit (« Deploy your app », lue le 19/10/2026) |
| Vérifié en ligne le 19/10/2026 : Apple (membre, 92), LVMH (calcul en direct, 24), Roku (classée par la SEC), Claranova (5), recherche sans résultat, anglais, page Méthode, largeur téléphone. Yahoo et la SEC répondent aux serveurs de Streamlit | [T] |

## 16. Audit de sécurité et mentions légales (19/10/2026)

| Choix | Nature |
|---|---|
| Erreurs : `showErrorDetails = "none"` (le défaut « full » montrait le code et les chemins aux visiteurs) ; erreurs imprévues attrapées, message simple, détail dans le journal du serveur | [P] |
| Mémoire bornée : caches limités (1 000 recherches, 300 fiches) pour qu'une avalanche de recherches ne fasse pas tomber le site | [P] |
| Au plus 20 nouvelles sociétés par 10 minutes et par visite (`notabourse/limites.py`) ; saisie limitée à 60 caractères | [P] |
| Textes venus de Yahoo (nom, symbole, bourse) échappés avant l'affichage Markdown ; aucun texte venu de Yahoo dans le HTML non échappé (test automatique) | [P] |
| Actions GitHub du robot figées par leur commit (checkout v4.4.0, setup-python v5.6.0) | [P] |
| Page « Mentions légales » : éditeur non professionnel anonyme (LCEN, article 1-1, II, vérifié sur Légifrance le 19/10/2026), contact par GitHub, déclaration d'intérêts générale, hébergeur et prestataires de stockage | [M] 19/10/2026 |
| Cookies de mesure d'audience déposés par l'hébergeur Streamlit (Google Analytics, Segment, Datadog, relevés le 19/10/2026) : signalés dans les mentions, comparaison d'autres hébergeurs plus tard | [M] 19/10/2026 |
| Adresses : Snowflake Inc. (dépôts SEC, 8-K d'août 2025), GitHub, Inc., Supabase (conditions d'utilisation de Supabase) ; vérifiées en ligne le 19/10/2026 | sourcé |
