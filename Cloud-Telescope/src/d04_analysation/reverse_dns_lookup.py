import pandas as pd
import socket
import dns.resolver
import dns.reversename
from src.d04_analysation.count_percent import *
from src.d04_analysation.find_scanner import *


def reserve_dns(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df['dns'] = ''
    resolver = dns.resolver.Resolver()  # Verwendet automatisch die System-Resolver

    for index, row in df.iterrows():
        reverse_dns = ''
        try:
            rev_name = dns.reversename.from_address(row[column])
            reverse_dns = str(resolver.resolve(rev_name, "PTR")[0])
            print(f'Found reverse DNS for IP: {row[column]} : {reverse_dns}')
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout, dns.resolver.NoNameservers):
            print(f'No reverse DNS for IP: {row[column]}')

        if reverse_dns != '':
            print(f'Found reverse DNS for IP: {row[column]} : {reverse_dns}')
        df.loc[index, 'dns'] = reverse_dns

    return df


def calc_top_scanner(port_scan: pd.DataFrame, address_scan: pd.DataFrame, conn_udp: pd.DataFrame) -> FindScannerReturn:
    unique_conn_udp: pd.DataFrame = conn_udp.drop_duplicates(subset='id.orig_h', keep='first')
    result_port: pd.DataFrame = top_scanner_loop(port_scan, unique_conn_udp, 'dst', 10)
    result_address: pd.DataFrame = top_scanner_loop(address_scan, unique_conn_udp, 'p', 10)

    return FindScannerReturn(port_scanner=result_port, address_scanner=result_address)


def top_scanner_loop(df: pd.DataFrame, unique_conn_udp: pd.DataFrame, dst_port_identifier_column: str,
                     result_df_size: int = 10) -> pd.DataFrame:
    unique_conn_udp = unique_conn_udp[['id.orig_h', 'orig_as_name_rir']]
    df['duration_mean'] = pd.to_timedelta(df['duration']).dt.total_seconds()

    result_df: pd.DataFrame = pd.DataFrame({
        'src': pd.Series(dtype='str'),
        'total_scanner': pd.Series(dtype='float'),
        'total_connections': pd.Series(dtype='float'),
        'mean_duration': pd.Series(dtype='float'),
        'unique_ports_host': pd.Series(dtype='float'),
        'orig_as_name_rir': pd.Series(dtype='str'),
    })

    df = df.merge(unique_conn_udp, how='left', left_on='src', right_on='id.orig_h')
    df_calculation: list[ColumnResults] = column_calculation(df, {'orig_as_name_rir': -1, 'total_scanned': -1}, False)
    df_calculation_src: pd.DataFrame = df_calculation[0].result_as_df
    df_calculation_src = df_calculation_src.iloc[1:]
    df_calculation_src = df_calculation_src.head(result_df_size)

    for index, row in df_calculation_src.iterrows():

        sub_port_scan: pd.DataFrame = df[df['orig_as_name_rir'] == row['orig_as_name_rir']]
        mean_duration: float = sub_port_scan['duration_mean'].mean()
        total_scanner: int = len(sub_port_scan)
        total_connections: int = sub_port_scan['total_scanned'].sum()
        print(sub_port_scan['src'].tolist())
        sub_dst_port: pd.DataFrame = sub_port_scan.drop_duplicates(subset=[dst_port_identifier_column], keep='first')
        new_row: pd.DataFrame = pd.DataFrame({
            'src': [" ".join(sub_port_scan['src'].tolist())],
            'total_scanner': [total_scanner],
            'total_connections': [total_connections],
            'mean_duration': [mean_duration],
            'unique_ports_host': [len(sub_dst_port)],
            'orig_as_name_rir': [row['orig_as_name_rir']],
        })
        result_df = pd.concat([result_df, new_row], ignore_index=True)

    return result_df




