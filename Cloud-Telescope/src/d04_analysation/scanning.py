import pandas as pd
from src.config import *
from src.d01_data._find_feather_file import find_feather_file
from src.d01_data.log_names_enum import LogNamesEnum
from src.d01_data.read_files import get_log_columns
import os
from dataclasses import dataclass
import re


@dataclass
class ScanningResponse:
    address_scan: pd.DataFrame
    port_scan: pd.DataFrame


def get_scanning_data(duration: bool = False) -> ScanningResponse:

    address_scan: pd.DataFrame = pd.DataFrame({
        'interval': pd.Series(dtype='str'),
        'threshold': pd.Series(dtype='str'),
        'total_scanner': pd.Series(dtype='int64'),
    })
    port_scan: pd.DataFrame = pd.DataFrame({
        'interval': pd.Series(dtype='str'),
        'threshold': pd.Series(dtype='str'),
        'total_scanner': pd.Series(dtype='int64'),
    })

    scanning_folders: str = f'{path_data_raw}/cloud_merged_pcap/zeek_scanner_folders'

    folder_list: list[str] = os.listdir(scanning_folders)

    result_duration_port: pd.DataFrame = pd.DataFrame()
    result_duration_address: pd.DataFrame = pd.DataFrame()

    for folder in folder_list:

        folder_name = folder.split('-')[-1]
        interval: str = folder_name.split('_')[-1].replace('min', '')
        threshold: str = folder_name.split('_')[0].split('.')[0]

        columns: list[str] = get_log_columns(f'{scanning_folders}/{folder}/notice.log')

        dataFrame: pd.DataFrame = pd.read_csv(
            f'{scanning_folders}/{folder}/notice.log',
            delimiter='\t',
            comment='#',
            names=columns,
            low_memory=False
        )

        total_port_scans: int = len(dataFrame[dataFrame['note'] == 'ScanUDP::Port_Scan'])
        total_address_scans: int = len(dataFrame[dataFrame['note'] == 'ScanUDP::Address_Scan'])

        if duration:
            if not folder.endswith('10min'):
                continue
            print(f'working on folder: {folder}')
            port_scan_duration: pd.DataFrame = dataFrame[dataFrame['note'] == 'ScanUDP::Port_Scan']
            address_scan_duration: pd.DataFrame = dataFrame[dataFrame['note'] == 'ScanUDP::Address_Scan']
            new_row_port: pd.DataFrame = calc_scan_duration(port_scan_duration, threshold)
            result_duration_port = pd.concat([result_duration_port, new_row_port], ignore_index=True)

            new_row_address: pd.DataFrame = calc_scan_duration(address_scan_duration, threshold)
            result_duration_address = pd.concat([result_duration_address, new_row_address], ignore_index=True)

        else:
            print(folder_name)
            print(f'total_port_scans: {total_port_scans}')
            print(f'total_address_scans: {total_address_scans}')
            address_scan.loc[len(address_scan)] = [interval, threshold, total_address_scans]
            port_scan.loc[(len(port_scan))] = [interval, threshold, total_port_scans]

    if duration:
        result_duration_address = resort_duration_df(result_duration_address)
        result_duration_port = resort_duration_df(result_duration_port)

        return ScanningResponse(address_scan=result_duration_address, port_scan=result_duration_port)

    return ScanningResponse(address_scan=address_scan, port_scan=port_scan)


