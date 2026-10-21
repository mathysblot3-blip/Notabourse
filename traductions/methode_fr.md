Bourse à lunettes note la **force** d'une action : sa capacité à donner des rendements stables et persistants à long terme. La
note vient de mon travail de recherche sur les membres du S&P 500. Le site applique cette formule, sans la
modifier, aux données de Yahoo Finance.

### En bref

- Quatre parties notées de 0 à 100 : **rentabilité, croissance, bilan, dynamique**.
- Chaque société est comparée aux membres du S&P 500 de **son groupe** : industrie et services, financières, ou
  foncières cotées.
- La moyenne des quatre parties donne la **note M**, puis la **note sur 100**. 50 = au milieu.
- Une santé financière fragile, des pertes récentes ou des fonds propres négatifs **excluent** la société de la
  sélection, sans changer sa note. L'indicateur « Risque de faillite » de chaque fiche le signale.
- La note **ne dit pas si l'action est chère** : chaque fiche l'indique à part, en comparant son prix à
  celui de son secteur (partie 6). Elle **n'est pas un conseil** en investissement.

### 1. Les quatre parties

| Partie | Question posée | Ratios utilisés |
|---|---|---|
| Rentabilité | Gagne-t-elle bien sa vie, comparée à ses concurrents ? | Bénéfice des 12 derniers mois / fonds propres (ROE), en écart à la moyenne de son secteur. Financières : bénéfice / actif, en écart à leur sous-secteur (banques, assurances, autres) |
| Croissance | Ses ventes et ses résultats progressent-ils, et régulièrement ? | Croissance annuelle des ventes et du résultat d'exploitation (EBITDA) sur les 4 derniers exercices : régularité (une mauvaise année pèse jusqu'à trois fois plus qu'une bonne) et niveau. Foncières : résultat courant par action (FFO) ; financières : revenus |
| Bilan | Résiste-t-elle aux coups durs ? | Dettes et trésorerie rapportées à la valeur de l'entreprise (dettes + valeur en bourse), et taille. Foncières : dette nette / EBITDA. Financières : fonds propres / actif, et taille |
| Dynamique | L'action fait-elle mieux que le marché, et régulièrement ? | Écart hebdomadaire avec le S&P 500 (dividendes compris) sur 11 mois, dernier mois exclu ; les semaines de hausse exceptionnelle sont neutralisées |

Pour chaque ratio, les valeurs extrêmes sont ramenées aux 5e et 95e centiles, puis la société est classée parmi son
groupe. La note de 0 à 100 traduit ce rang : 0 pour les 5 % les moins bons, 100 pour les 5 % les meilleurs.

J'ai aussi testé la volatilité du cours et le prix (bénéfice ou EBITDA rapportés à la valeur de l'entreprise), sans
les garder : choisir des actions calmes a coûté du rendement, et le prix donnait des résultats irréguliers d'une
période à l'autre. La sécurité vient donc de l'exclusion des sociétés en danger (partie 4), pas du choix d'actions
calmes.

### 2. De quatre notes à une note sur 100

1. **S** = moyenne des notes de partie disponibles (au moins 2).
2. **M** = (S − moyenne des S du groupe) / écart-type des S du groupe. Comparer à l'intérieur du groupe évite de juger
   une banque avec les critères d'un industriel.
3. **Note sur 100** = part des membres du S&P 500 dont la note M est plus basse.
4. **Étoiles** : 5 dès 95, 4,5 dès 90, 4 dès 80, 3,5 dès 70, 3 dès 55, 2,5 dès 40, 2 dès 30, 1,5 dès 20, 1 dès 10,
   0,5 en dessous.

Chaque fiche montre ces calculs avec les chiffres de la société, dans les menus « Détail des calculs ».

### 3. Groupes et secteurs

Le groupe et le secteur viennent du code d'activité (SIC) que la société déclare à la SEC (Securities and Exchange
Commission), l'autorité des marchés américaine, rangé dans les 12 secteurs de Fama et French. Sans code SEC (la
plupart des sociétés non américaines), le site prend l'industrie indiquée par Yahoo Finance et la rattache au groupe et au secteur le plus fréquent parmi les
membres du S&P 500 de cette industrie.

### 4. Le risque de faillite

Trois voyants, notés de −1 à +1 (une financière n'en a qu'un : fonds propres / actif) :

| Voyant | Vert | Rouge |
|---|---|---|
| Trésorerie, si l'activité consomme de l'argent | 2 ans de trésorerie ou plus | 1 an ou moins |
| Endettement : dettes / (dettes + valeur en bourse) | 80 % ou moins | 90 % ou plus |
| Intérêts : EBITDA / intérêts | 2 fois ou plus | 1 fois ou moins |
| Financières : fonds propres / actif | 5 % ou plus | 4 % ou moins |

