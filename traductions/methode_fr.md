NotaBourse note la **force** d'une action : sa capacité à donner des rendements stables et persistants à long terme. La
note vient d'un travail de recherche de Mathys Blot sur les membres du S&P 500. Le site applique cette formule, sans la
modifier, aux données de Yahoo Finance.

### En bref

- Quatre parties notées de 0 à 100 : **rentabilité, croissance, bilan, dynamique**.
- Chaque société est comparée aux membres du S&P 500 de **son groupe** : industrie et services, financières, ou
  foncières cotées.
- La moyenne des quatre parties donne la **note M**, puis la **note sur 100** : la part des membres du S&P 500 qui font
  moins bien. 50 = au milieu.
- Une santé financière fragile, des pertes récentes ou des fonds propres négatifs **excluent** la société de la
  sélection, sans changer sa note.
- La note **ne dit pas si l'action est chère** et **n'est pas un conseil** en investissement.

### 1. Les quatre parties

| Partie | Question posée | Ratios utilisés |
|---|---|---|
| Rentabilité | Gagne-t-elle bien sa vie, comparée à ses concurrents ? | Bénéfice des 12 derniers mois / fonds propres (ROE), en écart à la moyenne de son secteur. Financières : bénéfice / actif, en écart à leur sous-secteur (banques, assurances, autres) |
| Croissance | Ses ventes et ses résultats progressent-ils, et régulièrement ? | Croissance annuelle des ventes et du résultat d'exploitation (EBITDA) sur les 4 derniers exercices : régularité (une mauvaise année pèse jusqu'à trois fois plus qu'une bonne) et niveau. Foncières : résultat courant par action (FFO) ; financières : revenus |
| Bilan | Résiste-t-elle aux coups durs ? | Dettes et trésorerie rapportées à la valeur de l'entreprise (dettes + valeur en bourse), et taille. Foncières : dette nette / EBITDA. Financières : fonds propres / actif, et taille |
| Dynamique | L'action fait-elle mieux que le marché, et régulièrement ? | Écart hebdomadaire avec le S&P 500 (dividendes compris) sur 11 mois, dernier mois exclu ; les semaines de hausse exceptionnelle sont neutralisées |

Pour chaque ratio, les valeurs extrêmes sont ramenées aux 5e et 95e centiles, puis la société est classée parmi son
groupe. La note de 0 à 100 traduit ce rang : 0 pour les 5 % les moins bons, 100 pour les 5 % les meilleurs.

### 2. De quatre notes à une note sur 100

1. **S** = moyenne des notes de partie disponibles (au moins 2).
2. **M** = (S − moyenne des S du groupe) / écart-type des S du groupe. Comparer à l'intérieur du groupe évite de juger
   une banque avec les critères d'un industriel.
3. **Note sur 100** = part des membres du S&P 500 dont la note M est plus basse.
4. **Étoiles** : 5 dès 95, 4,5 dès 90, 4 dès 80, 3,5 dès 70, 3 dès 55, 2,5 dès 40, 2 dès 30, 1,5 dès 20, 1 dès 10,
   0,5 en dessous.

Chaque fiche montre ces calculs avec les chiffres de la société, dans les menus « Le calcul en détail ».

### 3. Groupes et secteurs

Le groupe et le secteur viennent du code d'activité (SIC) que la société déclare à la SEC, l'autorité des marchés
américaine, rangé dans les 12 secteurs de Fama et French. Sans code SEC (la plupart des sociétés non américaines), le
site prend l'industrie indiquée par Yahoo Finance et la rattache au groupe et au secteur le plus fréquent parmi les
membres du S&P 500 de cette industrie.

### 4. La santé financière (garde-fou)

Trois voyants, notés de −1 à +1 (une financière n'en a qu'un : fonds propres / actif) :

| Voyant | Vert | Rouge |
|---|---|---|
| Trésorerie, si l'activité consomme de l'argent | 2 ans de trésorerie ou plus | 1 an ou moins |
| Endettement : dettes / (dettes + valeur en bourse) | 80 % ou moins | 90 % ou plus |
| Intérêts : EBITDA / intérêts | 2 fois ou plus | 1 fois ou moins |
| Financières : fonds propres / actif | 5 % ou plus | 4 % ou moins |

La société est **exclue de la sélection** si la moyenne de ses voyants n'est pas verte, si elle a perdu de l'argent sur
l'un de ses deux derniers exercices, ou si ses fonds propres sont négatifs. L'exclusion ne change pas la note : elle
signale que la société ne remplit pas une condition de sécurité de la méthode.

