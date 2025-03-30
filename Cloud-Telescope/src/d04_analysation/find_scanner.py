import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from dataclasses import dataclass
import datetime


@dataclass
class FindScannerReturn:
    address_scanner: pd.DataFrame
    port_scanner: pd.DataFrame


def find_scanning(unique_port_scanner: pd.DataFrame, unique_address_scanner: pd.DataFrame, conn_udp: pd.DataFrame, address_threshold: int, port_threshold: int, address_interval: int,  port_interval: int, port_bool: bool) -> FindScannerReturn:
    conn_udp = conn_udp.sort_values(by='ts', ascending=True)
    conn_udp = conn_udp.reset_index(drop=True)

    unique_port_scanner = unique_port_scanner.sort_values(by='ts', ascending=True)
    unique_port_scanner = unique_port_scanner.reset_index(drop=True)

    unique_address_scanner = unique_address_scanner.sort_values(by='ts', ascending=True)
    unique_address_scanner = unique_address_scanner.reset_index(drop=True)

    address_scanner: pd.DataFrame = pd.DataFrame()
    port_scanner: pd.DataFrame = pd.DataFrame()

    if port_bool:
        if len(unique_port_scanner) > 0:
            port_scanner = finde_port_scan2(unique_port_scanner, conn_udp, port_threshold, port_interval)
    else:
        if len(unique_address_scanner) > 0:
            address_scanner = finde_address_scan2(unique_address_scanner, conn_udp, address_threshold, address_interval)

    return FindScannerReturn(address_scanner=address_scanner, port_scanner=port_scanner)


def finde_address_scan(unique_address_scanner: pd.DataFrame, conn_udp: pd.DataFrame, threshold: int, interval: int) -> pd.DataFrame:
    unique_src: pd.Series = unique_address_scanner['src']

    address_scanner: pd.DataFrame = pd.DataFrame({
        'ts': pd.Series(dtype='float64'),
        'end_ts': pd.Series(dtype='str'),
        'duration': pd.Series(dtype='timedelta64[ns]'),
        'note': pd.Series(dtype='str'),
        'msg': pd.Series(dtype='str'),
        'src': pd.Series(dtype='str'),
        'dst': pd.Series(dtype='str'),
        'p': pd.Series(dtype='str'),
        'total_scanned': pd.Series(dtype='int')
    })

    # loop through all unique src ip's
    for src in unique_src:

        sub_conn: pd.DataFrame = conn_udp[conn_udp['id.orig_h'] == src]

        sub_conn_grouped: DataFrameGroupBy = sub_conn.groupby('id.resp_p')
        sub_conn_port_group: list[pd.DataFrame] = [group for group_name, group in sub_conn_grouped]

        # loop through all resp port grouped dataframes
        for sub_conn_port in sub_conn_port_group:

            if len(sub_conn_port) < threshold:
                continue
            sub_conn_port = sub_conn_port.sort_values(by='ts', ascending=True)
            sub_conn_port = sub_conn_port.reset_index(drop=True)

            current_sequence: pd.DataFrame = pd.DataFrame({
                'ts': pd.Series(dtype='float64'),
                'resp_ip': pd.Series(dtype='str'),
            })

            current_sequence.loc[0, 'ts'] = sub_conn_port["ts"].iloc[0]
            current_sequence.loc[0, 'resp_ip'] = sub_conn_port["id.resp_h"].iloc[0]

            start_index: int = 1
            for i in range(start_index, len(sub_conn_port)):
                if sub_conn_port["ts"].iloc[i] - sub_conn_port["ts"].iloc[i - 1] <= interval:
                    if not sub_conn_port["id.resp_h"].iloc[i] in current_sequence['resp_ip']:
                        new_row = pd.DataFrame({
                            'ts': [sub_conn_port["ts"].iloc[i]],
                            'resp_ip': [sub_conn_port["id.resp_h"].iloc[i]],
                        })
                        current_sequence = pd.concat([current_sequence, new_row], ignore_index=True)

                else:
                    if len(current_sequence) >= threshold:
                        result_new_row = pd.DataFrame(
                            {'ts': [current_sequence.iloc[0]['ts']],
                             'end_ts': [current_sequence.iloc[-1]['ts']],
                             'duration': [pd.to_timedelta(current_sequence.iloc[-1]['ts'] - current_sequence.iloc[0]['ts'], unit='s')],
                             'note': ['ScanUDP::Address_Scan'],
                             'msg': [''],
                             'src': [src],
                             'dst': [''],
                             'p': [sub_conn_port.iloc[0]['id.resp_p']],
                             'total_scanned': [len(current_sequence)],
                             })
                        address_scanner = pd.concat([address_scanner, result_new_row], ignore_index=True)

                    current_sequence = pd.DataFrame({
                        'ts': pd.Series(dtype='float64'),
                        'resp_ip': pd.Series(dtype='str'),
                    })
                    new_row = pd.DataFrame(
                        {'ts': [sub_conn_port.iloc[i]["ts"]], 'resp_ip': [sub_conn_port.iloc[i]["id.resp_h"]]})
                    current_sequence = pd.concat([current_sequence, new_row], ignore_index=True)

            if len(current_sequence) >= threshold:

                result_new_row = pd.DataFrame(
                    {'ts': [current_sequence.iloc[0]['ts']],
                     'end_ts': [current_sequence.iloc[-1]['ts']],
                     'duration': [pd.to_timedelta(current_sequence.iloc[-1]['ts'] - current_sequence.iloc[0]['ts'], unit='s')],
                     'note': ['ScanUDP::Address_Scan'],
                     'msg': [''],
                     'src': [src],
                     'dst': [''],
                     'p': [sub_conn_port.iloc[0]['id.resp_p']],
                     'total_scanned': [len(current_sequence)],
                     })
                address_scanner = pd.concat([address_scanner, result_new_row], ignore_index=True)

    return address_scanner


