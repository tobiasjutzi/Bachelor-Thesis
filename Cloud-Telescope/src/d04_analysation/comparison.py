import pandas as pd
from dataclasses import dataclass


@dataclass
class ComparisonResponse:
    cloud_in_darknet: pd.DataFrame
    cloud_not_in_darknet: pd.DataFrame


def address_comparison(cloud_in_darknet: pd.DataFrame, cloud_not_in_darknet: pd.DataFrame, conn_udp: pd.DataFrame) -> ComparisonResponse:

    cloud_in_darknet = add_country_information(cloud_in_darknet, conn_udp)
    cloud_not_in_darknet = add_country_information(cloud_not_in_darknet, conn_udp)

    return ComparisonResponse(cloud_in_darknet=cloud_in_darknet, cloud_not_in_darknet=cloud_not_in_darknet)


def add_country_information(df: pd.DataFrame, conn_udp: pd.DataFrame) -> pd.DataFrame:
    conn_unique: pd.DataFrame = conn_udp.drop_duplicates(subset='id.orig_h', keep='first')
    conn_unique = conn_unique[['id.orig_h', 'orig_country_location', 'orig_timezone_location']]
    df_country: pd.DataFrame = df.merge(conn_unique, how='left', left_on='src', right_on='id.orig_h')
    df_country['orig_timezone_location'] = df_country['orig_timezone_location'].str.split('/').str[0]
    # df_country['resp_timezone_location'] = df_country['resp_timezone_location'].str.split('/').str[0]

    return df_country