Ces seuils laissent passer presque tout le S&P 500. Pour prévenir plus tôt, le site montre en **orange** un « point de
vigilance » dès 60 % de dettes, un EBITDA inférieur à 4 fois les intérêts, un flux d'exploitation négatif ou, pour une
financière, moins de 6 % de fonds propres. Cet orange est un avertissement d'affichage : il ne change ni la note ni
l'exclusion.

### 5. Les données

- Comptes, cours et capitalisations : **Yahoo Finance**, convertis en dollars. Les ratios sont calculés poste par poste
  comme dans la recherche.
- 12 derniers mois : les 4 derniers trimestres publiés, sinon le dernier exercice (sociétés qui publient par semestre).
- Le site compte les recherches (date et société cherchée) pour savoir ce qui intéresse ; il n'enregistre rien sur
  le visiteur.
- Les membres du S&P 500 sont notés entre eux **chaque semaine** ; leur fiche vient de ce calcul. Une autre société est
  calculée à la demande, puis comparée à ces membres comme si on l'ajoutait à son groupe, sans changer leurs notes.

### 6. Ce qui diffère de la recherche

La recherche a été menée sur les comptes déposés à la SEC. Le site applique la même formule aux données de Yahoo, avec
ces adaptations :

| Adaptation | Pourquoi |
|---|---|
| Données Yahoo Finance au lieu des dépôts SEC ; postes comptables choisis par définition, avant tout test | Yahoo couvre les sociétés du monde entier, la SEC seulement celles qui y déposent leurs comptes |
| Résultat d'exploitation : celui de Yahoo, déjà nettoyé des éléments exceptionnels | Le retraiter à nouveau compterait deux fois les dépréciations |
| Croissance annuelle sur 4 exercices, au lieu de trimestrielle sur 5 ans | Yahoo ne garde que quelques années de comptes |
| Note dès 2 parties, avec un avertissement (la recherche exige la dynamique) | Choix de l'auteur : noter aussi les sociétés incomplètes, en le signalant |
| Sociétés cotées depuis moins de 12 mois notées, avec un avertissement (la recherche ne les note pas) | Même choix |
| Classement par l'industrie Yahoo quand la SEC n'a pas de code d'activité | Sociétés non américaines |
| Comptes en normes IFRS (sociétés européennes, asiatiques...) | Définitions proches mais pas identiques (loyers, éléments exceptionnels) : comparaison moins exacte |
| Phrases simples et point de vigilance orange | Affichage seulement : la note ne change pas |

**Test d'acceptation (19/10/2026).** Avant la mise en ligne, le site a recalculé avec les données Yahoo les notes des
membres du S&P 500 à la dernière date de la recherche (31/08/2026), puis les a comparées aux notes de recherche. Les
seuils avaient été fixés avant le calcul.

| Mesure | Résultat | Seuil |
|---|---|---|
| Corrélation de rang des notes M (495 sociétés notées des deux côtés) | 0,95 | 0,80 au moins |
| Écart médian de la note sur 100 | 4 points | moins de 10 |
| Financières seules | 0,88 ; 7 points | |

Test réussi. Les plus gros écarts viennent de données absentes d'un côté ou de l'autre, de la définition du bénéfice
chez les gérants d'actifs, et de la croissance annuelle.

### 7. Limites

- **Ce n'est pas un conseil en investissement.** L'auteur n'est pas un conseiller financier agréé.
- **Rien n'est prouvé en réel.** Une première formule, fixée avant le test, a échoué sur la période de test réservée
  (2018-2026). La formule actuelle a été construite ensuite, en connaissant cette période : ce qu'elle a fait sur le passé
  peut tenir de la chance. Sa preuve ne peut venir que du suivi dans le temps.
- **La note ignore le prix.** Une très bonne société peut être une action trop chère.
- **Une note relative.** Elle compare la société aux membres du S&P 500 du moment : elle peut baisser parce que les
  autres progressent.
- **Conçue pour les grandes sociétés américaines.** Pour une petite société ou une société étrangère, la comparaison est
  moins sûre (normes comptables, devises, données plus rares).
- **Données sans garantie.** Yahoo Finance peut contenir des erreurs ou des trous ; une fiche peut changer quand Yahoo
  corrige ses données.

### 8. Sources

La méthode s'appuie notamment sur Novy-Marx (2013) pour la comparaison au secteur, Chan, Karceski et Lakonishok (2003)
et Lakonishok, Shleifer et Vishny (1994) pour la croissance, Campbell, Hilscher et Szilagyi (2008) pour l'endettement
et la trésorerie, et Jegadeesh et Titman (1993) pour la dynamique. Données : Yahoo Finance, SEC (codes d'activité),
secteurs de Fama et French.
