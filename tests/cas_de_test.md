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
| Unibail-Rodamco-Westfield SE (URW.PA) | REIT (provisoire (étape b)) | EUR / EUR | 31/12/2025 | 31/12/2025 (exercice) | 30/06/2026 | 16/10/2026 | 4 |
| LVMH Moët Hennessy - Louis Vuitton, Société Européenne (MC.PA) | NF (provisoire (étape b)) | EUR / EUR | 31/12/2025 | 31/12/2025 (exercice) | 30/06/2026 | 16/10/2026 | 4 |
| TotalEnergies SE (TTE.PA) | NF (provisoire (étape b)) | EUR / USD | 31/12/2025 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Airbus SE (AIR.PA) | NF (provisoire (étape b)) | EUR / EUR | 31/12/2025 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Toyota Motor Corporation (7203.T) | NF (provisoire (étape b)) | JPY / JPY | 31/03/2026 | 30/06/2026 (4 trimestres) | 30/06/2026 | 16/10/2026 | 4 |
| Nestlé S.A. (NESN.SW) | NF (provisoire (étape b)) | CHF / CHF | 31/12/2025 | 31/12/2025 (exercice) | 30/06/2026 | 16/10/2026 | 4 |
| Claranova SE (ALCLA.PA) | NF (provisoire (étape b)) | EUR / EUR | 30/06/2024 | 30/06/2024 (trop ancien) | 31/12/2025 | 16/10/2026 | 3 |

## 2. Ratios (définitions de la recherche, CHOIX.md §3)

| Société | ROE | ROA fin. | TLMTA | CASHMTA | Capitalisation (Md$) | Dette nette / EBITDA | Fonds propres / actif | Dynamique : moyenne, écart-type, semaines |
|---|---|---|---|---|---|---|---|---|
| AAPL | 1.2 | 0.336 | 0.0521 | 0.0118 | 5013 | 0.131 | 0.292 | 0.00147, 0.0282, 48 |
| MSFT | 0.302 | 0.195 | 0.0708 | 0.0181 | 3928 | -0.188 | 0.588 | -0.011, 0.0295, 48 |
| NVDA | 0.842 | 0.512 | 0.0164 | 0.0119 | 5171 | -0.145 | 0.715 | 0.000236, 0.0378, 48 |
| JPM | 0.17 | 0.0139 | 0.837 | 0.15 | 902.2 |  | 0.0619 | -0.000269, 0.0259, 48 |
| PLD | 0.0782 | 0.027 | 0.26 | 0.0107 | 122.2 | 5.53 | 0.536 | -0.000782, 0.0267, 48 |
| URW.PA | 0.0709 | 0.0215 | 0.686 | 0.0699 | 14.27 | 10.8 | 0.355 | -0.00157, 0.0286, 47 |
| MC.PA | 0.16 | 0.0767 | 0.224 | 0.0493 | 215.3 | 0.323 | 0.48 | -0.012, 0.032, 47 |
| TTE.PA | 0.139 | 0.0568 | 0.477 | 0.0828 | 200.3 | 0.745 | 0.454 | 0.00601, 0.0428, 47 |
| AIR.PA | 0.23 | 0.0501 | 0.42 | 0.0514 | 171.6 | -0.564 | 0.186 | -0.00306, 0.0319, 47 |
| 7203.T | 0.12 | 0.0554 | 0.638 | 0.132 | 231 | 4.98 | 0.364 | -0.0034, 0.0381, 50 |
| NESN.SW | 0.309 | 0.0701 | 0.319 | 0.0198 | 255.4 | 3.22 | 0.228 | -0.00404, 0.035, 48 |
| ALCLA.PA |  |  | 0.749 | 0.152 | 0.0322 |  | 0.331 | -0.0343, 0.0538, 47 |

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
| ALCLA.PA |  | 0.68 |  |  | 0.68 | non | oui | non |
