#!/usr/bin/env python3

import csv
import random
from pathlib import Path

INPUT_CSV = Path("data/processed/exports/windows_temp.csv")
OUTPUT_CSV = Path("data/processed/exports/windows_V6_3.csv")

FALL_LABEL = "fall"
NOT_FALL_LABEL = "not_fall"
TARGET_RATIO = 3   # not_fall = 3 * fall
RANDOM_SEED = 53


def main() -> None:
    random.seed(RANDOM_SEED)

    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Fichier introuvable : {INPUT_CSV}")

    with INPUT_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        header = reader.fieldnames

    if not header:
        raise ValueError("En-tête CSV introuvable.")

    if "label" not in header:
        raise ValueError("Colonne 'label' introuvable dans le CSV.")

    fall_indices = [i for i, row in enumerate(rows) if row["label"] == FALL_LABEL]
    not_fall_indices = [i for i, row in enumerate(rows) if row["label"] == NOT_FALL_LABEL]

    nb_fall = len(fall_indices)
    nb_not_fall = len(not_fall_indices)

    print(f"Lignes '{FALL_LABEL}'     : {nb_fall}")
    print(f"Lignes '{NOT_FALL_LABEL}' : {nb_not_fall}")

    target_not_fall = TARGET_RATIO * nb_fall
    print(f"Objectif '{NOT_FALL_LABEL}' final : {target_not_fall}")

    if nb_not_fall < target_not_fall:
        raise ValueError(
            f"Impossible d'obtenir {TARGET_RATIO}x plus de '{NOT_FALL_LABEL}' que de '{FALL_LABEL}' "
            f"en supprimant seulement des '{NOT_FALL_LABEL}' : "
            f"disponibles={nb_not_fall}, nécessaires={target_not_fall}."
        )

    nb_to_remove = nb_not_fall - target_not_fall
    print(f"Lignes '{NOT_FALL_LABEL}' à supprimer : {nb_to_remove}")

    indices_to_remove = set(random.sample(not_fall_indices, nb_to_remove))
    kept_rows = [row for i, row in enumerate(rows) if i not in indices_to_remove]

    final_fall = sum(1 for row in kept_rows if row["label"] == FALL_LABEL)
    final_not_fall = sum(1 for row in kept_rows if row["label"] == NOT_FALL_LABEL)

    if final_not_fall != TARGET_RATIO * final_fall:
        raise ValueError(
            f"Équilibrage échoué : fall={final_fall}, not_fall={final_not_fall}, "
            f"ratio attendu={TARGET_RATIO}:1"
        )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(kept_rows)

    print(f"Fichier source       : {INPUT_CSV}")
    print(f"Fichier de sortie    : {OUTPUT_CSV}")
    print(f"Total final fall     : {final_fall}")
    print(f"Total final not_fall : {final_not_fall}")
    print(f"Ratio final          : {final_not_fall / final_fall:.2f}:1")
    print(f"Total final données  : {len(kept_rows)}")
    print(f"Total final lignes   : {len(kept_rows) + 1} (avec en-tête)")


if __name__ == "__main__":
    main()
