import pandas as pd
from src.config import *
from src.d01_data._find_feather_file import find_feather_file
from src.d01_data.log_names_enum import LogNamesEnum


def get_log_columns(completed_path: str) -> list[str]:
    columns: list[str] = []
    with open(completed_path) as data_file:
        for line in data_file:
            if line.startswith('#fields'):
                columns = line.strip().split('\t')[1:]
                break
    return columns


def read_log_file(log_name: LogNamesEnum, path_to_log_file: str, is_server: bool = False) -> pd.DataFrame:
    completed_path: str
    if is_server:
        completed_path = f'{path_server_data}/{path_to_log_file}/{log_name.value}'
    else:
        completed_path = f'{path_data_raw}/{path_to_log_file}/{log_name.value}'

    dataFrame: pd.DataFrame = pd.DataFrame()
    print(completed_path)
    # completed_path = "/home/jovyan/data/nils-ma/zeek-logs/weird.log"

    columns: list[str] = get_log_columns(completed_path)

    if len(columns) > 0:
        dataFrame = pd.read_csv(
            completed_path,
            delimiter='\t',
            comment='#',
            names=columns,
            low_memory=False
            # skiprows=8
        )
    else:
        dataFrame = pd.read_csv(completed_path, sep='\t')
    return dataFrame


def load_latest_dataframe(log_name: LogNamesEnum) -> pd.DataFrame:
    file_name: str = find_feather_file(log_name).name
    return pd.read_feather(f'{path_data_intermediate}/{file_name}')


def load_specific_dataframe(log_name: LogNamesEnum, full_feather_name: str) -> pd.DataFrame:

    file_name: str = find_feather_file(log_name).name
    return pd.read_feather(f'{path_data_intermediate}/{file_name}')

