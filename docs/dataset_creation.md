# Création et historique des versions du dataset et du modèle — V1 à V7

## Contexte

Objectif : construire un premier modèle de détection de chute avec Edge Impulse à partir de données IMU.

Configuration de base retenue au fil des essais :
- Capteur IMU à **50 Hz**
- Classification binaire : **`fall`** / **`not_fall`**
- Données d'entrée par fenêtre temporelle
- Entraînement dans **Edge Impulse**
- Comparaison des versions par :
  - accuracy
  - AUC
  - rappel `fall`
  - rappel `not_fall`
  - F1 score

L'idée générale a été d'avancer par itérations contrôlées, en modifiant **un levier à la fois** pour comprendre ce qui améliore réellement la séparation entre `fall` et `not_fall`.

---

## Problème majeur découvert en cours de route

Le point clé identifié après plusieurs essais est le suivant :

Le dataset initial était basé sur le dataset **SisFall**, dans lequel :
- chaque fichier correspond à un enregistrement complet lié à une personne
- certains fichiers correspondent à des mouvements normaux (`not_fall`)
- d'autres correspondent à des chutes (`fall`)
- un fichier de chute dure environ **15 s**
- mais il ne contient en réalité qu'**une seule vraie chute**, sur une portion beaucoup plus courte

### Erreur de construction du dataset initial
Pour construire les premières versions, les enregistrements complets ont été découpés en fenêtres de **1 s** ou **2 s**, puis :
- tout fichier de chute a été considéré comme entièrement `fall`
- donc toutes les fenêtres extraites de ce fichier ont hérité du label `fall`

Cela a créé un très fort **bruit de label** :
- beaucoup de fenêtres `fall` ne contenaient pas réellement la chute
- certaines contenaient seulement la phase avant chute
- d'autres seulement la phase après impact
- d'autres encore ressemblaient à du mouvement normal

### Conséquence
Le modèle apprenait sur des exemples contradictoires :
- des mouvements normaux étiquetés `fall`
- des fenêtres peu discriminantes étiquetées `fall`

Cela a été identifié comme la vraie cause principale des mauvais résultats de V1 à V5.

---

## V1 — Première version de référence

### Structure
- **Fenêtre de 2 secondes**
- **100 points** par fenêtre à 50 Hz
- **6 canaux bruts** :
  - `gx`, `gy`, `gz`
  - `ax`, `ay`, `az`
- Format aplati en une ligne CSV par fenêtre
- Label final : `fall` ou `not_fall`

### But
Obtenir une **baseline simple** avec le pipeline minimal :
- dataset CSV
- import dans Edge Impulse
- impulsion tabulaire
- classifieur standard
- paramètres d'entraînement par défaut

### Résultats observés
- Accuracy : **58,3%**
- AUC : **0,57**
- F1 `fall` : **0,42**
- Rappel `fall` : **55,3%**

### Interprétation
Le modèle est à peine meilleur que le hasard. Il sépare mal les deux classes et commet :
- beaucoup de faux négatifs sur `fall`
- beaucoup de faux positifs sur `not_fall`

### Conclusion V1
La baseline fonctionne techniquement, mais la représentation des données est trop faible pour bien distinguer les chutes de mouvements brusques non dangereux.

---

## V2 — Ajout de signaux dérivés

### Modification apportée
Ajout de deux nouvelles features calculées à chaque pas de temps :
- `g_norm = sqrt(gx² + gy² + gz²)`
- `a_norm = sqrt(ax² + ay² + az²)`

### Nouvelle structure
- Toujours **2 secondes**
- Toujours **100 points**
- Passage de **6 canaux** à **8 canaux** :
  - `gx`, `gy`, `gz`
  - `ax`, `ay`, `az`
  - `g_norm`, `a_norm`

### But
Tester si les normes du gyroscope et de l'accéléromètre donnent au modèle une information globale plus utile sur :
- l'intensité de rotation
- l'intensité d'accélération

### Point de vigilance dans Edge Impulse
Il a fallu vérifier que :
- toutes les colonnes `g_norm_*` étaient cochées
- toutes les colonnes `a_norm_*` étaient cochées
- `window_id` et `source_file` n'étaient pas utilisées comme features

### Résultats observés
- Accuracy : **56,5%**
- AUC : **0,59**
- F1 `fall` : **0,45**
- Rappel `fall` : **65,4%**

### Interprétation
Ce n'est pas mieux globalement, mais ce n'est pas totalement pire non plus :
- le rappel `fall` monte
- le F1 `fall` monte légèrement
- l'AUC monte légèrement
- mais l'accuracy baisse
- les faux positifs restent très élevés

### Conclusion V2
`g_norm` et `a_norm` apportent un petit signal utile, mais ne débloquent pas le problème principal.

