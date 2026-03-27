#!/usr/bin/env python3

from pathlib import Path

INPUT_ROOT = Path("data/processed/cleaned")
INPUT_LABEL_DIRS = ["not_fall", "fall"]

OUTPUT_FILE = Path("data/processed/exports/windows.csv")

LINE_STEP = 4
WINDOW_SIZE = 100


def build_header(window_size: int) -> list[str]:
    header = ["window_id", "source_file"]
    axes = ["gx", "gy", "gz", "ax", "ay", "az"]

    for i in range(window_size):
        for axis in axes:
            header.append(f"{axis}_{i}")

    header.append("label")
    return header


HEADER = build_header(WINDOW_SIZE)


def clean_line(line: str) -> str:
    return line.strip().rstrip(";")


def chunk_list(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        if len(chunk) == chunk_size:
            yield chunk


def parse_line(line: str) -> list[str]:
    values = [v.strip() for v in clean_line(line).split(",")]

    # Si une première valeur type timestamp est présente
    if len(values) == 7:
        values = values[1:]

    if len(values) != 6:
        raise ValueError(f"Ligne invalide, 6 valeurs utiles attendues : {line.strip()}")

    return values


def process_file(input_path: Path, label: str, output_handle, window_index_start: int) -> int:
    with input_path.open("r", encoding="utf-8") as f:
        raw_lines = [line for line in f if line.strip()]

    sampled_lines = raw_lines[::LINE_STEP]
    window_index = window_index_start

    for chunk in chunk_list(sampled_lines, WINDOW_SIZE):
        flattened_values = []

        for line in chunk:
            flattened_values.extend(parse_line(line))

        row = [f"window_{window_index}", input_path.name] + flattened_values + [label]
        output_handle.write(",".join(row) + "\n")
        window_index += 1

    return window_index


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    input_files: list[tuple[Path, str]] = []

    for label_dir in INPUT_LABEL_DIRS:
        folder = INPUT_ROOT / label_dir

        if not folder.exists():
            print(f"[INFO] Dossier absent : {folder}")
            continue

        files = sorted([f for f in folder.iterdir() if f.is_file()])
        for file in files:
            input_files.append((file, label_dir))

    if not input_files:
        print("Aucun fichier trouvé.")
        return

    window_index = 1

    with OUTPUT_FILE.open("w", encoding="utf-8") as out:
        out.write(",".join(HEADER) + "\n")

        for input_file, label in input_files:
            try:
                window_index = process_file(input_file, label, out, window_index)
                print(f"{input_file} -> label={label}")
            except ValueError as e:
                print(f"[ERREUR] {input_file.name}: {e}")

    print(f"Dataset généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
