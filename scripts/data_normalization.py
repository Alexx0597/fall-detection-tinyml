#!/usr/bin/env python3

from pathlib import Path

INPUT_DIR = Path("data/processed/cleaned/fall/not_normalized")
OUTPUT_DIR = Path("data/processed/cleaned/fall")

OUTPUT_PREFIX = "scaled_"
OUTPUT_EXT = ".txt"

FACTOR_FIRST_3 = (2 * 2000) / (2 ** 16)
FACTOR_LAST_3 = (2 * 8) / (2 ** 14)


def transform_line(line: str) -> str:
    line = line.strip()

    if not line:
        return ""

    # retire le ';' final s'il existe
    if line.endswith(";"):
        line = line[:-1]

    # découpe + suppression des espaces autour
    values = [v.strip() for v in line.split(",")]

    # on attend exactement 6 valeurs
    if len(values) != 6:
        raise ValueError(f"Ligne invalide, 6 valeurs attendues : {line}")

    nums = [float(v) for v in values]

    result = []

    # 3 premières valeurs
    for v in nums[:3]:
        result.append(round(FACTOR_FIRST_3 * v, 4))

    # 3 dernières valeurs
    for v in nums[3:]:
        result.append(round(FACTOR_LAST_3 * v, 4))

    return ",".join(f"{v:.4f}" for v in result) + ";\n"


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
