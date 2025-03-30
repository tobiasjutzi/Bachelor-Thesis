from __future__ import annotations

import os
import subprocess
import argparse


def scanner_zeek(path_udp_script: str, path_log_folder: str, path_zeek_config_disable_logs: str, path_pcap_file: str):

    interval: int = 1
    max_interval: int = 20

    threshold: float = 4.0
    max_threshold: float = 100.0

    while interval <= max_interval:

        # set interval
        addr_scan_interval: str = f'        const addr_scan_interval = {interval}min &redef;'
        port_scan_interval: str = f'        const port_scan_interval = {interval}min &redef;'
        try:
            subprocess.run(["sed", "-i", "33d", path_udp_script], cwd=path_log_folder, check=True)
            subprocess.run(["sed", "-i", f"33i\\{addr_scan_interval}", path_udp_script], cwd=path_log_folder, check=True)

            subprocess.run(["sed", "-i", "42d", path_udp_script], cwd=path_log_folder, check=True)
            subprocess.run(["sed", "-i", f"42i\\{port_scan_interval}", path_udp_script], cwd=path_log_folder, check=True)
            print(f'interval is set to {interval}')

        except subprocess.CalledProcessError as e_interval:
            print(f'Error setting interval: {interval} - {e_interval}')
            interval = interval + 1
            break

        while threshold <= max_threshold:

            # set threshold
            addr_scan_threshold: str = f'        const addr_scan_threshold = {threshold} &redef;'
            port_scan_threshold: str = f'        const port_scan_threshold = {threshold} &redef;'

            try:
                subprocess.run(["sed", "-i", "37d", path_udp_script], cwd=path_log_folder, check=True)
                subprocess.run(["sed", "-i", f"37i\\{addr_scan_threshold}", path_udp_script], cwd=path_log_folder,
                               check=True)

                subprocess.run(["sed", "-i", "46d", path_udp_script], cwd=path_log_folder, check=True)
                subprocess.run(["sed", "-i", f"46i\\{port_scan_threshold}", path_udp_script], cwd=path_log_folder,
                               check=True)
                print(f'threshold is set to {threshold}')

            except subprocess.CalledProcessError as e_threshold:
                print(f'Error while setting threshold: {threshold} - {e_threshold}')
                threshold = threshold + 2.0
                break

            # create output folder
            folder_name: str = f'zeek_scan_addr-{threshold}_{interval}min_p-{threshold}_{interval}min'
            folder_path: str = f'{path_log_folder}/{folder_name}'
            try:
                os.makedirs(folder_path)
                print(f'Folder was created successfully: {folder_path}')
            except PermissionError as e:
                print(f'Error while creating output folder: {e}')
                break
            except OSError as e:
                print(f'Error while creating output folder: {e}')
                threshold = threshold + 2.0
                break

            # run zeek
            zeek_command: str = f'zeek -C {path_zeek_config_disable_logs} {path_udp_script} -r {path_pcap_file}'

            try:
                subprocess.run(zeek_command, shell=True, cwd=f'{folder_path}', check=True)
                print(f'Zeek run successfully for interval: {interval} and threshold: {threshold}')

            except subprocess.CalledProcessError as e:
                print(f'Error while merging .pcap files: {e}')
                threshold = threshold + 2.0
                break

            threshold = threshold + 2.0

        # reset threshold
        threshold = 4.0

        interval = interval + 1


parser = argparse.ArgumentParser(description='Script to merge mmdb infos to IP List')
parser.add_argument(
    'path_udp_script',
    type=str,
    help='absolut path to udp scan detection script',
    default='/home/tobias/work/Cloud-Telescope/shell/config/custom_scripts/scan_detection_upd_for_scanner_script.zeek'
)

parser.add_argument(
    'path_log_folder',
    type=str,
    help='absolut path to folder in which zeek logs will created',
    default='/home/tobias/work/Cloud-Telescope/data/raw/cloud_merged_pcap/zeek_scanner_folders'
)

parser.add_argument(
    'path_zeek_config_disable_logs',
    type=str,
    help='absolut path to .zeek config which disables logs',
    default='/home/tobias/work/Cloud-Telescope/shell/config/custom_scripts/disable_logs_for_scanner_script.zeek'
)

parser.add_argument(
    'path_pcap_file',
    type=str,
    help='absolut path to .pcap file',
    default='/home/tobias/work/Cloud-Telescope/data/raw/cloud_merged_pcap/merged_pcap_files.pcap'
)

args = parser.parse_args()

scanner_zeek(args.path_udp_script, args.path_log_folder, args.path_zeek_config_disable_logs, args.path_pcap_file)
