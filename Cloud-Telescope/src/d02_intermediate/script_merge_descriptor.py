import os
import json
import pandas as pd
import argparse
from src.config import *


def extract_data_from_descriptors(run_folder: str, out_folder: str):

    folder_path: str = f'{path_root}{run_folder}'
    output_path: str = f'{path_root}{out_folder}'

    data = []

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if file.startswith("descriptor-"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    descriptor_data = json.load(f)

                    row = {
                        "ipv4": descriptor_data.get("ipv4"),
                        "creation": descriptor_data.get("creation"),
                        "region": descriptor_data.get("region"),
                        "deletion": descriptor_data.get("deletion")
                    }
                    data.append(row)
            except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
                print(f"Fehler beim Verarbeiten von {file_path}: {e}")

    df = pd.DataFrame(data, columns=["ipv4", "creation", "region", "deletion"])

    df.to_csv(f'{output_path}/descriptor.csv', index=False)
    print("CSV-Datei gespeichert: output.csv")