---

## V3 — Rééquilibrage des classes

### Modification apportée
Création d'un dataset équilibré :
- conservation de tous les `fall`
- sélection du même nombre de `not_fall`

### Structure
- Toujours **2 secondes**
- Toujours **100 points**
- Toujours **8 canaux**
- Dataset équilibré :
  - `fall` : **1050**
  - `not_fall` : **1050**

### But
Tester si le déséquilibre des classes explique une part importante des mauvaises performances.

### Résultats observés
- Accuracy : **57,0%**
- AUC : **0,57**
- F1 `fall` : **0,60**
- Rappel `fall` : **66,1%**
- Rappel `not_fall` : **48,3%**

### Interprétation
Le modèle devient plus agressif sur `fall` :
- il détecte un peu plus de chutes
- mais il classe encore beaucoup trop de `not_fall` comme des chutes

### Conclusion V3
L'équilibrage aide un peu la classe `fall`, mais ne résout pas le fond du problème. Le verrou principal n'était donc pas seulement le déséquilibre des classes.

---

## V4 — Réduction de la fenêtre à 1 seconde

### Modification apportée
Réduction de la taille de fenêtre :
- de **2 secondes** à **1 seconde**
- de **100 points** à **50 points**

### Structure
- **1 seconde**
- **50 points**
- **8 canaux**
- Dataset équilibré
- 400 features capteurs par fenêtre

### But
Tester si la fenêtre de 2 s diluait trop le signal utile de la chute.

### Résultats observés
- Accuracy : **57,9%**
- AUC : **0,58**
- F1 `fall` : **0,64**
- Rappel `fall` : **75,4%**
- Rappel `not_fall` : **41,4%**

### Interprétation
La réduction de la fenêtre aide clairement à mieux détecter les chutes :
- le rappel `fall` monte nettement
- le F1 `fall` monte aussi

Mais :
- les faux positifs restent très élevés
- le modèle sur-détecte `fall`

### Conclusion V4
La fenêtre de **1 seconde** est meilleure que celle de **2 secondes** pour ce problème. La taille de fenêtre était bien un levier important.

V4 devient la nouvelle baseline utile pour les étapes suivantes.

---

## V5 — Ajouter plus de `not_fall` difficiles

### Hypothèse
Le modèle fait encore beaucoup de faux positifs parce qu'il ne connaît pas assez de cas `not_fall` ressemblant à des chutes.

### Principe
Créer une version avec :
- plus de `not_fall`
- mais surtout des `not_fall` **difficiles / confondants**

### Types de `not_fall` recherchés
Exemples pertinents :
- trébuchements rattrapés
- s'asseoir brusquement
- mouvements rapides du buste
- changements de direction violents
- sauts / réceptions
- secousses fortes
- mouvements réalistes proches de l'usage cible

### But
Réduire les faux positifs en apprenant mieux au modèle la différence entre :
- une vraie chute
- un mouvement très dynamique mais non dangereux

### Résultats observés
- Accuracy : **62,3%**
- AUC : **0,57**
- Rappel `fall` : **42,7%**
- Rappel `not_fall` : **71,0%**
- F1 `fall` : **0,41**
- F1 `not_fall` : **0,72**

### Interprétation
L'ajout de `not_fall` difficiles change fortement le biais du modèle :
- il reconnaît mieux les `not_fall`
- il réduit les faux positifs
- mais il rate beaucoup plus de vraies chutes

### Conclusion V5
Le levier est réel, mais le compromis est mauvais dans cette version :
- V5 apprend au modèle à être plus prudent avant de prédire `fall`
- mais cela dégrade trop le rappel sur les chutes

V5 n'est donc pas une meilleure version finale que V4, mais reste un test utile pour comprendre l'effet des `not_fall` difficiles.

---

## V6 — Recentrage correct des fenêtres de chute

### Hypothèse
Le problème principal n'était pas le modèle lui-même, mais le fait que les fenêtres `fall` n'étaient pas réellement centrées sur l'événement de chute.

### Principe
Pour chaque enregistrement de chute :
- calcul d'un score d'événement à partir de `a_norm` et `g_norm`
- repérage du pic principal
- construction de **3 fenêtres de 1 seconde / 50 points** par événement :
  - une fenêtre **parfaitement centrée** sur le pic
  - une fenêtre **décalée de -8 points**
  - une fenêtre **décalée de +8 points**

Ainsi :
- les fenêtres `fall` couvrent non seulement l'instant central de la chute
- mais aussi la transition juste avant et juste après l'événement
- les mouvements éloignés de la chute ne sont plus automatiquement étiquetés `fall`

Ce choix permet :
- d'augmenter le nombre de fenêtres `fall` utiles sans revenir à l'erreur initiale
- de donner au modèle une petite variabilité temporelle autour de la chute
- d'apprendre non seulement le pic, mais aussi sa dynamique locale