def finde_port_scan(unique_port_scanner: pd.DataFrame, conn_udp: pd.DataFrame, threshold: int, interval: int) -> pd.DataFrame:

    unique_src: pd.Series = unique_port_scanner['src']
    port_scanner: pd.DataFrame = pd.DataFrame({
        'ts': pd.Series(dtype='float64'),
        'end_ts': pd.Series(dtype='str'),
        'duration': pd.Series(dtype='timedelta64[ns]'),
        'note': pd.Series(dtype='str'),
        'msg': pd.Series(dtype='str'),
        'src': pd.Series(dtype='str'),
        'dst': pd.Series(dtype='str'),
        'p': pd.Series(dtype='str'),
        'total_scanned': pd.Series(dtype='int')
    })

    for src in unique_src:

        sub_conn: pd.DataFrame = conn_udp[conn_udp['id.orig_h'] == src]

        sub_conn_grouped: DataFrameGroupBy = sub_conn.groupby('id.resp_h')
        sub_conn_resp_ip_group: list[pd.DataFrame] = [group for group_name, group in sub_conn_grouped]

        for sub_conn_resp_ip in sub_conn_resp_ip_group:
            if len(sub_conn_resp_ip) < threshold:
                continue

            sub_conn_resp_ip = sub_conn_resp_ip.sort_values(by='ts', ascending=True)
            sub_conn_resp_ip = sub_conn_resp_ip.reset_index(drop=True)

            current_sequence: pd.DataFrame = pd.DataFrame({
                'ts': pd.Series(dtype='float64'),
                'resp_port': pd.Series(dtype='str'),
            })

            current_sequence.loc[0, 'ts'] = sub_conn_resp_ip["ts"].iloc[0]
            current_sequence.loc[0, 'resp_port'] = sub_conn_resp_ip["id.resp_p"].iloc[0]

            start_index: int = 1
            for i in range(start_index, len(sub_conn_resp_ip)):
                if sub_conn_resp_ip["ts"].iloc[i] - sub_conn_resp_ip["ts"].iloc[i - 1] <= interval:
                    if str(sub_conn_resp_ip["id.resp_p"].iloc[i]) not in [num.strip() for num in current_sequence['resp_port'].split(',')]:
                        new_row = pd.DataFrame({
                            'ts': [sub_conn_resp_ip["ts"].iloc[i]],
                            'resp_port': [sub_conn_resp_ip["id.resp_p"].iloc[i]],
                        })
                        current_sequence = pd.concat([current_sequence, new_row], ignore_index=True)

                else:
                    if len(current_sequence) >= threshold:
                        result_new_row = pd.DataFrame(
                            {'ts': [current_sequence.iloc[0]['ts']],
                             'end_ts': [current_sequence.iloc[-1]['ts']],
                             'duration': [pd.to_timedelta(current_sequence.iloc[-1]['ts'] - current_sequence.iloc[0]['ts'], unit='s')],
                             'note': ['ScanUDP::Port_Scan'],
                             'msg': [''],
                             'src': [src],
                             'dst': [sub_conn_resp_ip["id.resp_h"].iloc[0]],
                             'p': [', '.join(current_sequence['resp_port'].astype(str))],
                             'total_scanned': [len(current_sequence)],
                             })
                        port_scanner = pd.concat([port_scanner, result_new_row], ignore_index=True)

                    current_sequence = pd.DataFrame({
                        'ts': pd.Series(dtype='float64'),
                        'resp_port': pd.Series(dtype='str'),
                    })
                    new_row = pd.DataFrame(
                        {'ts': [sub_conn_resp_ip.iloc[i]["ts"]], 'resp_port': [sub_conn_resp_ip.iloc[i]["id.resp_p"]]})
                    current_sequence = pd.concat([current_sequence, new_row], ignore_index=True)

            if len(current_sequence) >= threshold:
                result_new_row = pd.DataFrame(
                    {'ts': [current_sequence.iloc[0]['ts']],
                     'end_ts': [current_sequence.iloc[-1]['ts']],
                     'duration': [pd.to_timedelta(current_sequence.iloc[-1]['ts'] - current_sequence.iloc[0]['ts'], unit='s')],
                     'note': ['ScanUDP::Port_Scan'],
                     'msg': [''],
                     'src': [src],
                     'dst': [sub_conn_resp_ip["id.resp_h"].iloc[0]],
                     'p': [', '.join(current_sequence['resp_port'].astype(str))],
                     'total_scanned': [len(current_sequence)],
                     })
                port_scanner = pd.concat([port_scanner, result_new_row], ignore_index=True)
    return port_scanner


