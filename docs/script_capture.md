# Script de capture série IMU

## Objectif

Ce script permet d’enregistrer le flux CSV envoyé par l’Arduino Nano 33 BLE Rev2 vers un fichier `.csv` côté PC.

Il remplace avantageusement une simple commande `cat` car il gère mieux :

- l’écriture dans un fichier daté,
- l’affichage en direct dans le terminal,
- la suppression des lignes vides,
- la normalisation des fins de ligne,
- la reconnexion automatique si la carte reset ou si le port disparaît.

---

## Contexte

La carte Arduino n’écrit pas directement un fichier CSV.

Elle envoie un **flux texte au format CSV** sur le port série USB.

Le PC agit alors comme :

- récepteur,
- afficheur,
- enregistreur du fichier `.csv`.

Le rôle du script est donc de :

1. ouvrir le port série,
2. lire chaque ligne transmise,
3. nettoyer le flux,
4. sauvegarder le tout dans un fichier exploitable.

---

## Dépendance nécessaire

Le script utilise la bibliothèque Python `pyserial`.

### Installation simple

```bash
pip install pyserial