def calc_scan_duration(df: pd.DataFrame, threshold: str) -> pd.DataFrame:

    sec_columns = [f"{i}" for i in range(60)]
    min_columns = [f"{i*60}" for i in range(1, 61)]
    all_columns = ["threshold"] + sec_columns + min_columns
    duration_df = pd.DataFrame([{col: 0 for col in all_columns}])
    duration_df.loc[0, 'threshold'] = int(threshold)

    for index, row in df.iterrows():
        msg: str = row['msg']
        duration_value: str = msg.split(' ')[-1]
        sec: int = int(duration_value.split('m')[0])
        minute: int = int(duration_value.split('m')[-1].replace('s', ''))
        sec = sec + minute * 60

        # for i in range(59, -1, -1):
        #     # if f'{i} sec' not in duration_df.columns:
        #     #   duration_df[f'{i} sec'] = [0]
        #     if sec >= i:
        #         duration_df.loc[0, f'{0}':f'{i}'] += 1
        #         break
        # for i in range(60, 0, -1):
        #     # if f'{i} min' not in duration_df.columns:
        #     #    duration_df[f'{i} min'] = [0]
        #     if sec >= i*60:
        #         duration_df.loc[0, f'{1*60}':f'{i*60}'] += 1
        #         break
        for i in range(0, 59):
            # if f'{i} sec' not in duration_df.columns:
            #   duration_df[f'{i} sec'] = [0]
            if sec <= i:
                duration_df.loc[0, f'{i}':f'{59}'] += 1
                break
        for i in range(1, 60):
            # if f'{i} min' not in duration_df.columns:
            #    duration_df[f'{i} min'] = [0]
            if sec <= i*60:
                duration_df.loc[0, f'{i*60}':f'{60*60}'] += 1
                break

    return duration_df


def resort_duration_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(by='threshold', ascending=True)
    df = df.reset_index(drop=True)

    result_df: pd.DataFrame = df.melt(id_vars=["threshold"], var_name="sec", value_name="total")
    result_df["sec"] = result_df["sec"].str.replace(" sec", "").astype(int)

    return result_df


def calculate_proportion_address_port(scanning_response: ScanningResponse, interval: int, min_threshold_address: int, max_threshold_address: int, min_threshold_port: int, max_threshold_port):
    address_df: pd.DataFrame = scanning_response.address_scan
    port_df: pd.DataFrame = scanning_response.port_scan

    address_df = address_df[address_df['interval'] == interval]
    port_df = port_df[port_df['interval'] == interval]

    address_df = address_df.drop(columns=['interval'])
    port_df = port_df.drop(columns=['interval'])

    address_df["threshold"] = address_df["threshold"].astype(int)
    port_df["threshold"] = port_df["threshold"].astype(int)

    port_df = port_df[port_df['threshold'] >= min_threshold_port]
    port_df = port_df[port_df['threshold'] <= max_threshold_port]

    address_df = address_df[address_df['threshold'] >= min_threshold_port]
    # address_df = address_df.sort_values(by='threshold', ascending=True)
    # for index, row in address_df.iterrows():
    #     if row['threshold'] <= min_threshold_address:
    #         address_df.loc[index, 'total_scanner'] = 0
    address_df.loc[address_df['threshold'] <= min_threshold_address, 'total_scanner'] = 0

    address_df = address_df[address_df['threshold'] <= max_threshold_address]

    merged_df: pd.DataFrame = address_df.merge(port_df, how='left', on='threshold', suffixes=('_address', '_port'))

    merged_df["threshold"] = merged_df["threshold"].astype(int)
    #merged_df = merged_df[merged_df['threshold'] >= min_threshold]
    #merged_df = merged_df[merged_df['threshold'] <= max_threshold]

    merged_df = merged_df.sort_values(by='threshold', ascending=True)

    return merged_df


def calc_total_scanner(unique_src: bool = False, single_src: bool = False, mean_duration: bool = False) -> ScanningResponse:
    address_scan: pd.DataFrame = pd.DataFrame({
        'interval': pd.Series(dtype='str'),
        'threshold': pd.Series(dtype='str'),
        'total_scanner': pd.Series(dtype='int64'),
    })
    port_scan: pd.DataFrame = pd.DataFrame({
        'interval': pd.Series(dtype='str'),
        'threshold': pd.Series(dtype='str'),
        'total_scanner': pd.Series(dtype='int64'),
    })

    scanning_folders: str = os.path.join(path_root, 'Cloud-Telescope', 'data', 'scanner')

    address_scan = calc_total_scanner_loop(f'{scanning_folders}/address_scanner', unique_src, single_src, mean_duration)
    port_scan = calc_total_scanner_loop(f'{scanning_folders}/port_scanner', unique_src, single_src, mean_duration)

    return ScanningResponse(address_scan=address_scan, port_scan=port_scan)


def extract_numbers(s):
    match = re.search(r'threshold(\d+)interval(\d+)', s)
    if match:
        threshold = int(match.group(1))
        interval = int(match.group(2))
        return (threshold, interval)