###


def finde_address_scan2(unique_address_scanner: pd.DataFrame, conn_udp: pd.DataFrame, threshold: int, interval: int) -> pd.DataFrame:
    unique_src: pd.Series = unique_address_scanner['id.orig_h']

    address_scanner: pd.DataFrame = pd.DataFrame({
        'ts': pd.Series(dtype='float64'),
        'end_ts': pd.Series(dtype='str'),
        'duration': pd.Series(dtype='timedelta64[ns]'),
        'note': pd.Series(dtype='str'),
        'msg': pd.Series(dtype='str'),
        'src': pd.Series(dtype='str'),
        'dst': pd.Series(dtype='str'),
        'p': pd.Series(dtype='str'),
        'total_scanned': pd.Series(dtype='int')
    })

    # loop through all unique src ip's
    print(len(unique_src))
    count: int = 0
    for src in unique_src:
        print(count)
        count = count + 1
        sub_conn: pd.DataFrame = conn_udp[conn_udp['id.orig_h'] == src]

        sub_conn_grouped: DataFrameGroupBy = sub_conn.groupby('id.resp_p')
        sub_conn_port_group: list[pd.DataFrame] = [group for group_name, group in sub_conn_grouped]

        # loop through all resp port grouped dataframes
        for sub_conn_port in sub_conn_port_group:

            if len(sub_conn_port) < threshold:
                continue
            sub_conn_port = sub_conn_port.sort_values(by='ts', ascending=True)
            sub_conn_port = sub_conn_port.reset_index(drop=True)

            current_sequence: pd.DataFrame = pd.DataFrame({
                'ts': pd.Series(dtype='float64'),
                'resp_ip': pd.Series(dtype='str'),
            })

            current_sequence.loc[0, 'ts'] = sub_conn_port["ts"].iloc[0]
            current_sequence.loc[0, 'resp_ip'] = sub_conn_port["id.resp_h"].iloc[0]

            start_index: int = 1
            for i in range(start_index, len(sub_conn_port)):
                if sub_conn_port["ts"].iloc[i] - sub_conn_port["ts"].iloc[i - 1] <= interval:
                    if not sub_conn_port["id.resp_h"].iloc[i] in current_sequence['resp_ip']:
                        new_row = pd.DataFrame({
                            'ts': [sub_conn_port["ts"].iloc[i]],
                            'resp_ip': [sub_conn_port["id.resp_h"].iloc[i]],
                        })
                        current_sequence = pd.concat([current_sequence, new_row], ignore_index=True)

                else:
                    if len(current_sequence) >= threshold:
                        result_new_row = pd.DataFrame(
                            {'ts': [current_sequence.iloc[0]['ts']],
                             'end_ts': [current_sequence.iloc[-1]['ts']],
                             'duration': [pd.to_timedelta(current_sequence.iloc[-1]['ts'] - current_sequence.iloc[0]['ts'], unit='s')],
                             'note': ['ScanUDP::Address_Scan'],
                             'msg': [''],
                             'src': [src],
                             'dst': [''],
                             'p': [sub_conn_port.iloc[0]['id.resp_p']],
                             'total_scanned': [len(current_sequence)],
                             })
                        address_scanner = pd.concat([address_scanner, result_new_row], ignore_index=True)

                    current_sequence = pd.DataFrame({
                        'ts': pd.Series(dtype='float64'),
                        'resp_ip': pd.Series(dtype='str'),
                    })
                    new_row = pd.DataFrame(
                        {'ts': [sub_conn_port.iloc[i]["ts"]], 'resp_ip': [sub_conn_port.iloc[i]["id.resp_h"]]})
                    current_sequence = pd.concat([current_sequence, new_row], ignore_index=True)

            if len(current_sequence) >= threshold:

                result_new_row = pd.DataFrame(
                    {'ts': [current_sequence.iloc[0]['ts']],
                     'end_ts': [current_sequence.iloc[-1]['ts']],
                     'duration': [pd.to_timedelta(current_sequence.iloc[-1]['ts'] - current_sequence.iloc[0]['ts'], unit='s')],
                     'note': ['ScanUDP::Address_Scan'],
                     'msg': [''],
                     'src': [src],
                     'dst': [''],
                     'p': [sub_conn_port.iloc[0]['id.resp_p']],
                     'total_scanned': [len(current_sequence)],
                     })
                address_scanner = pd.concat([address_scanner, result_new_row], ignore_index=True)

    return address_scanner


