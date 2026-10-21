Le backtesting consiste à tester une méthode sur le passé, comme si on l'avait suivie. Voici ce qu'aurait donné la
note de 2010 à 2026, avec un portefeuille simulé : les 50 actions du S&P 500 les mieux notées,
pondérées par leur taille en bourse (10 % au plus par action, 40 % au plus par secteur), revues une fois par an, frais
de transaction compris (0,1 % par achat ou vente). Une action déjà détenue est gardée tant qu'elle reste parmi les 60
premières. Ce portefeuille n'existe pas : je ne le propose pas et je ne le gère pas.

**À lire avant les graphiques.** Ces résultats sont simulés et calculés **en échantillon** : la formule a été mise au
point en connaissant toute la période, après 211 essais. Ils montrent que la méthode tient la route, pas qu'elle
fonctionnera à l'avenir.

### 1. Un dollar placé en 2010

1 $ placé en août 2010 devient 13,9 $, contre 9,3 $ dans le S&P 500. C'est le chiffre le plus sensible aux réglages de
la formule : il ne vaut pas grand-chose seul.

{{graphique:3_un_dollar}}

### 2. Année par année

Meilleur que le S&P 500 12 années sur 15, de 2011 à 2025 (en jaune : les années gagnées).

{{graphique:4_annees}}

### 3. Toutes les périodes de 10 ans

Le S&P 500 (dividendes réinvestis) est battu sur chacune des 75 périodes de 10 ans qui commencent entre 2010 et 2016,
de 2,4 points par an au minimum.

{{graphique:2_fenetres_10_ans}}

### 4. Le filtre « Risque de faillite »

Ce filtre ne coûte rien en rendement : 18,9 % par an sur les 10 dernières années, avec comme sans lui. En revanche, les
sociétés qu'il écarte ont perdu plus de 40 % en un an trois fois plus souvent que les autres (7,2 % contre 2,4 %). La
barre du milieu compte toutes les exclusions, bénéfices ou fonds propres négatifs compris. Limites : le filtre écarte
environ 5 sociétés par mois, et une action retirée de la cote est remplacée par le marché pour le reste de l'année, ce
qui adoucit les faillites (l'écart réel est sans doute plus grand).

{{graphique:7_exclusion}}

### 5. Limite : la note repère surtout le haut du classement

Seules les 10 % des actions les mieux notées battent nettement les autres ; les groupes 1 à 8 font à peu près pareil.
L'écart entre le haut et le bas (+3,8 points par an) n'est pas statistiquement significatif (t de 1,2). L'avance du
portefeuille vient donc du haut du classement et de la pondération par la taille, pas d'un don pour trier toutes les
actions. Les groupes 1 à 9 sont sous zéro car chaque groupe est à poids égaux, alors que le S&P 500 est porté par ses
géants.

{{graphique:1_deciles}}

### 6. Limite : des baisses plus fortes

Plus de rendement, mais des baisses plus fortes : −30,2 % au pire (en 2022), contre −23,9 % pour le S&P 500.

{{graphique:9_baisses}}

### 7. Une note cohérente hors du S&P 500

Une action notée de l'extérieur, comme une société hors du S&P 500, reçoit presque la même note que parmi les membres :
0,26 point d'écart en moyenne sur 4 197 cas. Ce graphique montre la cohérence du calcul, pas une performance.

{{graphique:8_hors_indice:sans_avertissement}}

### 8. Selon les réglages du portefeuille

L'avance tient quels que soient les réglages : de +2,5 à +4,9 points par an sur les 10 dernières années (+3,6 pour les
réglages retenus, en jaune). Les réglages retenus (plafonds par action et par secteur, tampon, revue annuelle) ont été
choisis pour la sécurité et la stabilité recherchées par la note, pas pour le rendement le plus élevé : sans plafond par
secteur, par exemple, l'avance aurait été de +4,9 points.

{{graphique:5_robustesse}}
