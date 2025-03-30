import os
import subprocess
import sys
from typing import Optional
from src.d01_data.read_files import *

import pandas as pd

try:
    from scapy.all import rdpcap, wrpcap
except ImportError:
    print('scapy Packet wird installiert')
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scapy"])
    from scapy.all import rdpcap, wrpcap
from src.config import *


# outdated
def merge_pcap_files(pcap_directory: str, pcap_output_path: str, is_server: bool = True):
    source_directory: str
    output_path: str

    if is_server:
        source_directory = f'{path_server_data}/{pcap_directory}'
        print('SEVER'+ source_directory)
        output_path = f'{path_server_data}/{pcap_output_path}/big_pcap.pcap'
    else:
        source_directory = f'{path_data_raw}/{pcap_directory}'
        output_path = f'{path_data_raw}/{pcap_output_path}/big_pcap.pcap'

    source_directory = f'{path_root}/Cloud-Telescope/data/raw/merge_pcap_test'
    output_path = f'{path_root}/Cloud-Telescope/data/raw/merge_pcap_test/big_pcap.pcap'

    files = [os.path.join(source_directory, f) for f in os.listdir(source_directory) if f.endswith('.pcap')]

    if not files:
        print("Keine .pcap-Dateien im angegebenen Verzeichnis gefunden.")
        return

    all_packets = []

    for file in files:
        print(f"Verarbeite {file}...")
        packets = rdpcap(file)
        all_packets.extend(packets)

    wrpcap(output_path, all_packets)
    print(f"Die Dateien wurden erfolgreich zu {output_path} zusammengeführt.")


def convert_json_to_csv(folder_path_from_server_data: str):
    absolut_folder_path: str = f'{path_server_data}{folder_path_from_server_data}'
    chunk_size = 1000000

    files: list[str] = os.listdir(absolut_folder_path)
    for file in files:
        current_chunk: int = 0
        if file.endswith('.json'):
            print(f'working on file {file}')
            new_file: str = f'{file.split(".")[0]}.csv'
            absolut_new_file_path: str = f'{absolut_folder_path}/{new_file}'
            absolut_file_path: str = f'{absolut_folder_path}/{file}'

            print(f'absolut_file_path: {absolut_file_path}')
            print(f'absolut_new_file_path: {absolut_new_file_path}')

            first_chunk = next(pd.read_json(absolut_file_path, lines=True, chunksize=chunk_size))
            first_chunk.to_csv(absolut_new_file_path, mode='w', header=True, index=False)
            print('Header geschrieben')

            for chunk in pd.read_json(absolut_file_path, lines=True, chunksize=chunk_size):
                chunk.to_csv(absolut_new_file_path, mode='a', header=False, index=False)
                print(f'Chunk: {current_chunk}')
                current_chunk += current_chunk

            print(f'finished working on file {file}')
    print(f'finished script')



