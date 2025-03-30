from dataclasses import dataclass
from ..config import path_data_intermediate
from src.d01_data.log_names_enum import LogNamesEnum
import os
import re


@dataclass
class FileFinder:
        name: str
        number: int
        type: str
        text: str


def find_feather_file(log_name: LogNamesEnum, full_feather_name: str = None) -> FileFinder:
    """
    full_feather_name == None -> find and return the latest file if it has a value then find the specific file
    :param log_name: name/type of the log file (conn, dns, ntp)
    :param full_feather_name: the full .feather file name (conn_1__test.feather)
    :return: the latest oder specific file as a pd.Dataframe
    """

    files_names = [f for f in os.listdir(f'{path_data_intermediate}') if
                   f.endswith('.feather') and f.startswith(log_name.name)]
    latest_file = FileFinder(name='', number=0, type=log_name.name, text='')

    for file_name in files_names:
        latest_type: str = file_name.split('_', 1)[0]

        start_number: int = len(latest_type) + 1
        end_number: int = len(file_name.split('__', 1)[0])
        latest_number: int = int(file_name[start_number:end_number])

        start_text: int = end_number + 2
        end_text: int = len(file_name.split('.', 1)[0])
        latest_text: str = file_name[start_text: end_text]

        if full_feather_name is None and latest_type and latest_number and latest_number >= latest_file.number:
            latest_file.name = file_name
            latest_file.number = latest_number
            latest_file.type = latest_type
            latest_file.text = latest_text
        if full_feather_name is not None and full_feather_name == file_name:
            latest_file.name = file_name
            latest_file.number = latest_number
            latest_file.type = latest_type
            latest_file.text = latest_text

    return latest_file

