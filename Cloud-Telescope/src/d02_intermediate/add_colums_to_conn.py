import pandas as pd
import pycountry
import os
from src.config import *

def _get_country_name(alpha_code):
    if pd.isna(alpha_code):
        return None
    country = pycountry.countries.get(alpha_2=alpha_code)
    return country.name if country else None


def add_country_name(conn_dataframe: pd.DataFrame):
    conn_dataframe['orig_country_name'] = conn_dataframe['geo.orig.country_code'].apply(_get_country_name)
    conn_dataframe['resp_country_name'] = conn_dataframe['geo.resp.country_code'].apply(_get_country_name)
    return conn_dataframe


def add_column_data(conn: pd.DataFrame) -> pd.DataFrame:
    conn['Date'] = pd.to_datetime(conn['ts'], unit='s', utc=True).dt.round('us')
    return conn


def merge_ip_info(conn_df: pd.DataFrame, ip_info_merge_folder_from_root: str) -> pd.DataFrame:
    conn_merge: pd.DataFrame = conn_df
    final_df: pd.DataFrame

    #orig_ip: pd.DataFrame = conn_merge[conn_merge['id.orig_h']]
    absolut_ip_info_folder_path: str = f'{path_root}/Cloud-Telescope/data/{ip_info_merge_folder_from_root}'

    ip_info_files: list[str] = os.listdir(absolut_ip_info_folder_path)

    print(f'conn_merge infos: {conn_merge.shape[0]} und {conn_merge.shape[1]}')
    print(conn_merge.columns)
    print('------------')
    for file in ip_info_files:
        print(f'Working on file: {file} ...')
        file_description: str = file.split('.')[0].split('_')[-2]
        absolut_ip_info_file_path: str = f'{absolut_ip_info_folder_path}/{file}'

        current_chunk: int = 0
        chunk_size = 100_000

        ipInfo: pd.DataFrame = pd.read_csv(absolut_ip_info_file_path)
        ipInfo.drop_duplicates(inplace=True)
        print('Duplikate::')
        print(ipInfo['ip'].nunique())  # Anzahl der eindeutigen Werte

        ipInfo = ipInfo.rename(columns=lambda x: f'resp_{x}_{file_description}')
        print(ipInfo.columns)
        print(f'IpInfo DF: {ipInfo.shape[0]} und {ipInfo.shape[1]}')
        print(f'conn_merge infos2: {conn_merge.shape[0]} und {conn_merge.shape[1]}')
        conn_merge = conn_merge.merge(ipInfo, how='left', left_on='id.resp_h', right_on=f'resp_ip_{file_description}')
        print(f'neues conn_merge: {conn_merge.shape[0]} und {conn_merge.shape[1]}')

        # for chunk in pd.read_csv(absolut_ip_info_file_path, chunksize=chunk_size):
        #     print(f'working on chunk: {current_chunk}')
        #     chunk = chunk.rename(columns=lambda x: f'orig_{x}_{file_description}')
        #     conn_merge = conn_merge.merge(chunk, how='left', left_on='id.orig_h', right_on=f'orig_ip_{file_description}')
        #     conn_merge = conn_merge.drop(columns=[f'orig_ip_{file_description}'])
        #     print(f'finished working on chunk: {current_chunk}')
        #     current_chunk = current_chunk + 1

        print(f'Finished working on file: {file}')

    return conn_merge
