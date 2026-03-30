#!/usr/bin/env python3

from pathlib import Path
from math import sqrt

INPUT_DIR = Path("data/processed/cleaned/fall")
OUTPUT_DIR = Path("data/processed/cleaned/with_norms/fall")

OUTPUT_PREFIX = "norm_"
OUTPUT_EXT = ".txt"


def clean_line(line: str) -> str:
    return line.strip().rstrip(";")


def transform_line(line: str) -> str:
    values = [v.strip() for v in clean_line(line).split(",")]

    # Si une première valeur type timestamp est encore présente
    if len(values) == 7:
        values = values[1:]

    if len(values) != 6:
        raise ValueError(f"Ligne invalide, 6 valeurs attendues : {line.strip()}")

    gx, gy, gz, ax, ay, az = map(float, values)

    gyro_norm = sqrt(gx**2 + gy**2 + gz**2)
    accel_norm = sqrt(ax**2 + ay**2 + az**2)

    return (
        f"{gx:.4f},{gy:.4f},{gz:.4f},"
        f"{ax:.4f},{ay:.4f},{az:.4f},"
        f"{gyro_norm:.4f},{accel_norm:.4f};\n"
    )


def process_file(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line_number, line in enumerate(fin, start=1):
            if not line.strip():
                continue
            try:
                fout.write(transform_line(line))
            except ValueError as e:
                print(f"[ERREUR] {input_path.name} ligne {line_number}: {e}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted([f for f in INPUT_DIR.iterdir() if f.is_file()])

    if not files:
        print(f"Aucun fichier trouvé dans {INPUT_DIR}")
        return

    for index, input_file in enumerate(files, start=1):
        output_file = OUTPUT_DIR / f"{OUTPUT_PREFIX}{index:03d}{OUTPUT_EXT}"
        process_file(input_file, output_file)
        print(f"{input_file.name} -> {output_file.name}")


if __name__ == "__main__":
    main()
