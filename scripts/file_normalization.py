from pathlib import Path

# Dossiers
INPUT_DIR = Path("data/raw/fall")
OUTPUT_DIR = Path("data/processed/cleaned/fall/not_normalized")

# Préfixe des fichiers de sortie
OUTPUT_PREFIX = "data_"
OUTPUT_EXT = ".txt"


def transform_line(line: str) -> str:
    # Supprime les 2 premiers espaces si présents
    if line.startswith("  "):
        line = line[2:]

    # Retire retour ligne + ';' final
    line = line.rstrip("\n").rstrip().rstrip(";")

    # Découpe et nettoie les espaces autour des valeurs
    values = [v.strip() for v in line.split(",")]

    # Supprime les 3 premières valeurs
    if len(values) > 3:
        values = values[3:]
    else:
        values = []

    return ",".join(values) + ";\n"


def process_file(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            if line.strip():  # ignore les lignes vides
                fout.write(transform_line(line))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Récupère tous les fichiers du dossier d'entrée
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
