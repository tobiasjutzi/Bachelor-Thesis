from __future__ import annotations

import datetime as dt
import pandas as pd
from src.config import *
from src.d02_intermediate.switch_two_colums import *


def map_icmp_backscatter(conn: pd.DataFrame, backscatter_traffic_unique: pd.DataFrame, backscatter_traffic_complete: pd.DataFrame):

    icmp: pd.DataFrame = conn[conn['proto'] == 'icmp']
    icmp_resp_local: pd.DataFrame = icmp[icmp['id.resp_h'].isin(telescope_ips)]

    backscatter_icmp_attacked_server: pd.DataFrame = icmp_resp_local[icmp_resp_local['id.orig_h'].isin(backscatter_traffic_unique['id.resp_h'])]

    return backscatter_icmp_attacked_server
    backscatter_traffic_unique.loc[:, 'icmp_ddos_start'] = pd.Series(dtype="float")
    backscatter_traffic_unique.loc[:, 'icmp_ddos_end'] = pd.Series(dtype="float")
    backscatter_traffic_unique.loc[:, 'ddos_icmp_duration'] = pd.Series(dtype="float")
    backscatter_traffic_unique.loc[:, 'save_detection_start'] = pd.Series(pd.NA, dtype="boolean")
    backscatter_traffic_unique.loc[:, 'save_detection_end'] = pd.Series(pd.NA, dtype="boolean")
    backscatter_traffic_unique.loc[:, 'ddos_duration_complete'] = pd.Series(dtype="float")
    backscatter_traffic_unique.loc[:, 'ddos_attack_duration'] = pd.Series(dtype="float")

    for index, row in backscatter_traffic_unique.iterrows():
        if row['id.resp_h'] != '64.185.224.134':
            continue
        icmp_current_ip_df: pd.DataFrame = backscatter_icmp_attacked_server[backscatter_icmp_attacked_server['id.orig_h'] == row['id.resp_h']]

        conn_current_ip_df: pd.DataFrame = backscatter_traffic_complete[backscatter_traffic_complete['id.resp_h'] == row['id.resp_h']]

        first_detection: float | None = None
        last_detection: float | None = None
        if not conn_current_ip_df.empty:
            conn_current_ip_df = conn_current_ip_df.sort_values(by='ts', ascending=True)
            conn_current_ip_df = conn_current_ip_df.reset_index(drop=True)
            first_detection = conn_current_ip_df.loc[0, 'ts']
            last_detection = conn_current_ip_df.loc[len(conn_current_ip_df) - 1, 'ts']
            temp_conn = conn_current_ip_df[['id.resp_h', 'ts', 'Date', 'proto', 'uid', 'history']]
            display(temp_conn)
        else:
            print(f"For the response IP: {row['id.resp_h']} not corresponding IP is founded in backscatter_traffic_complete (conn) -> first_detection and last_detection is None")

        icmp_ddos_start: float | None = None
        icmp_ddos_end: float | None = None
        if not icmp_current_ip_df.empty:
            icmp_current_ip_df = icmp_current_ip_df.sort_values(by='ts', ascending=True)
            icmp_current_ip_df = icmp_current_ip_df.reset_index(drop=True)
            icmp_ddos_start = icmp_current_ip_df.loc[0, 'ts']
            icmp_ddos_end = icmp_current_ip_df.loc[len(icmp_current_ip_df) - 1, 'ts']
            temp = icmp_current_ip_df[['id.resp_h', 'id.orig_h', 'ts', 'Date', 'proto', 'uid', 'history']]
            display(temp)
        else:
            print(f"For the response IP: {row['id.resp_h']} is not corresponding IP is founded in icmp_backscatter df icmp_ddos_start and icmp_ddos_end is None")

        if icmp_ddos_start is not None and icmp_ddos_end is not None:
            backscatter_traffic_unique.loc[index, 'icmp_ddos_start'] = icmp_ddos_start
            backscatter_traffic_unique.loc[index, 'icmp_ddos_end'] = icmp_ddos_end
            backscatter_traffic_unique.loc[index, 'ddos_icmp_duration'] = icmp_ddos_end - icmp_ddos_start
            print('---')
            print(f'icmp_ddos_start: {dt.datetime.utcfromtimestamp(icmp_ddos_start).isoformat()}')
            print(f'icmp_ddos_end: {dt.datetime.utcfromtimestamp(icmp_ddos_end).isoformat()}')
            print(f'ddos_icmp_duration: {icmp_ddos_end - icmp_ddos_start}')
            print('-')
        else:
            print(f"for Resp IP: {row['id.resp_h']} icmp_ddos_start and icmp_ddos_end is None -> can not set in df: icmp_ddos_start, icmp_ddos_end, ddos_icmp_duration")

        if backscatter_traffic_unique.loc[index, 'creation_orig'] > 0:
            if first_detection is not None and last_detection is not None:
                if first_detection >= backscatter_traffic_unique.loc[index, 'creation_orig']:
                    backscatter_traffic_unique.loc[index, 'save_detection_start'] = True
                    backscatter_traffic_unique.loc[index, 'ddos_attack_duration'] = last_detection - first_detection
                    print(f'first_detection: {dt.datetime.utcfromtimestamp(first_detection).isoformat()}')
                    print(f'last_detection: {dt.datetime.utcfromtimestamp(last_detection).isoformat()}')
                    print(f'ddos_attack_duration: {last_detection - first_detection}')
                    print('-')
                else:
                    backscatter_traffic_unique.loc[index, 'save_detection_start'] = False
            else:
                print(f"for Resp IP: {row['id.resp_h']} first_detection and last_detection is None -> can not set save_detection_start, ddos_attack_duration, ddos_duration_complete")
        else:
            print(f"for Resp IP: {row['id.resp_h']} creation_orig is negativ -> can not set save_detection_start and ddos_attack_duration")

        if backscatter_traffic_unique.loc[index, 'deletion_orig'] > 0:
            if icmp_ddos_end is not None:
                if icmp_ddos_end <= backscatter_traffic_unique.loc[index, 'deletion_orig']:
                    backscatter_traffic_unique.loc[index, 'save_detection_end'] = True
                else:
                    backscatter_traffic_unique.loc[index, 'save_detection_end'] = False
            else:
                print(f"for Resp IP: {row['id.resp_h']} icmp_ddos_end is None -> can not set save_detection_end")
        else:
            print(f"for Resp IP: {row['id.resp_h']} deletion_orig is negativ -> can not set save_detection_end, ddos_duration_complete")

        if icmp_ddos_end is not None and icmp_ddos_start is not None and icmp_ddos_start is not None and last_detection is not None:
            if backscatter_traffic_unique.loc[index, 'save_detection_end'] and backscatter_traffic_unique.loc[
                index, 'save_detection_start']:
                print(f'first_detection: {dt.datetime.utcfromtimestamp(first_detection).isoformat()}')
                print(f'icmp_ddos_end: {dt.datetime.utcfromtimestamp(icmp_ddos_end).isoformat()}')

                backscatter_traffic_unique.loc[index, 'ddos_duration_complete'] = icmp_ddos_end - first_detection

                print(f'complete: {icmp_ddos_end - first_detection}')
                print('---')

    # backscatter_traffic_unique = backscatter_traffic_unique[backscatter_traffic_unique['icmp_ddos_start'].notna()]
    # backscatter_traffic_unique = switch_two_columns(backscatter_traffic_unique, 'resp_whois_domain_rir', 'ts')

    # backscatter_traffic_unique['icmp_ddos_start'] = pd.to_datetime(backscatter_traffic_unique['icmp_ddos_start'], errors='coerce')
    # backscatter_traffic_unique['icmp_ddos_end'] = pd.to_datetime(backscatter_traffic_unique['icmp_ddos_end'], errors='coerce')
    # backscatter_traffic_unique['ddos_icmp_duration'] = pd.to_timedelta(backscatter_traffic_unique['ddos_icmp_duration'], unit='s', errors='coerce')

    # backscatter_traffic_unique['test'] = backscatter_traffic_unique['ts'] < backscatter_traffic_unique['icmp_ddos_start']
    return backscatter_traffic_unique
