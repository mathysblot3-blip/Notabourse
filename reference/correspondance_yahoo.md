# Correspondance industrie Yahoo -> groupe, secteur, sous-secteur (généré par `construire_correspondance.py`)

Calibrée sur 500 membres du S&P 500 classés par le SIC de la SEC. 145 industries Yahoo :
112 avec des membres, 33 sans membre (SIC représentatif).
Ne sert qu'aux sociétés qui ne déposent pas à la SEC.

## Industries où les membres ne sont pas tous classés pareil (34)

| Secteur Yahoo | Industrie Yahoo | Classement retenu | Règle | Membres | Part majoritaire | Membres en désaccord |
|---|---|---|---|---|---|---|
| Basic Materials | Specialty Chemicals | NF / Chems / Chems | membres | 9 | 89% | SHW (NF / Shops / Shops) |
| Basic Materials | Building Materials | NF / Other / Other | membres | 3 | 67% | CRH (NF / Manuf / Manuf) |
| Communication Services | Entertainment | NF / Other / Other | membres | 7 | 57% | FOXA (NF / Telcm / Telcm), NWSA (NF / NoDur / NoDur), SKYD (NF / Telcm / Telcm) |
| Communication Services | Advertising Agencies | NF / Other / Other | SIC représentatif 7311 | 2 | 50% (égalité) | OMC (NF / Other / Other) |
| Consumer Cyclical | Internet Retail | NF / Other / Other | membres | 3 | 67% | AMZN (NF / Shops / Shops) |
| Consumer Cyclical | Apparel Retail | NF / Shops / Shops | membres | 3 | 67% | LULU (NF / NoDur / NoDur) |
| Consumer Cyclical | Auto Parts | NF / Shops / Shops | membres | 4 | 75% | APTV (NF / Durbl / Durbl) |
| Consumer Cyclical | Packaging & Containers | NF / Manuf / Manuf | membres | 6 | 83% | AMCR (NF / Durbl / Durbl) |
| Consumer Defensive | Household & Personal Products | NF / Chems / Chems | membres | 7 | 86% | KMB (NF / Manuf / Manuf) |
| Energy | Oil & Gas E&P | NF / Enrgy / Enrgy | membres | 9 | 89% | TPL (NF / Other / Other) |
| Energy | Oil & Gas Equipment & Services | NF / Enrgy / Enrgy | membres | 3 | 67% | BKR (NF / Manuf / Manuf) |
| Financial Services | Credit Services | FIN / FIN / banques | SIC représentatif 6141 | 6 | 50% (égalité) | MA (NF / Other / Other), PYPL (NF / Other / Other), V (NF / Other / Other) |
| Financial Services | Asset Management | FIN / FIN / autres | membres | 13 | 77% | NTRS (FIN / FIN / banques), PFG (FIN / FIN / assurances), STT (FIN / FIN / banques) |
| Financial Services | Financial Data & Stock Exchanges | FIN / FIN / autres | membres | 9 | 44% | COIN (FIN / FIN / banques), FDS (NF / BusEq / BusEq), MCO (NF / Other / Other), MSCI (NF / Other / Other), SPGI (NF / Other / Other) |
| Healthcare | Biotechnology | NF / Hlth / Hlth | membres | 5 | 80% | INCY (NF / Other / Other) |
| Healthcare | Diagnostics & Research | NF / BusEq / BusEq | membres | 12 | 58% | CRL (NF / Other / Other), IDXX (NF / Hlth / Hlth), IQV (NF / Other / Other), LH (NF / Hlth / Hlth), DGX (NF / Hlth / Hlth) |
| Healthcare | Healthcare Plans | FIN / FIN / assurances | membres | 6 | 83% | CVS (NF / Shops / Shops) |
| Industrials | Aerospace & Defense | NF / Manuf / Manuf | membres | 13 | 85% | LHX (NF / BusEq / BusEq), NOC (NF / BusEq / BusEq) |
| Industrials | Specialty Industrial Machinery | NF / Manuf / Manuf | membres | 17 | 82% | AOS (NF / Durbl / Durbl), AME (NF / BusEq / BusEq), ROK (NF / BusEq / BusEq) |
| Industrials | Farm & Heavy Construction Machinery | NF / Manuf / Manuf | membres | 3 | 67% | PCAR (NF / Durbl / Durbl) |
| Industrials | Railroads | NF / Other / Other | membres | 4 | 75% | WAB (NF / Manuf / Manuf) |
| Industrials | Building Products & Equipment | NF / Manuf / Manuf | membres | 5 | 80% | TT (NF / BusEq / BusEq) |
| Industrials | Specialty Business Services | NF / Other / Other | SIC représentatif 7389 | 3 | 33% (égalité) | CPRT (NF / Shops / Shops), GPN (NF / Other / Other) |
| Industrials | Electrical Equipment & Parts | NF / BusEq / BusEq | membres | 3 | 67% | BE (NF / Manuf / Manuf) |
| Industrials | Conglomerates | NF / Manuf / Manuf | SIC représentatif 3600 | 2 | 50% (égalité) | HON (NF / Manuf / Manuf) |
| Industrials | Consulting Services | NF / Other / Other | SIC représentatif 8742 | 2 | 50% (égalité) | VRSK (NF / BusEq / BusEq) |
| Real Estate | REIT - Residential | REIT / REIT / REIT | membres | 6 | 83% | INVH (NF / Other / Other) |
| Technology | Software - Infrastructure | NF / BusEq / BusEq | membres | 16 | 88% | AKAM (NF / Other / Other), CPAY (NF / Other / Other) |
| Technology | Software - Application | NF / BusEq / BusEq | membres | 15 | 80% | FICO (NF / Other / Other), PAYX (NF / Other / Other), UBER (NF / Other / Other) |
| Technology | Semiconductor Equipment & Materials | NF / BusEq / BusEq | membres | 5 | 80% | LRCX (NF / Manuf / Manuf) |
| Technology | Communication Equipment | NF / BusEq / BusEq | membres | 6 | 83% | ZBRA (NF / Manuf / Manuf) |
| Technology | Information Technology Services | NF / BusEq / BusEq | SIC représentatif 7370 | 9 | 44% (égalité) | CDW (NF / Shops / Shops), CTSH (NF / BusEq / BusEq), IBM (NF / BusEq / BusEq), JKHY (NF / BusEq / BusEq), LDOS (NF / BusEq / BusEq) |
| Technology | Electronic Components | NF / BusEq / BusEq | membres | 5 | 60% | GLW (NF / Manuf / Manuf), TEL (NF / Shops / Shops) |
| Utilities | Utilities - Diversified | NF / Utils / Utils | SIC représentatif 4931 | 2 | 50% (égalité) | SRE (NF / Utils / Utils) |

