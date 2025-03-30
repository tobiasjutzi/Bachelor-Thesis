import pandas as pd
from typing import Optional
from src.d01_data.log_names_enum import LogNamesEnum
from src.config import telescope_ips as telescope_ip_list
from src.d01_data.read_files import load_latest_dataframe


def filter_upd_traffic(log_name: LogNamesEnum, dataframe_optional: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    dataframe: pd.DataFrame = pd.DataFrame()
    if dataframe is not None:
        dataframe = dataframe_optional
    else:
        dataframe = load_latest_dataframe(log_name)

    return dataframe[dataframe['proto'] == 'udp']


def filter_normal_traffic(log_name: LogNamesEnum, dataframe_optional: Optional[pd.DataFrame] = None) -> pd.DataFrame:

    udp_traffic = dataframe_optional[
        ~(dataframe_optional['id.orig_h'].isin(telescope_ip_list) & (dataframe_optional['history'] != '^d'))
    ]

    return udp_traffic


def filter_backscatter_traffic(log_name: LogNamesEnum, dataframe_optional: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    another filter criterion is to filter the 'conn_state' column with 'SHR'
    'SHR' means that the UDP 'connection' was created but then the destination Server did not received any pakete
    """
    #udp_traffic: pd.DataFrame = filter_upd_traffic(log_name, dataframe_optional)

    udp_traffic: pd.DataFrame = dataframe_optional
    orig_local: pd.DataFrame = udp_traffic[udp_traffic['id.orig_h'].isin(telescope_ip_list)]
    backscatter_traffic: pd.DataFrame = orig_local[orig_local['history'] == '^d']

    return backscatter_traffic
