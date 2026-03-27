# Création du premier dataset exploitable et vérification de la qualité des données

## Objectif

1. créer un premier dataset exploitable pour l’apprentissage,
2. vérifier la qualité des données avant de passer à l’entraînement.

Dans le cadre du projet de détection de chute, cette étape marque le passage entre :

- la mise en place de la chaîne technique,
- et la constitution d’une base de données réellement utilisable pour un premier modèle.

---

## Objectif du dataset V1

Le dataset V1 est basé sur une partie du dataset SisFall et  a été conçu pour entraîner un premier modèle de classification binaire :

- `fall`
- `not_fall`

L’objectif n’est pas encore de couvrir tous les cas réels possibles, mais de disposer d’un dataset :

- cohérent,
- propre,
- structuré,
- suffisant pour une première itération de modèle.

---

## Structure générale des données

L’organisation retenue dans le projet est la suivante :

```text
data/
├── raw/
│   ├── fall/
│   └── not_fall/
├── processed/
│   ├── cleaned/
│   ├── windows/
│   └── exports/
└── samples/
