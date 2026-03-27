# Prétraitement simple et transmission des données

## Objectif
Mettre en place un pipeline minimal et propre pour préparer la création du dataset.

Cette semaine ne consiste pas à faire du traitement avancé.  
Elle consiste à transformer la lecture brute de l’IMU en un flux de données :

- régulier,
- propre,
- lisible,
- réutilisable sur PC.

Les deux objectifs sont :

1. mettre en place un prétraitement simple,
2. stocker ou transmettre les données.

---

## Décisions retenues pour le projet

### Carte
Arduino Nano 33 BLE Rev2

### Capteurs utilisés
- accéléromètre 3 axes
- gyroscope 3 axes

### Capteur non utilisé pour la V1
- magnétomètre

### Signaux retenus
- `ax`
- `ay`
- `az`
- `gx`
- `gy`
- `gz`

### Unités
- accéléromètre : `g`
- gyroscope : `dps`

### Fréquence cible
- objectif initial : `50 Hz`
- soit un pas théorique de `20 ms`

### Format de transmission
- texte
- une ligne par échantillon
- format CSV

### Choix stockage / transmission
- **transmission série vers PC**
- pas de stockage local sur la carte pour la V1

---

## Prétraitement simple retenu

Le prétraitement retenu reste volontairement minimal.

### Il comprend
- sélection des 6 axes utiles
- cadence d’échantillonnage définie
- format de sortie stable
- ordre de colonnes figé

### Il ne comprend pas encore
- filtrage complexe
- fusion de capteurs
- compensation avancée de la gravité
- orientation 3D
- extraction de features ML

L’objectif n’est pas encore d’optimiser le modèle.  
L’objectif est d’obtenir un flux exploitable pour constituer un dataset cohérent.

---

## Format CSV retenu

### En-tête
Le flux commence par une ligne d’en-tête unique.

### Colonnes
- `time_ms`
- `ax`
- `ay`
- `az`
- `gx`
- `gy`
- `gz`

### Exemple de structure attendue

```text
time_ms,ax,ay,az,gx,gy,gz
0,0.01,-0.02,0.99,0.10,-0.05,0.02
20,0.02,-0.01,1.00,0.12,-0.03,0.01
40,0.01,-0.02,0.98,0.15,-0.02,0.00