def calc_total_scanner_loop(scanning_folders: str, unique_src: bool, single_src: bool, mean_duration: bool) -> pd.DataFrame:
    scan_total: pd.DataFrame = pd.DataFrame({
        'interval': pd.Series(dtype='str'),
        'threshold': pd.Series(dtype='str'),
        'total_scanner': pd.Series(dtype='int64'),
    })
    founded_src: list[str] = []
    last_threshold: str = '4'
    folder_list: list[str] = os.listdir(scanning_folders)
    folder_list = sorted(folder_list, key=extract_numbers)
    #print(folder_list)
    for file in folder_list:
        interval: str = file.split('interval')[-1]
        threshold: str = file.split('interval')[0].split('threshold')[-1]
        current_df: pd.DataFrame = pd.read_feather(f'{scanning_folders}/{file}')
        if unique_src:
            src_unique: int = len(current_df['src'].unique())
            scan_total.loc[len(scan_total)] = [interval, threshold, src_unique]
        elif single_src:
            print(f'last_threshold: {last_threshold} , threshold: {threshold}')
            if last_threshold != threshold:
                founded_src = []
            current_df = current_df.drop_duplicates(subset='src', keep='first')
            src_unique: pd.DataFrame = current_df[~current_df['src'].isin(founded_src)]
            #print(f'src_unique: {len(src_unique)}, (interval:{interval} threshold: {threshold})')
            founded_src.extend(src_unique['src'].tolist())
            scan_total.loc[len(scan_total)] = [interval, threshold, len(src_unique)]
            last_threshold = threshold
        elif mean_duration:
            current_df = current_df.drop_duplicates(subset='src', keep='first')
            mean_duration_minutes = current_df['duration'].mean().total_seconds() / 60
            scan_total.loc[len(scan_total)] = [interval, threshold, mean_duration_minutes]
        else:
            scan_total.loc[len(scan_total)] = [interval, threshold, len(current_df)]

    return scan_total


@dataclass
class MixedScanResponse:
    mixed_scan: pd.DataFrame
    address_scan_unique: pd.DataFrame
    port_scan_unique: pd.DataFrame


def calc_mixed_scanner(port_scan: pd.DataFrame, address_scan:pd.DataFrame) -> MixedScanResponse:

    address_scan_unique: pd.DataFrame = address_scan
    port_scan_unique: pd.DataFrame = port_scan
    mixed_scan: pd.DataFrame = pd.DataFrame(columns=port_scan.columns)
    potential_port: pd.DataFrame = port_scan[port_scan['src'].isin(address_scan['src'])]
    potential_address: pd.DataFrame = address_scan[address_scan['src'].isin(port_scan['src'])]

    for index, row in potential_port.iterrows():
        sub_potential_address: pd.DataFrame = potential_address[potential_address['src'] == row['src']]
        sub_potential_address = sub_potential_address[sub_potential_address['ts'] >= row['ts']]
        sub_potential_address = sub_potential_address[sub_potential_address['end_ts'] <= row['end_ts']]

        if len(sub_potential_address) > 0:
            address_scan_unique = address_scan_unique.drop(index=sub_potential_address.index)
            potential_address = potential_address.drop(index=sub_potential_address.index)
            mixed_scan = pd.concat([mixed_scan, sub_potential_address], ignore_index=True)

    for index, row in potential_address.iterrows():
        sub_potential_port: pd.DataFrame = potential_port[potential_port['src'] == row['src']]
        sub_potential_port = sub_potential_port[sub_potential_port['ts'] >= row['ts']]
        sub_potential_port = sub_potential_port[sub_potential_port['end_ts'] <= row['end_ts']]

        if len(sub_potential_port) > 0:
            port_scan_unique = port_scan_unique.drop(index=sub_potential_port.index)
            potential_port = potential_port.drop(index=sub_potential_port.index)
            mixed_scan = pd.concat([mixed_scan, sub_potential_port], ignore_index=True)

    return MixedScanResponse(mixed_scan=mixed_scan, address_scan_unique=address_scan_unique, port_scan_unique=port_scan_unique)


