import pandas as pd
from src.config import *
from src.d01_data.log_names_enum import LogNamesEnum
from src.d01_data.read_files import get_log_columns
import os
from dataclasses import dataclass


def scans_mapped_country(conn_upd: pd.DataFrame, address_df: pd.DataFrame, port_df: pd.DataFrame, mixed_df: pd.DataFrame) -> pd.DataFrame:

    conn_upd = conn_upd[['id.orig_h', 'orig_country_location']]
    mapped_list: dict[str, pd.DataFrame] = {'address_scan': address_df, 'port_scan': port_df, 'mixed_scan': mixed_df}

    result_df: pd.DataFrame = pd.DataFrame({
        'orig_country_location': pd.Series(dtype='str'),
    })

    for df_name, mapped_df in mapped_list.items():

        mapped_df = mapped_df[['src']]

        conn_upd_unique: pd.DataFrame = conn_upd.drop_duplicates(subset='id.orig_h', keep='first')
        merged_df: pd.DataFrame = mapped_df.merge(conn_upd_unique, how='left', left_on='src', right_on='id.orig_h')

        new_countries: pd.DataFrame = merged_df['orig_country_location']

        missing_cols = [col for col in result_df.columns if col not in result_df.columns]

        for col in missing_cols:
            new_countries[col] = pd.NA

        result_df = pd.concat([result_df, new_countries])
        result_df = result_df.drop_duplicates(subset=['orig_country_location'])
        result_df = result_df.reset_index(drop=True)

        merged_df = merged_df['orig_country_location'].value_counts().reset_index()
        merged_df = merged_df.rename(columns={'orig_country_location': 'country_location', 'count': df_name})

        result_df = result_df.merge(merged_df, how='left', left_on='orig_country_location', right_on='country_location')
        result_df = result_df.drop(columns=['country_location'])

    result_df = result_df.fillna(0)
    result_df['total'] = None
    for index, row in result_df.iterrows():
        total: int = row['address_scan'] + row['port_scan'] + row['mixed_scan']
        result_df.loc[index, 'total'] = total
    result_df = result_df.sort_values(by='total', ascending=False)
    result_df = result_df.reset_index(drop=True)
    return result_df


