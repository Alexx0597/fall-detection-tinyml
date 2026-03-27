# Fall Detection TinyML

Prototype de détection de chute embarquée sur microcontrôleur.

## Objectif
Développer un démonstrateur TinyML capable de détecter une chute à partir de données inertielle (accéléromètre + gyroscope), avec exécution locale sur microcontrôleur.

## Cible matérielle
- Arduino Nano 33 BLE Rev2
- Évolution prévue : STM32F411

## Environnement de développement
- Fedora KDE 43
- VS Code
- PlatformIO
- Git
- Python 3

## Structure du projet
- `firmware/` : code embarqué
- `data/` : données brutes et préparées
- `scripts/` : scripts Python de traitement
- `docs/` : documentation technique
- `results/` : résultats et mesures

## Feuille de route
1. Lecture des données IMU
2. Acquisition et création d’un dataset
3. Prétraitement simple
4. Entraînement d’un premier modèle
5. Export embarqué
6. Inférence temps réel sur cible
7. Mesures mémoire / latence
8. Portage vers STM32F411

## Statut
Projet en cours de mise en place.