### Structure commune
- **1 seconde**
- **50 points**
- **8 canaux**
- 400 features capteurs par fenêtre

### Variantes testées

#### V6 brut
Dataset réaliste issu du recentrage :
- `fall` : **450**
- `not_fall` : **5393**
- ratio ≈ **1:12**

#### V6_2
Version partiellement rééquilibrée :
- `fall` : **450**
- `not_fall` : **900**
- ratio **1:2**

#### V6_3
Version partiellement rééquilibrée :
- `fall` : **450**
- `not_fall` : **1350**
- ratio **1:3**

### Résultats observés en float32

#### V6 brut
- Accuracy : **97,97%**
- AUC : **0,938**
- Précision `fall` : **82,6%**
- Rappel `fall` : **89,1%**
- F1 `fall` : **0,857**

#### V6_2
- Accuracy : **89,45%**
- AUC : **0,889**
- Précision `fall` : **85,5%**
- Rappel `fall` : **86,6%**
- F1 `fall` : **0,861**

#### V6_3
- Accuracy : **88,62%**
- AUC : **0,882**
- Précision `fall` : **77,1%**
- Rappel `fall` : **87,1%**
- F1 `fall` : **0,818**

### Résultats observés en int8

#### V6 brut
- Accuracy : **81,0%**
- AUC : **0,876**
- Précision `fall` : **25,8%**
- Rappel `fall` : **95,3%**
- F1 `fall` : **0,407**

#### V6_2
- Accuracy : **63,3%**
- AUC : **0,687**
- Précision `fall` : **50,7%**
- Rappel `fall` : **90,2%**
- F1 `fall` : **0,649**

#### V6_3
- Accuracy : **65,9%**
- AUC : **0,728**
- Précision `fall` : **45,8%**
- Rappel `fall` : **89,4%**
- F1 `fall` : **0,606**

### Interprétation
V6 change complètement la situation.

Le recentrage correct des fenêtres de chute fait fortement progresser le modèle :
- la séparation `fall / not_fall` devient enfin bonne en float32
- les rappels `fall` deviennent élevés
- les F1 `fall` deviennent élevés
- l'AUC monte fortement

Cela valide directement le diagnostic posé après V5 :
- le vrai verrou principal était le **mauvais héritage du label fichier vers les fenêtres**
- pas l'idée de classification en elle-même

### Lecture des variantes
- **V6_2** donne le meilleur compromis lisible et équilibré
- **V6_3** est un peu plus agressif sur `fall`
- **V6 brut** montre qu'un dataset réaliste très déséquilibré peut tout de même bien fonctionner en float32

### Point critique restant
La version **int8** est nettement moins bonne que la version float32.

Cela signifie que :
- le dataset est maintenant beaucoup plus propre
- mais la **quantification int8** devient le nouveau sujet important pour une cible embarquée

### Conclusion V6
V6 est la version qui valide la vraie cause du problème :
- la classification n'était pas le mauvais paradigme
- les features n'étaient pas le problème principal
- le vrai problème était le **découpage temporel et le bruit de label sur les chutes**


---

## V7 — Test du chevauchement autour du pic de chute

### Hypothèse
Après les très bons résultats de V6, une question restait ouverte :
- le choix de décalage **`-8 / 0 / +8`** autour du pic est-il vraiment le meilleur ?
- ou bien un chevauchement plus fort ou plus large autour du pic pourrait-il améliorer encore la robustesse ?

### Principe
V7 ne change pas :
- la taille de fenêtre (**1 seconde / 50 points**)
- le nombre de canaux (**8**)
- la logique générale de recentrage sur l'événement
- l'utilisation de **toutes les fenêtres `not_fall`** pour rester dans un cadre réaliste et simplifier la comparaison

Le seul levier testé est le **décalage temporel des 3 fenêtres `fall`** extraites autour du pic.

### Variantes testées

#### V6 brut de référence
- décalage : **`-8 / 0 / +8`**

#### V7_1
- décalage : **`-4 / 0 / +4`**
- objectif : tester un recouvrement plus fin et plus redondant autour du pic

#### V7_2
- décalage : **`-12 / 0 / +12`**
- objectif : tester une couverture plus large de la dynamique avant / après l'événement

### Résultats observés en float32

#### V6 brut (`-8 / 0 / +8`)
- Accuracy : **97,97%**
- AUC : **0,938**
- Précision `fall` : **82,6%**
- Rappel `fall` : **89,1%**
- F1 `fall` : **0,857**

#### V7_1 (`-4 / 0 / +4`)
- Accuracy : **97,64%**
- AUC : **0,916**
- Précision `fall` : **82,1%**
- Rappel `fall` : **84,6%**
- F1 `fall` : **0,833**