## Industries sans aucun membre du S&P 500 (33) : SIC représentatif

| Secteur Yahoo | Industrie Yahoo | Classement retenu | Règle | Membres | | |
|---|---|---|---|---|---|---|
| Basic Materials | Other Industrial Metals & Mining | NF / Other / Other | SIC représentatif 1000 | 0 |  |  |
| Basic Materials | Other Precious Metals & Mining | NF / Other / Other | SIC représentatif 1040 | 0 |  |  |
| Basic Materials | Aluminum | NF / Manuf / Manuf | SIC représentatif 3334 | 0 |  |  |
| Basic Materials | Lumber & Wood Production | NF / Other / Other | SIC représentatif 2400 | 0 |  |  |
| Basic Materials | Silver | NF / Other / Other | SIC représentatif 1044 | 0 |  |  |
| Basic Materials | Coking Coal | NF / Enrgy / Enrgy | SIC représentatif 1220 | 0 |  |  |
| Basic Materials | Paper & Paper Products | NF / Manuf / Manuf | SIC représentatif 2621 | 0 |  |  |
| Communication Services | Publishing | NF / NoDur / NoDur | SIC représentatif 2711 | 0 |  |  |
| Communication Services | Broadcasting | NF / Telcm / Telcm | SIC représentatif 4833 | 0 |  |  |
| Consumer Cyclical | Furnishings, Fixtures & Appliances | NF / Durbl / Durbl | SIC représentatif 2510 | 0 |  |  |
| Consumer Cyclical | Gambling | NF / Other / Other | SIC représentatif 7990 | 0 |  |  |
| Consumer Cyclical | Recreational Vehicles | NF / Durbl / Durbl | SIC représentatif 3716 | 0 |  |  |
| Consumer Cyclical | Department Stores | NF / Shops / Shops | SIC représentatif 5311 | 0 |  |  |
| Consumer Cyclical | Textile Manufacturing | NF / NoDur / NoDur | SIC représentatif 2200 | 0 |  |  |
| Consumer Defensive | Education & Training Services | NF / Other / Other | SIC représentatif 8200 | 0 |  |  |
| Energy | Uranium | NF / Other / Other | SIC représentatif 1094 | 0 |  |  |
| Energy | Oil & Gas Drilling | NF / Enrgy / Enrgy | SIC représentatif 1381 | 0 |  |  |
| Energy | Thermal Coal | NF / Enrgy / Enrgy | SIC représentatif 1220 | 0 |  |  |
| Financial Services | Insurance - Specialty | FIN / FIN / assurances | SIC représentatif 6351 | 0 |  |  |
| Financial Services | Mortgage Finance | FIN / FIN / banques | SIC représentatif 6162 | 0 |  |  |
| Financial Services | Financial Conglomerates | FIN / FIN / banques | SIC représentatif 6199 | 0 |  |  |
| Healthcare | Pharmaceutical Retailers | NF / Shops / Shops | SIC représentatif 5912 | 0 |  |  |
| Industrials | Metal Fabrication | NF / Manuf / Manuf | SIC représentatif 3440 | 0 |  |  |
| Industrials | Marine Shipping | NF / Other / Other | SIC représentatif 4400 | 0 |  |  |
| Industrials | Staffing & Employment Services | NF / Other / Other | SIC représentatif 7363 | 0 |  |  |
| Industrials | Airports & Air Services | NF / Other / Other | SIC représentatif 4581 | 0 |  |  |
| Industrials | Business Equipment & Supplies | NF / BusEq / BusEq | SIC représentatif 3579 | 0 |  |  |
| Industrials | Infrastructure Operations | NF / Other / Other | SIC représentatif 1600 | 0 |  |  |
| Real Estate | REIT - Mortgage | REIT / REIT / REIT | SIC représentatif 6798 | 0 |  |  |
| Real Estate | Real Estate - Development | NF / Other / Other | SIC représentatif 6552 | 0 |  |  |
| Real Estate | Real Estate - Diversified | NF / Other / Other | SIC représentatif 6500 | 0 |  |  |
| Technology | Electronics & Computer Distribution | NF / Shops / Shops | SIC représentatif 5045 | 0 |  |  |
| Utilities | Utilities - Renewable | NF / Utils / Utils | SIC représentatif 4911 | 0 |  |  |
