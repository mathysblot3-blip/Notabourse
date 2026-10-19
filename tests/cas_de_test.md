# Cas de test : ratios, garde-fou, exclusions (généré par `tests/cas_de_test.py` le 19/10/2026)

Données Yahoo Finance du jour, mode direct. Notes finales : après la référence S&P 500 (étape b).

## 1. Données lues

| Société | Groupe (origine) | Devises cours / comptes | Dernier exercice | TTM (origine) | Bilan | Cours | Exercices |
|---|---|---|---|---|---|---|---|
| Apple Inc. (AAPL) | NF (SIC de la SEC) | USD / USD | 30/09/2025 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Microsoft Corporation (MSFT) | NF (SIC de la SEC) | USD / USD | 30/06/2026 | 30/06/2026 (exercice) | 30/06/2026 | 16/10/2026 | 4 |
| NVIDIA Corporation (NVDA) | NF (SIC de la SEC) | USD / USD | 31/01/2026 | 31/07/2026 (4 trimestres) | 31/07/2026 | 16/10/2026 | 4 |
| JPMorgan Chase & Co. (JPM) | FIN (SIC de la SEC) | USD / USD | 31/12/2025 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Prologis, Inc. (PLD) | REIT (SIC de la SEC) | USD / USD | 31/12/2025 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Unibail-Rodamco-Westfield SE (URW.PA) | REIT (industrie Yahoo) | EUR / EUR | 31/12/2025 | 31/12/2025 (exercice) | 30/06/2026 | 16/10/2026 | 4 |
| LVMH Moët Hennessy - Louis Vuitton, Société Européenne (MC.PA) | NF (industrie Yahoo) | EUR / EUR | 31/12/2025 | 31/12/2025 (exercice) | 30/06/2026 | 16/10/2026 | 4 |
| TotalEnergies SE (TTE.PA) | NF (industrie Yahoo) | EUR / USD | 31/12/2025 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Airbus SE (AIR.PA) | NF (industrie Yahoo) | EUR / EUR | 31/12/2025 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Toyota Motor Corporation (7203.T) | NF (industrie Yahoo) | JPY / JPY | 31/03/2026 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Nestlé S.A. (NESN.SW) | NF (industrie Yahoo) | CHF / CHF | 31/12/2025 | 31/12/2025 (exercice) | 30/06/2026 | 16/10/2026 | 4 |
| Claranova SE (ALCLA.PA) | NF (industrie Yahoo) | EUR / EUR | 30/06/2024 | 30/06/2024 (trop ancien) | 31/12/2025 | 16/10/2026 | 3 |

## 2. Ratios (définitions de la recherche, CHOIX.md §3)

| Société | ROE | ROA fin. | TLMTA | CASHMTA | Capitalisation (Md$) | Dette nette / EBITDA | Fonds propres / actif | Dynamique : moyenne, écart-type, semaines |
|---|---|---|---|---|---|---|---|---|
| AAPL | 1.2 | 0.336 | 0.0521 | 0.0118 | 5013 | 0.131 | 0.292 | 0.00147, 0.0282, 48 |
| MSFT | 0.302 | 0.195 | 0.0708 | 0.0181 | 3928 | -0.188 | 0.588 | -0.011, 0.0295, 48 |
| NVDA | 0.842 | 0.512 | 0.0164 | 0.0119 | 5171 | -0.145 | 0.715 | 0.000236, 0.0378, 48 |
| JPM | 0.17 | 0.0139 | 0.837 | 0.15 | 902.2 |  | 0.0619 | -0.000269, 0.0259, 48 |
| PLD | 0.0782 | 0.027 | 0.26 | 0.0107 | 122.2 | 5.53 | 0.536 | -0.000782, 0.0267, 48 |
| URW.PA | 0.0709 | 0.0215 | 0.687 | 0.07 | 14.21 | 10.8 | 0.355 | -0.00157, 0.0286, 47 |
| MC.PA | 0.16 | 0.0767 | 0.225 | 0.0494 | 214.6 | 0.323 | 0.48 | -0.012, 0.032, 47 |
| TTE.PA | 0.139 | 0.0568 | 0.478 | 0.0829 | 199.7 | 0.745 | 0.454 | 0.00601, 0.0428, 47 |
| AIR.PA | 0.23 | 0.0501 | 0.42 | 0.0514 | 171.6 | -0.564 | 0.186 | -0.00306, 0.0319, 47 |
| 7203.T | 0.12 | 0.0554 | 0.638 | 0.132 | 231 | 4.98 | 0.364 | -0.0034, 0.0381, 50 |
| NESN.SW | 0.309 | 0.0701 | 0.319 | 0.0198 | 254.7 | 3.22 | 0.228 | -0.00404, 0.035, 48 |
| ALCLA.PA |  |  | 0.747 | 0.152 | 0.03245 |  | 0.331 | -0.0343, 0.0538, 47 |

