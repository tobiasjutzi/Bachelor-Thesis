from __future__ import annotations

import os
import subprocess
import argparse


def create_dir(output_path: str, filename_without_type: str) -> str | None:

    output_folder_name: str = filename_without_type.split('_')[0]
    output_folder_path: str = f'{output_path}/{output_folder_name}'
    if not os.path.exists(output_folder_path):
        try:
            os.makedirs(output_folder_path)
            print(f'Output folder was created successfully: {output_folder_path}')
            return output_folder_path
        except PermissionError as e:
            print(f'Error while creating output folder: {e}')
            return None
        except OSError as e:
            print(f'Error while creating output folder: {e}')
            return None
    return output_folder_path


def merge_geo_data_to_ip_file(path_ips_list: str, path_to_db_folder: str, output_path: str, convert_process: int):

    folder_content: list[str] = os.listdir(path_to_db_folder)
    output_mmdb_folder_path: str | None = None
    output_folder_path: str | None = None


    print()
    print(f'start csv to mmdb convert process')
    print()

    for file in folder_content:
        if file.endswith('.csv'):
            filename_with_type: str = file.split('/')[-1]
            filename_without_type: str = filename_with_type.split('.')[0]

            output_mmdb_folder_path = create_dir(f'{path_to_db_folder}/mmdb_files', filename_without_type)
            print(output_mmdb_folder_path)

            if convert_process != 0:
                print(f'working on converting file: {filename_with_type}')

                mmdb_file_name: str = f'{output_mmdb_folder_path}/{filename_without_type}.mmdb'
                command_convert: str = f'mmdbctl import {filename_with_type} {mmdb_file_name}'
                try:
                    subprocess.run(command_convert, shell=True, cwd=path_to_db_folder, check=True)
                    print(f'The file {filename_with_type} was converted successfully and is stored as {mmdb_file_name}')
                except subprocess.CalledProcessError as e:
                    print(f'Error while converting file {filename_with_type} : {e}')


    print()
    print(f'start merge process')
    print()

    folder_content = os.listdir(output_mmdb_folder_path)
    merge_file_path: str = ''

    for file in folder_content:
        if file.endswith('.mmdb'):

            filename_with_type: str = file.split('/')[-1]
            filename_without_type: str = filename_with_type.split('.')[0]
            print()
            print(f'working on merging file: {filename_with_type}')
            print(f'verifying {filename_with_type} ...')

            command_verifying: str = f'mmdbctl verify {filename_with_type}'
            try:
                subprocess.run(command_verifying, shell=True, cwd=f'{output_mmdb_folder_path}', check=True)
                print(f'The file {filename_with_type} was verified successfully')
            except subprocess.CalledProcessError as e:
                print(f'The file {filename_with_type} could not verified: {e}')
                break

            output_folder_path = create_dir(output_path, filename_without_type)
            if output_folder_path is None:
                break

            merge_file_path = f'{output_folder_path}/{filename_without_type}_merge.csv'
            command_merge: str = f'mmdbctl read -f csv {path_ips_list} {filename_with_type} > {merge_file_path}'
            print(f'merge file {filename_with_type} ...')
            try:
                subprocess.run(command_merge, shell=True, cwd=f'{output_mmdb_folder_path}', check=True)
                print(f'The IpInfo Database {filename_with_type} was merged successfully, File: {merge_file_path}')

            except subprocess.CalledProcessError as e:
                print(f'Error while merging IpInfo Database {filename_with_type} : {e}')
                break

    print()

    if output_folder_path:
        mmdb_folder: list[str] = os.listdir(output_folder_path)
        part_folder: dict[str, list[str]] = {}

        for mmdb_file in mmdb_folder:
            file_name_parts: list[str] = mmdb_file.split('.')[0].split('_')
            if file_name_parts[-2] == 'part':
                name: str = '_'.join(file_name_parts[:-3])
                if name in part_folder:
                    part_folder[name].append(mmdb_file)
                else:
                    part_folder[name] = [mmdb_file]

        for name, file_name_list in part_folder.items():
            command: str = '{'
            for index, file_name in enumerate(file_name_list):
                if index == 0:
                    command = f'{command} cat {file_name};'
                else:
                    command = f'{command} tail -n +2 {file_name};'

            command = f"{command} }} > {name}_merge.csv"

            try:
                subprocess.run(command, shell=True, cwd=f'{output_folder_path}', check=True)
                print(f'All parts of {name} are merged successfully')

            except subprocess.CalledProcessError as e:
                print(f'Error while merging the parts of {name} : {e}')
                break

            for file_name in file_name_list:
                try:
                    subprocess.run(f'rm {file_name}', shell=True, cwd=f'{output_folder_path}', check=True)
                    print(f'File {file_name} is deleted successfully')

                except subprocess.CalledProcessError as e:
                    print(f'Error while deleting file {file_name} : {e}')
                    break



parser = argparse.ArgumentParser(description='Script to merge mmdb infos to IP List')
parser.add_argument(
    'path_ips_list',
    type=str,
    help='absolut path to a .txt file which contains a List of IP addresses',
    default='/home/tobias/work/Cloud-Telescope/data/raw/merge_pcap_test/ips.txt'
)
parser.add_argument(
    'path_mmdb_folder',
    type=str,
    help='absolut path to a folder that contains .mmdb geo databases',
    default='/hdd-pool/datasets/ipinfo/database/mmdb_files'
)
parser.add_argument(
    'path_merged_output',
    type=str,
    help='absolut path to a folder which will used to storge the merged output csv files',
    default='/home/tobias/work/Cloud-Telescope/data/ipInfo'
)

parser.add_argument(
    'convert_csv_to_mmdb',
    type=int,
    help='1= convert csv files to mmdb, 0: skip convert process',
    default=1
)
args = parser.parse_args()

merge_geo_data_to_ip_file(args.path_ips_list, args.path_mmdb_folder, args.path_merged_output, args.convert_csv_to_mmdb)

