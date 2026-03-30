#!/usr/bin/env python3

from pathlib import Path
import csv

INPUT_ROOT = Path("data/processed/cleaned/with_norms")
NOT_FALL_DIR = INPUT_ROOT / "not_fall"
FALL_PREBUILT_FILE = INPUT_ROOT / "fall" / "fall_centered_windows72.txt"

OUTPUT_FILE = Path("data/processed/exports/windows_temp.csv")

GROUP_SIZE = 4
WINDOW_SIZE = 50


def build_header(window_size: int) -> list[str]:
    header = ["window_id", "source_file"]
    axes = ["gx", "gy", "gz", "ax", "ay", "az", "g_norm", "a_norm"]

    for i in range(window_size):
        for axis in axes:
            header.append(f"{axis}_{i}")

    header.append("label")
    return header


HEADER = build_header(WINDOW_SIZE)


def clean_line(line: str) -> str:
    return line.strip().rstrip(";")


def chunk_list_keep_remainder(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def chunk_list_full_only(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        if len(chunk) == chunk_size:
            yield chunk


def parse_line(line: str) -> list[float]:
    values = [v.strip() for v in clean_line(line).split(",")]

    # Si une première valeur type timestamp est présente
    if len(values) == 9:
        values = values[1:]

    if len(values) != 8:
        raise ValueError(f"Ligne invalide, 8 valeurs utiles attendues : {line.strip()}")

    return [float(v) for v in values]


def average_group(lines: list[str]) -> list[str]:
    parsed = [parse_line(line) for line in lines]

    nb_cols = len(parsed[0])
    averaged = []

    for col_idx in range(nb_cols):
        col_mean = sum(row[col_idx] for row in parsed) / len(parsed)
        averaged.append(f"{col_mean:.4f}")

    return averaged


def process_not_fall_file(input_path: Path, output_handle, window_index_start: int) -> int:
    with input_path.open("r", encoding="utf-8") as f:
        raw_lines = [line for line in f if line.strip()]

    averaged_lines = [average_group(group) for group in chunk_list_keep_remainder(raw_lines, GROUP_SIZE)]

    window_index = window_index_start

    for chunk in chunk_list_full_only(averaged_lines, WINDOW_SIZE):
        flattened_values = []

        for averaged_line in chunk:
            flattened_values.extend(averaged_line)

        row = [f"window_{window_index}", input_path.name] + flattened_values + ["not_fall"]
        output_handle.write(",".join(row) + "\n")
        window_index += 1

    return window_index


def copy_fall_dataset_file(input_path: Path, output_handle, window_index_start: int) -> int:
    if not input_path.exists():
        print(f"[INFO] Fichier absent : {input_path}")
        return window_index_start

    with input_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print(f"[INFO] Fichier vide : {input_path}")
        return window_index_start

    expected_len = len(HEADER)

    # Détecte et saute l'en-tête si présent
    start_idx = 1 if rows[0] and rows[0][0] == "window_id" else 0

    window_index = window_index_start

    for row in rows[start_idx:]:
        if not row:
            continue

        if len(row) != expected_len:
            raise ValueError(
                f"Ligne invalide dans {input_path.name} : {len(row)} colonnes au lieu de {expected_len}"
            )

        # Réindexe le window_id pour garder une numérotation continue
        row[0] = f"window_{window_index}"

        # Force le label à fall, par sécurité
        row[-1] = "fall"

        output_handle.write(",".join(row) + "\n")
        window_index += 1

    return window_index


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    not_fall_files = []

    if NOT_FALL_DIR.exists():
        not_fall_files = sorted([f for f in NOT_FALL_DIR.iterdir() if f.is_file()])
    else:
        print(f"[INFO] Dossier absent : {NOT_FALL_DIR}")

    window_index = 1

    with OUTPUT_FILE.open("w", encoding="utf-8") as out:
        out.write(",".join(HEADER) + "\n")

        # 1. Génère les fenêtres not_fall depuis les fichiers bruts
        for input_file in not_fall_files:
            try:
                window_index = process_not_fall_file(input_file, out, window_index)
                print(f"{input_file} -> label=not_fall")
            except ValueError as e:
                print(f"[ERREUR] {input_file.name}: {e}")

        # 2. Copie directement les fenêtres fall déjà générées
        try:
            window_index = copy_fall_dataset_file(FALL_PREBUILT_FILE, out, window_index)
            print(f"{FALL_PREBUILT_FILE} -> label=fall (copie directe)")
        except ValueError as e:
            print(f"[ERREUR] {FALL_PREBUILT_FILE.name}: {e}")

    print(f"Dataset généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