## 3. Croissances annuelles disponibles (nombre ; au moins 2 pour une note)

| Société | Croissances CA / EBITDA / FFO par action / revenus (régularité) | Niveau CA / EBITDA / revenus |
|---|---|---|
| AAPL | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| MSFT | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| NVDA | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| JPM | 3 / 0 / 3 / 3 | 3 / 0 / 3 |
| PLD | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| URW.PA | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| MC.PA | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| TTE.PA | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| AIR.PA | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| 7203.T | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| NESN.SW | 3 / 3 / 3 / 3 | 3 / 3 / 3 |
| ALCLA.PA | 2 / 2 / 2 / 2 | 2 / 2 / 2 |

## 4. Garde-fou (notes de -1 à +1 ; vert dès +0,33, rouge sous -0,33) et exclusions

| Société | Trésorerie | Endettement | Intérêts | Fonds propres / actif | Moyenne | Bénéfices 2 ans > 0 | Fonds propres > 0 | Gardée |
|---|---|---|---|---|---|---|---|---|
| AAPL | 1 | 1 |  |  | 1 | oui | oui | oui |
| MSFT | 1 | 1 | 1 |  | 1 | oui | oui | oui |
| NVDA | 1 | 1 | 1 |  | 1 | oui | oui | oui |
| JPM |  |  |  | 1 | 1 | oui | oui | oui |
| PLD | 1 | 1 | 1 |  | 1 | oui | oui | oui |
| URW.PA | 1 | 1 | 0.45 |  | 0.82 | oui | oui | oui |
| MC.PA | 1 | 1 | 1 |  | 1 | oui | oui | oui |
| TTE.PA | 1 | 1 | 1 |  | 1 | oui | oui | oui |
| AIR.PA | 1 | 1 | 1 |  | 1 | oui | oui | oui |
| 7203.T | 1 | 1 | 1 |  | 1 | oui | oui | oui |
| NESN.SW | 1 | 1 | 1 |  | 1 | oui | oui | oui |
| ALCLA.PA |  | 0.69 |  |  | 0.69 | non | oui | non |

## 5. Notes (référence S&P 500 du 19/10/2026)

| Société | Origine | Rentabilité | Croissance | Bilan | Dynamique | S | M | Note sur 100 | Étoiles | Règle | Note de recherche |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AAPL | référence (membre) | 100 | 32.4 | 90.2 | 85.2 | 77 | 1.45 | 92 | 4.5 | recherche | 92 |
| MSFT | référence (membre) | 68.7 | 100 | 93.7 | 5.77 | 67 | 0.911 | 81 | 4 | recherche | 81 |
| NVDA | référence (membre) | 98.9 | 100 | 91.3 | 75.7 | 91.5 | 2.23 | 98 | 5 | recherche | 98 |
| JPM | référence (membre) | 63.4 | 76 | 81.4 | 49.1 | 67.5 | 1.07 | 86 | 4 | recherche | 86 |
| PLD | référence (membre) | 59.7 | 62.3 | 82.1 | 82.9 | 71.7 | 0.995 | 83 | 4 | recherche | 83 |
| URW.PA | calcul contre les membres | 47.6 | 10.9 | 2.99 | 80.9 | 35.6 | -0.572 | 31.2 | 2 | recherche | 31.2 |
| MC.PA | calcul contre les membres | 43.2 | 6.34 | 91.7 | 2.63 | 36 | -0.766 | 23.8 | 1.5 | recherche | 23.8 |
| TTE.PA | calcul contre les membres | 59.7 | 0 | 82.1 | 97.1 | 59.7 | 0.517 | 69 | 3 | recherche | 69 |
| AIR.PA | calcul contre les membres | 58.5 | 59.3 | 74.5 | 57 | 62.3 | 0.657 | 73.6 | 3.5 | recherche | 73.6 |
| 7203.T | calcul contre les membres | 28.5 | 42.6 | 75.3 | 51.8 | 49.6 | -0.0326 | 50.2 | 2.5 | recherche | 50.2 |
| NESN.SW | calcul contre les membres | 80.6 | 2.83 | 66.6 | 47.7 | 49.4 | -0.0396 | 49.8 | 2.5 | recherche | 49.8 |
| ALCLA.PA | calcul contre les membres |  | 42.6 | 18.3 | 0 | 20.3 | -1.61 | 4.84 | 0.5 | recherche | 4.84 |
