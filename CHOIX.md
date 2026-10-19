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
| Bilan : le plus récent disponible (trimestriel, semestriel ou annuel) | [R] « dernier bilan déposé » |
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
