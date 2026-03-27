#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys
import time

import serial
from serial import SerialException


def make_output_path(output_dir: pathlib.Path) -> pathlib.Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / f"imu_capture_session_{timestamp}.csv"


def open_serial(port: str, baudrate: int, timeout: float) -> serial.Serial:
    return serial.Serial(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture un flux série Arduino dans un fichier CSV."
    )
    parser.add_argument(
        "--port",
        default="/dev/ttyACM0",
        help="Port série à ouvrir (défaut: /dev/ttyACM0)",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=115200,
        help="Baudrate du port série (défaut: 115200)",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Dossier de sortie (défaut: data/raw)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Timeout de lecture série en secondes (défaut: 1.0)",
    )
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    output_path = make_output_path(output_dir)

    print(f"[INFO] Fichier de sortie : {output_path}")
    print(f"[INFO] Port : {args.port} | Baudrate : {args.baudrate}")
    print("[INFO] Ctrl+C pour arrêter.\n")

    first_connection = True

    with output_path.open("a", encoding="utf-8", newline="\n") as f:
        while True:
            try:
                print(f"[INFO] Tentative de connexion à {args.port}...")
                with open_serial(args.port, args.baudrate, args.timeout) as ser:
                    print("[INFO] Port série connecté.")

                    # Optionnel: laisse le temps à la carte de stabiliser sa sortie
                    time.sleep(0.5)

                    while True:
                        raw = ser.readline()

                        if not raw:
                            continue

                        try:
                            line = raw.decode("utf-8", errors="replace")
                        except Exception:
                            continue

                        # Normalisation des fins de ligne
                        line = line.replace("\r", "").strip("\n")

                        if not line:
                            continue

                        # Évite d'écrire plusieurs fois l'en-tête si la carte reboot
                        if (
                            not first_connection
                            and line.strip() == "time_ms,ax,ay,az,gx,gy,gz"
                        ):
                            print("[INFO] En-tête détecté après reconnexion, ignoré.")
                            continue

                        print(line)
                        f.write(line + "\n")
                        f.flush()

                    first_connection = False

            except KeyboardInterrupt:
                print("\n[INFO] Capture arrêtée par l'utilisateur.")
                return 0

            except SerialException as e:
                print(f"[WARN] Port indisponible ou déconnecté : {e}")
                print("[INFO] Nouvelle tentative dans 1 seconde...\n")
                first_connection = False
                time.sleep(1.0)

            except OSError as e:
                print(f"[WARN] Erreur système sur le port série : {e}")
                print("[INFO] Nouvelle tentative dans 1 seconde...\n")
                first_connection = False
                time.sleep(1.0)


if __name__ == "__main__":
    sys.exit(main())
