from __future__ import annotations

import os
import subprocess
import argparse



def create_storage_file(storage_temp_files: list[str], output_path: str)-> str:

    storage_file_no: int = len(storage_temp_files)
    try:
        subprocess.run(f'touch temp_storage_{storage_file_no}', shell=True, cwd=f'{output_path}', check=True)
        subprocess.run(f'cp temp_pcap.pcap temp_storage_{storage_file_no}', shell=True, cwd=f'{output_path}',
                       check=True)
        subprocess.run(f'> temp_pcap.pcap', shell=True, cwd=f'{output_path}', check=True)
        print(f'new temporary storage file is created: temp_storage_{storage_file_no}')
        return f'temp_storage_{storage_file_no}'

    except subprocess.CalledProcessError as e:
        print(f'Error while merging .pcap files: {e}')
        return ''


def merge_telescope_pcap(path_telescope_folder: str, output_path: str, ip_folders: list[str], apportionment: int, storage_temp_files: list[str]):
    if not os.path.exists(f'{output_path}/merged_pcap_files.pcap'):
        try:
            subprocess.run(f'touch merged_pcap_files.pcap', shell=True, cwd=f'{output_path}', check=True)
            print(f'merged pcap file is created in: {output_path}/merged_pcap_files.pcap')

        except subprocess.CalledProcessError as e:
            print(f'Error while merging .pcap files: {e}')

    if not os.path.exists(f'{output_path}/temp_pcap.pcap'):
        try:
            subprocess.run(f'touch temp_pcap.pcap', shell=True, cwd=f'{output_path}', check=True)
            print(f'temp_pcap file is created in: {output_path}/temp_pcap.pcap')

        except subprocess.CalledProcessError as e:
            print(f'Error while merging .pcap files: {e}')

    # 2147483648 = 2GB value can be changed
    if os.path.getsize(f'{output_path}/temp_pcap.pcap') > 2147483648:
        storage_temp_files.append(create_storage_file(storage_temp_files, output_path))

    command: str = f'mergecap -w {output_path}/merged_pcap_files.pcap {output_path}/temp_pcap.pcap'

    first_folder: str = ip_folders[0]
    first_folder_parts: list[str] = first_folder.split('-')
    folder_name: str = ''

    for i in range(apportionment):
        if folder_name == '':
            folder_name = first_folder_parts[i]
        else:
            folder_name = f'{folder_name}-{first_folder_parts[i]}'

    print(f'working on sub folder name: {folder_name}')
    to_remove: list[str] = []
    for folder in ip_folders:
        if folder.startswith(folder_name):
            command = command + f' {folder}/*.pcap'
            to_remove.append(folder)

    for folder in to_remove:
        ip_folders.remove(folder)

    try:
        subprocess.run(command, shell=True, cwd=f'{path_telescope_folder}', check=True)
        print(f'finished working on sub folder name: {folder_name}')

    except subprocess.CalledProcessError as e:
        print(f'Error while merging .pcap files: {e}')

    try:
        subprocess.run(f'> temp_pcap.pcap', shell=True, cwd=f'{output_path}', check=True)
        subprocess.run(f'cp merged_pcap_files.pcap temp_pcap.pcap', shell=True, cwd=f'{output_path}', check=True)
        subprocess.run(f'> merged_pcap_files.pcap', shell=True, cwd=f'{output_path}', check=True)

    except subprocess.CalledProcessError as e:
        print(f'Error while merging .pcap files: {e}')

    if len(ip_folders) > 0:
        merge_telescope_pcap(path_telescope_folder, output_path, ip_folders, apportionment, storage_temp_files)
    else:
        storage_files: list[str] = os.listdir(output_path)
        storage_merge_command: str = f'mergecap -w merged_pcap_files.pcap temp_pcap.pcap'
        for file in storage_files:
            if file.startswith('temp_storage_'):
                storage_merge_command = f'{storage_merge_command} {file}'

        try:
            print('merging storage files ...')
            subprocess.run(storage_merge_command, shell=True, cwd=f'{output_path}', check=True)
            print('finished merging storage files ...')

        except subprocess.CalledProcessError as e:
            print(f'Error while merging .pcap files: {e}')

        try:
            subprocess.run(f'rm temp_pcap.pcap', shell=True, cwd=f'{output_path}', check=True)
            subprocess.run(f'rm temp_storage_*', shell=True, cwd=f'{output_path}', check=True)

        except subprocess.CalledProcessError as e:
            print(f'Error while merging .pcap files: {e}')



parser = argparse.ArgumentParser(description='Script to merge Cloud Teleksop pcap files')
parser.add_argument(
    'path_telescope_folder',
    type=str,
    help='absolut path for folder which contains the collected teleskop IP folders',
    default='/hdd-pool/datasets/run200125'
)
parser.add_argument(
    'path_merged_output',
    type=str,
    help='absolut output path',
    default='/home/tobias/work/Cloud-Telescope/data/raw/cloud_merged_pcap/merged_pcap_files.pcap'
)
parser.add_argument(
    'apportionment',
    type=int,
    help='apportionment',
    default=2
)
args = parser.parse_args()

folders: list[str] = os.listdir(args.path_telescope_folder)
folders = sorted(folders)
remove_folders = []
for fol in folders[:]:
    if '.' in fol or fol.endswith('-logs') or not any(file.endswith(".pcap") for file in os.listdir(f'{args.path_telescope_folder}/{fol}')):
        remove_folders.append(fol)

for fold in remove_folders:
    folders.remove(fold)

print(f'Total folder to merge: {len(folders)}')
print(folders)
merge_telescope_pcap(args.path_telescope_folder, args.path_merged_output, folders, args.apportionment, [])
