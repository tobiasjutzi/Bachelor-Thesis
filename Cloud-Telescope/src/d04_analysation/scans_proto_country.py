import pandas as pd
from src.d04_analysation.count_percent import *


def calculate_scans_proto_country(conn_upd: pd.DataFrame, address_scan: pd.DataFrame, mapped_country: pd.DataFrame, mapped_ports: pd.DataFrame):

    mapped_country = mapped_country.sort_values(by='address_scan', ascending=False)
    mapped_country = mapped_country.head(4)
    mapped_country = mapped_country.reset_index(drop=True)

    country_names: list[str] = [mapped_country.loc[0, 'orig_country_location'], mapped_country.loc[1, 'orig_country_location'], mapped_country.loc[2, 'orig_country_location'], mapped_country.loc[3, 'orig_country_location']]

    result: pd.DataFrame = pd.DataFrame({
        'port': pd.Series(dtype='str'),
        'total_scans': pd.Series(dtype='str'),
        country_names[0]: pd.Series(dtype='str'),
        country_names[1]: pd.Series(dtype='str'),
        country_names[2]: pd.Series(dtype='str'),
        country_names[3]: pd.Series(dtype='str'),
    })

    mapped_ports = mapped_ports.drop(index=0)
    result['port'] = mapped_ports['p']
    result['total_scans'] = mapped_ports['total']
    result = result.head(10)

    address_scan = address_scan.rename(columns={'p': 'port'})
    address_scan = address_scan[['src', 'port']]


    conn_upd = conn_upd[['id.orig_h', 'orig_country_location']]
    conn_upd.drop_duplicates(subset=['id.orig_h'], keep='first', inplace=True)

    address_scan = address_scan.merge(conn_upd, how='left', left_on='src', right_on='id.orig_h')
    address_scan = address_scan.drop(columns=['id.orig_h'])
    address_scan['port'] = address_scan['port'].astype(str)
    #return address_scan
    for index_port, row_port in result.iterrows():
        for country_name in country_names:
            address_scan_temp: pd.DataFrame = address_scan[address_scan['port'] == row_port['port']]
            address_scan_temp = address_scan_temp[address_scan_temp['orig_country_location'] == country_name]

            result.loc[index_port, country_name] = len(address_scan_temp)

    return result
