import pandas as pd
from ..config import path_data_intermediate
import re
from src.d01_data._find_feather_file import find_feather_file
from src.d01_data._find_feather_file import FileFinder
from src.d01_data.log_names_enum import LogNamesEnum
from src.config import path_data_intermediate


def save_dataframe_as_feather(dataframe: pd.DataFrame, log_name: LogNamesEnum,modify_description: str):
    latestFile: FileFinder = find_feather_file(log_name)

    if latestFile.number == 0:
        if modify_description != '':
            dataframe.to_feather(f'{path_data_intermediate}/{latestFile.type}_1__{modify_description}.feather')
            print(f'{latestFile.type} is save as {latestFile.type}_1__.feather')
            return
        dataframe.to_feather(f'{path_data_intermediate}/{latestFile.type}_1__.feather')
        print(f'{latestFile.type} is save as {latestFile.type}_1__{modify_description}.feather')
        return

    updated_file_name: str
    if modify_description != '':
        if latestFile.text != '':
            updated_file_name: str = f'{path_data_intermediate}/{latestFile.type}_{str(latestFile.number + 1)}__{latestFile.text}-{modify_description}.feather'
            dataframe.to_feather(updated_file_name)
            print(f'{latestFile.type} is save as {updated_file_name}')
            return
        updated_file_name: str = f'{path_data_intermediate}/{latestFile.type}_{str(latestFile.number + 1)}__{modify_description}.feather'
        dataframe.to_feather(updated_file_name)
        print(f'{latestFile.type} is save as {updated_file_name}')
        return
    updated_file_name: str = f'{path_data_intermediate}/{latestFile.type}_{str(latestFile.number + 1)}__{latestFile.text}.feather'
    dataframe.to_feather(updated_file_name)
    print(f'{latestFile.type} is save as {updated_file_name}')