La société est **exclue de la sélection** si la moyenne de ses voyants n'est pas verte, si elle a perdu de l'argent sur
l'un de ses deux derniers exercices, ou si ses fonds propres sont négatifs. L'exclusion ne change pas la note : elle
signale que la société ne remplit pas une condition de sécurité de la méthode.

Ces seuils laissent passer presque tout le S&P 500. Pour prévenir plus tôt, le site montre en **orange** un « point de
vigilance » dès 60 % de dettes, un EBITDA inférieur à 4 fois les intérêts, un flux d'exploitation négatif ou, pour une
financière, moins de 6 % de fonds propres. Cet orange est un avertissement d'affichage : il ne change ni la note ni
l'exclusion.

### 5. Les données

- Comptes, cours et capitalisations : **Yahoo Finance**.
- 12 derniers mois : les 4 derniers trimestres publiés, sinon le dernier exercice (sociétés qui publient par semestre).
- La référence, c'est-à-dire les membres du S&P 500 et leurs ratios, est recalculée automatiquement chaque samedi.
- Le site compte les recherches (date et société cherchée) pour savoir ce qui intéresse ; il n'enregistre rien sur
  le visiteur.

La note du site est une adaptation de ma note de recherche, calculée sur les comptes déposés à la SEC. Avant la
mise en ligne, j'ai vérifié qu'elles concordent : sur les membres du S&P 500, corrélation de rang de 0,95 et écart
médian de 4 points sur 100.

### 6. Le prix comparé au secteur

Chaque fiche compare le prix de l'action à celui des autres sociétés de son secteur. Ce repère est à part : il n'entre
pas dans la note.

1. **PER** de la société = valeur en bourse / bénéfice net des 12 derniers mois : le prix vaut tant de fois le
   bénéfice annuel. Une société en perte n'a pas de PER.
2. **PER du secteur** = 1 / moyenne des (bénéfice / valeur en bourse) des membres du S&P 500 bénéficiaires du même
   secteur (au moins 5, sinon tout le groupe). C'est la moyenne harmonique de leurs PER : une société au bénéfice
   minuscule, donc au PER énorme, ne fausse pas la moyenne. Comparer à des sociétés semblables et prendre cette moyenne
   suit Liu, Nissim et Thomas (2002), voir la page Sources.
3. **Écart** = PER / PER du secteur − 1. L'action est dite **bon marché** à −20 % ou moins, **chère** à +25 % ou plus,
   **dans la norme** entre les deux. Les deux seuils se répondent : 1 / 0,8 = 1,25.

Quand un chiffre manque, la fiche donne quand même une estimation, signalée « valeur peu fiable » :
bénéfice du dernier exercice, bénéfice moyen des derniers exercices pour une société en perte, PER donné par Yahoo
Finance ou, en dernier recours, prix rapporté aux ventes face au même rapport dans le secteur.

Ce repère décrit le prix, il ne prédit rien : sur 2010-2026, il n'a eu aucun lien net avec le rendement des 12 mois
suivants.

### 7. Rôle de l'IA

J'ai mené ce projet avec Claude Code (modèle Opus 5.5 d'Anthropic), une intelligence artificielle. Tous les choix sont
les miens ou ont été validés par moi ; l'IA a fait les choses suivantes :

- mener des recherches en ligne ;
- écrire tout le code Python, de la recherche comme du site ;
- télécharger les données gratuites (comptes déposés à la SEC, cours, indices) et vérifier qu'aucune donnée du futur
  n'est utilisée ;
- lancer les calculs : backtests, test réservé, 211 essais, tests statistiques ;
- produire les graphiques, les rapports et les textes, que j'ai relus et corrigés.

L'IA s'est trompée plusieurs fois (données manquantes, mois oublié dans un calcul). Chaque erreur trouvée a été
corrigée, mais l'IA est imparfaite : des erreurs peuvent subsister.

### 8. Limites

- **Ce n'est pas un conseil en investissement.** Je ne suis pas conseiller financier agréé.
- **Rien n'est prouvé en réel.** Une première formule, fixée avant le test, a échoué sur la période de test réservée
  (2018-2026). La formule actuelle a été construite ensuite, en connaissant cette période : ce qu'elle a fait sur le passé
  peut tenir de la chance. Sa preuve ne peut venir que du suivi dans le temps. Les résultats simulés, bons et
  mauvais, sont sur la page Backtesting.
- **La note ignore le prix.** Une très bonne société peut être une action trop chère ; le prix est tout de même
  indiqué sur chaque fiche, comparé à celui du secteur (partie 6).
- **Une note relative.** Elle compare la société aux membres du S&P 500 du moment : elle peut baisser parce que les
  autres progressent.
- **Conçue pour les grandes sociétés américaines.** Pour une petite société ou une société étrangère, la comparaison est
  moins sûre (normes comptables, devises, données plus rares).
- **Données sans garantie.** Yahoo Finance peut contenir des erreurs ou des trous ; une fiche peut changer quand Yahoo
  corrige ses données.