#### V7_2 (`-12 / 0 / +12`)
- Accuracy : **97,33%**
- AUC : **0,928**
- Précision `fall` : **76,7%**
- Rappel `fall` : **87,5%**
- F1 `fall` : **0,818**

### Résultats observés en int8

#### V7_1 (`-4 / 0 / +4`)
- Accuracy : **59,9%**
- AUC : **0,727**
- Précision `fall` : **13,4%**
- Rappel `fall` : **87,7%**
- F1 `fall` : **0,233**

#### V7_2 (`-12 / 0 / +12`)
- Accuracy : **55,4%**
- AUC : **0,717**
- Précision `fall` : **12,4%**
- Rappel `fall` : **90,6%**
- F1 `fall` : **0,218**

### Interprétation
Les deux variantes V7 sont bonnes en float32, mais aucune ne dépasse **V6 brut**.

Lecture des résultats :
- **`-4 / 0 / +4`** semble trop redondant : les fenêtres sont trop proches et apportent moins de diversité temporelle
- **`-12 / 0 / +12`** semble trop large : les fenêtres s'éloignent davantage de la zone la plus discriminante
- **`-8 / 0 / +8`** apparaît comme le meilleur compromis entre :
  - couverture de la dynamique de chute
  - diversité temporelle
  - concentration sur l'événement utile

### Conclusion V7
Le test de chevauchement confirme que :
- jouer sur le décalage autour du pic est une piste pertinente
- mais le réglage initial de V6, **`-8 / 0 / +8`**, était déjà le meilleur parmi les variantes testées

Cela permet de clore ce levier expérimental :
- le centrage et le décalage des fenêtres `fall` sont maintenant bien calibrés
- le prochain sujet important n'est plus le fenêtrage autour du pic
- le prochain vrai verrou reste la **quantification int8** et l'embarqué


---

## Statut final de V7 dans l'historique

Initialement, une V7 était envisagée comme combinaison :
- de fenêtres `fall` mieux centrées
- et d'un enrichissement en `not_fall` difficiles

Ensuite, une autre V7 a été utilisée pour tester le **chevauchement des fenêtres autour du pic**.

Au final :
- la comparaison V7 a été utile pour valider le choix du décalage
- mais elle n'a pas donné de meilleure version que **V6 brut**
- la configuration retenue pour la suite reste donc **V6 brut avec `-8 / 0 / +8`**

Autrement dit :
- **V7 existe comme test expérimental**
- mais **V6 brut reste la version de référence retenue**

---

## Résumé global des enseignements

### Ce qui a été appris
- Le pipeline Edge Impulse fonctionne.
- Le format tabulaire permet de lancer rapidement des expériences.
- Ajouter `g_norm` et `a_norm` aide un peu, mais ne suffit pas.
- Rééquilibrer les classes aide légèrement, sans résoudre le problème de fond.
- Réduire la fenêtre de 2 s à 1 s améliore la détection des chutes.
- Ajouter plus de `not_fall` difficiles réduit les faux positifs, mais peut faire chuter trop fortement le rappel `fall`.
- Le vrai verrou principal était la **mauvaise labellisation temporelle des chutes**.
- Recentrer correctement les fenêtres `fall` fait fortement progresser le modèle.
- Tester le chevauchement autour du pic montre que **`-8 / 0 / +8`** est le meilleur compromis parmi les variantes testées.

### Ce qui reste problématique
- Les performances int8 restent nettement inférieures aux performances float32.
- Il faut maintenant travailler la robustesse embarquée :
  - quantification
  - compromis précision / rappel
  - validation plus réaliste
  - future exportation sur cible

---

## Stratégie expérimentale réellement retenue

Ordre logique final :
1. **V1** : baseline simple
2. **V2** : ajout de features dérivées
3. **V3** : équilibrage des classes
4. **V4** : réduction de la taille de fenêtre
5. **V5** : ajout de `not_fall` difficiles
6. **V6** : recentrage correct des `fall`, avec variantes de ratio
7. **V7** : validation du chevauchement autour du pic

Cette stratégie a permis d'isoler progressivement :
- la représentation des signaux
- l'équilibre des classes
- la taille de fenêtre
- la difficulté des négatifs
- et surtout la qualité réelle du label `fall`

---

## Recommandation de suivi

Pour chaque future version, noter systématiquement :
- accuracy
- AUC
- précision `fall`
- rappel `fall`
- F1 `fall`
- rappel `not_fall`
- description exacte de la modification faite

À ce stade, la meilleure base de travail pour la suite est :
- **V6_2** si l'on veut un bon compromis propre
- **V6 brut** si l'on veut observer un comportement plus réaliste sur distribution naturelle
