import pandas as pd


def aggressivity_mapped_countries(mapped_result_country: pd.DataFrame, conn_udp: pd.DataFrame, address_scan: pd.DataFrame, port_scan: pd.DataFrame):

    result_df: pd.DataFrame = pd.DataFrame({
        'country': pd.Series(dtype='str'),
        'port_aggressivity': pd.Series(dtype='float'),
        'address_aggressivity': pd.Series(dtype='float'),
    })

    result_df['country'] = mapped_result_country['orig_country_location']

    for index, country in mapped_result_country['orig_country_location'].items():
        sub_conn_udp: pd.DataFrame = conn_udp[conn_udp['orig_country_location'] == country]

        sub_port: pd.DataFrame = port_scan[port_scan['src'].isin(sub_conn_udp['id.orig_h'])]
        sub_address: pd.DataFrame = address_scan[address_scan['src'].isin(sub_conn_udp['id.orig_h'])]
        mean_port: float = sub_port['total_scanned'].mean()
        mean_address: float = sub_address['total_scanned'].mean()

        result_df.loc[index, 'port_aggressivity'] = mean_port
        result_df.loc[index, 'address_aggressivity'] = mean_address

    return result_df


