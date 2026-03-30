#!/usr/bin/env python3

from pathlib import Path
from math import sqrt
import csv

INPUT_DIR = Path("data/processed/cleaned/with_norms/fall")
OUTPUT_CSV = Path("data/processed/cleaned/with_norms/fall/fall_centered_windows72.txt")

WINDOW_SIZE = 50
HALF_WINDOW = WINDOW_SIZE // 2

# 3 fenêtres :
# 0   = centrée sur le pic
# -8  = un peu avant
# +8  = un peu après
OFFSETS = [-12, 0, 12]


def clean_line(line: str) -> str:
    return line.strip().rstrip(";")


def parse_line(line: str) -> list[float]:
    values = [v.strip() for v in clean_line(line).split(",")]

    # Cas avec timestamp au début
    if len(values) == 9:
        values = values[1:]

    # Cas sans g_norm / a_norm
    if len(values) == 6:
        gx, gy, gz, ax, ay, az = map(float, values)
        g_norm = sqrt(gx**2 + gy**2 + gz**2)
        a_norm = sqrt(ax**2 + ay**2 + az**2)
        return [gx, gy, gz, ax, ay, az, g_norm, a_norm]

    # Cas avec g_norm / a_norm déjà présents
    if len(values) == 8:
        return [float(v) for v in values]

    raise ValueError(f"Ligne invalide, 6 ou 8 valeurs attendues : {line.strip()}")


def zscore(values: list[float]) -> list[float]:
    n = len(values)
    if n == 0:
        return []

    mean = sum(values) / n
    var = sum((x - mean) ** 2 for x in values) / n
    std = var ** 0.5

    if std == 0:
        return [0.0 for _ in values]

    return [(x - mean) / std for x in values]


def build_header(window_size: int) -> list[str]:
    header = ["window_id", "source_file"]
    axes = ["gx", "gy", "gz", "ax", "ay", "az", "g_norm", "a_norm"]

    for i in range(window_size):
        for axis in axes:
            header.append(f"{axis}_{i}")

    header.append("label")
    return header


def compute_score(rows: list[list[float]]) -> list[float]:
    g_norm = [row[6] for row in rows]
    a_norm = [row[7] for row in rows]

    z_a = zscore(a_norm)
    z_g = zscore(g_norm)

    return [za + 0.5 * zg for za, zg in zip(z_a, z_g)]


def extract_window(rows: list[list[float]], center_idx: int) -> list[list[float]] | None:
    start = center_idx - HALF_WINDOW
    end = start + WINDOW_SIZE

    if start < 0 or end > len(rows):
        return None

    return rows[start:end]


def flatten_window(window: list[list[float]]) -> list[str]:
    flattened = []
    for sample in window:
        flattened.extend(f"{v:.4f}" for v in sample)
    return flattened


def process_file(input_path: Path, window_index_start: int) -> tuple[list[list[str]], int]:
    with input_path.open("r", encoding="utf-8") as f:
        rows = [parse_line(line) for line in f if line.strip()]

    if len(rows) < WINDOW_SIZE:
        print(f"[IGNORÉ] {input_path.name}: fichier trop court ({len(rows)} lignes)")
        return [], window_index_start

    score = compute_score(rows)
    idx_peak = max(range(len(score)), key=lambda i: score[i])

    result_rows = []
    window_index = window_index_start

    for offset in OFFSETS:
        center = idx_peak + offset
        window = extract_window(rows, center)

        if window is None:
            print(
                f"[IGNORÉ] {input_path.name}: fenêtre offset {offset} hors bornes "
                f"(peak={idx_peak}, center={center}, len={len(rows)})"
            )
            continue

        flattened = flatten_window(window)

        row = [
            f"window_{window_index}",
            input_path.name,
            *flattened,
            "fall",
        ]
        result_rows.append(row)
        window_index += 1

    return result_rows, window_index


def main() -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    files = sorted([f for f in INPUT_DIR.iterdir() if f.is_file()])

    if not files:
        print(f"Aucun fichier trouvé dans {INPUT_DIR}")
        return

    header = build_header(WINDOW_SIZE)
    total_written = 0
    total_files = 0

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        window_index = 1

        for input_file in files:
            total_files += 1
            try:
                rows_to_write, window_index = process_file(input_file, window_index)

                for row in rows_to_write:
                    writer.writerow(row)
                    total_written += 1

                print(f"[OK] {input_file.name}: {len(rows_to_write)} fenêtre(s) écrite(s)")

            except ValueError as e:
                print(f"[ERREUR] {input_file.name}: {e}")

    print(f"Fichier écrit : {OUTPUT_CSV}")
    print(f"Fichiers traités : {total_files}")
    print(f"Fenêtres écrites : {total_written}")


if __name__ == "__main__":
    main()
