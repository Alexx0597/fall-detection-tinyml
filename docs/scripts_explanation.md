# Explication des scripts du projet

Ce document résume le rôle et le fonctionnement des principaux scripts utilisés pour préparer le dataset de détection de chute.

---

## 1. Script d’extraction des fenêtres `fall` centrées sur le pic

### But
Créer automatiquement des fenêtres `fall` à partir des fichiers de chute bruts, en centrant les fenêtres sur le moment le plus probable de la chute. Le script lit les fichiers du dossier `data/processed/cleaned/with_norms/fall` et écrit un fichier texte au format CSV nommé `fall_centered_windows72.txt`. 

### Entrée
Chaque ligne d’un fichier source contient soit :
- `gx, gy, gz, ax, ay, az`
- soit `gx, gy, gz, ax, ay, az, g_norm, a_norm`

Le script accepte aussi un timestamp initial éventuel, qu’il ignore automatiquement.

### Fonctionnement
1. **Lecture et parsing**
   - `parse_line()` nettoie la ligne.
   - S’il y a 6 valeurs, il recalcule `g_norm` et `a_norm`.
   - S’il y a 8 valeurs, il les garde telles quelles.

2. **Calcul du score d’événement**
   - `compute_score()` calcule :
     - `zscore(a_norm)`
     - `zscore(g_norm)`
   - puis combine les deux avec :
     - `score = zscore(a_norm) + 0.5 * zscore(g_norm)`

3. **Détection du pic**
   - Le pic est défini par l’indice du score maximal.

4. **Création de plusieurs fenêtres**
   - Fenêtre taille `50`
   - Offsets utilisés : `[-12, 0, 12]`
   - Cela produit jusqu’à 3 fenêtres par fichier :
     - une un peu avant le pic
     - une centrée sur le pic
     - une un peu après le pic

5. **Export**
   - Le script écrit les fenêtres dans un fichier `.txt` mais au format CSV.
   - Le header contient :
     - `window_id`
     - `source_file`
     - toutes les colonnes `gx_0 ... a_norm_49`
     - `label` fixé à `fall`

### Fonctions principales
- `parse_line()`
- `zscore()`
- `compute_score()`
- `extract_window()`
- `flatten_window()`
- `process_file()`
- `main()`

---

## 2. Script de création du dataset global

### But
Construire un dataset final combinant :
- des fenêtres `not_fall` générées à partir de fichiers bruts
- des fenêtres `fall` déjà préparées dans un seul fichier texte de type CSV (`fall_centered_windows61.txt`)

### Entrées
- Dossier `data/processed/cleaned/with_norms/not_fall`
- Fichier `data/processed/cleaned/with_norms/fall/fall_centered_windows61.txt`

### Fonctionnement pour `not_fall`
1. **Lecture des fichiers bruts**
   - Le script parcourt tous les fichiers de `not_fall`.

2. **Découpage par groupes de 4 lignes**
   - `chunk_list_keep_remainder()` garde aussi le dernier groupe incomplet.

3. **Calcul de la moyenne**
   - `average_group()` calcule la moyenne colonne par colonne sur chaque groupe.
   - Exemple :
     - 4 lignes -> 1 ligne moyenne.

4. **Création des fenêtres**
   - Les lignes moyennées sont ensuite découpées en fenêtres complètes de taille `50`.
   - Les fenêtres incomplètes sont ignorées via `chunk_list_full_only()`.

5. **Ajout au dataset**
   - Chaque fenêtre `not_fall` devient une ligne dans le CSV de sortie avec le label `not_fall`.

### Fonctionnement pour `fall`
1. Le script ne relit pas tous les fichiers du dossier `fall`.
2. Il ouvre directement `fall_centered_windows61.txt`.
3. Il saute l’en-tête si présent.
4. Il recopie chaque ligne dans le dataset final.
5. Il renumérote `window_id` pour garder une suite continue.
6. Il force le label à `fall`.

### Fonctions principales
- `build_header()`
- `parse_line()`
- `average_group()`
- `process_not_fall_file()`
- `copy_fall_dataset_file()`
- `main()`

### Résultat
Le script écrit un dataset final `windows_temp.csv` contenant :
- les fenêtres `not_fall` générées par moyenne + fenêtrage
- les fenêtres `fall` copiées depuis un fichier déjà préparé

---

## 3. Script d’équilibrage du dataset

### But
Réduire aléatoirement le nombre de lignes `not_fall` pour obtenir un ratio voulu par rapport aux lignes `fall`.

Dans la version actuelle, le ratio cible est :
- `not_fall = 2 * fall`

### Entrée / sortie
- Entrée : `windows_temp.csv`
- Sortie : `windows_V6_2.csv`

### Fonctionnement
1. **Lecture du CSV**
   - Le script lit toutes les lignes avec `csv.DictReader`.

2. **Comptage des labels**
   - Il compte :
     - nombre de `fall`
     - nombre de `not_fall`

3. **Calcul de la cible**
   - `target_not_fall = 2 * nb_fall`

4. **Calcul du nombre à supprimer**
   - `nb_to_remove = nb_not_fall - target_not_fall`

5. **Suppression aléatoire**
   - Il choisit aléatoirement les lignes `not_fall` à supprimer.
   - La graine aléatoire est fixée (`RANDOM_SEED = 42`) pour un résultat reproductible.

6. **Vérification finale**
   - Le script vérifie que :
     - `final_not_fall == 2 * final_fall`

7. **Écriture**
   - Le CSV équilibré est sauvegardé.

### Fonctions principales
- `main()` uniquement, avec toute la logique dedans.

---

## Pipeline complet

L’enchaînement logique est :

1. **Préparer les fichiers bruts**
   - éventuellement ajout de `g_norm` et `a_norm`

2. **Créer les fenêtres `fall`**
   - avec le script centré sur le pic
   - sortie : `fall_centered_windows72.txt` ou variante équivalente

3. **Créer le dataset global**
   - `not_fall` : moyenne sur groupes de 4 puis fenêtres de 50
   - `fall` : copie du fichier préconstruit `fall_centered_windows61.txt`

4. **Équilibrer le dataset**
   - suppression aléatoire de `not_fall`
   - objectif : `2 × not_fall` par rapport à `fall`

---

## Résumé simple

- **Script 1** : détecte le pic de chute et crée les fenêtres `fall`
- **Script 2** : construit le dataset final
- **Script 3** : ajuste la proportion entre `fall` et `not_fall`