def finde_port_scan2(unique_port_scanner: pd.DataFrame, conn_udp: pd.DataFrame, threshold: int, interval: int) -> pd.DataFrame:

    unique_src: pd.Series = unique_port_scanner['id.orig_h']
    port_scanner: pd.DataFrame = pd.DataFrame({
        'ts': pd.Series(dtype='float64'),
        'end_ts': pd.Series(dtype='str'),
        'duration': pd.Series(dtype='timedelta64[ns]'),
        'note': pd.Series(dtype='str'),
        'msg': pd.Series(dtype='str'),
        'src': pd.Series(dtype='str'),
        'dst': pd.Series(dtype='str'),
        'p': pd.Series(dtype='str'),
        'total_scanned': pd.Series(dtype='int')
    })
    print(len(unique_src))
    count: int = 0
    for src in unique_src:
        print(count)
        count = count + 1
        sub_conn: pd.DataFrame = conn_udp[conn_udp['id.orig_h'] == src]

        sub_conn_grouped: DataFrameGroupBy = sub_conn.groupby('id.resp_h')
        sub_conn_resp_ip_group: list[pd.DataFrame] = [group for group_name, group in sub_conn_grouped]

        for sub_conn_resp_ip in sub_conn_resp_ip_group:
            if len(sub_conn_resp_ip) < threshold:
                continue

            sub_conn_resp_ip = sub_conn_resp_ip.sort_values(by='ts', ascending=True)
            sub_conn_resp_ip = sub_conn_resp_ip.reset_index(drop=True)

            current_sequence: pd.DataFrame = pd.DataFrame({
                'ts': pd.Series(dtype='float64'),
                'resp_port': pd.Series(dtype='str'),
            })

            current_sequence.loc[0, 'ts'] = sub_conn_resp_ip["ts"].iloc[0]
            current_sequence.loc[0, 'resp_port'] = sub_conn_resp_ip["id.resp_p"].iloc[0]

            start_index: int = 1
            for i in range(start_index, len(sub_conn_resp_ip)):
                if sub_conn_resp_ip["ts"].iloc[i] - sub_conn_resp_ip["ts"].iloc[i - 1] <= interval:
                    print(f'str: {str(sub_conn_resp_ip["id.resp_p"].iloc[i])}')

                    if str(sub_conn_resp_ip["id.resp_p"].iloc[i]) not in [str(x) for x in current_sequence['resp_port'].tolist()]:
                        new_row = pd.DataFrame({
                            'ts': [sub_conn_resp_ip["ts"].iloc[i]],
                            'resp_port': [sub_conn_resp_ip["id.resp_p"].iloc[i]],
                        })
                        current_sequence = pd.concat([current_sequence, new_row], ignore_index=True)

                else:
                    if len(current_sequence) >= threshold:
                        result_new_row = pd.DataFrame(
                            {'ts': [current_sequence.iloc[0]['ts']],
                             'end_ts': [current_sequence.iloc[-1]['ts']],
                             'duration': [pd.to_timedelta(current_sequence.iloc[-1]['ts'] - current_sequence.iloc[0]['ts'], unit='s')],
                             'note': ['ScanUDP::Port_Scan'],
                             'msg': [''],
                             'src': [src],
                             'dst': [sub_conn_resp_ip["id.resp_h"].iloc[0]],
                             'p': [', '.join(current_sequence['resp_port'].astype(str))],
                             'total_scanned': [len(current_sequence)],
                             })
                        port_scanner = pd.concat([port_scanner, result_new_row], ignore_index=True)

                    current_sequence = pd.DataFrame({
                        'ts': pd.Series(dtype='float64'),
                        'resp_port': pd.Series(dtype='str'),
                    })
                    new_row = pd.DataFrame(
                        {'ts': [sub_conn_resp_ip.iloc[i]["ts"]], 'resp_port': [sub_conn_resp_ip.iloc[i]["id.resp_p"]]})
                    current_sequence = pd.concat([current_sequence, new_row], ignore_index=True)

            if len(current_sequence) >= threshold:
                result_new_row = pd.DataFrame(
                    {'ts': [current_sequence.iloc[0]['ts']],
                     'end_ts': [current_sequence.iloc[-1]['ts']],
                     'duration': [pd.to_timedelta(current_sequence.iloc[-1]['ts'] - current_sequence.iloc[0]['ts'], unit='s')],
                     'note': ['ScanUDP::Port_Scan'],
                     'msg': [''],
                     'src': [src],
                     'dst': [sub_conn_resp_ip["id.resp_h"].iloc[0]],
                     'p': [', '.join(current_sequence['resp_port'].astype(str))],
                     'total_scanned': [len(current_sequence)],
                     })
                port_scanner = pd.concat([port_scanner, result_new_row], ignore_index=True)
    return port_scanner