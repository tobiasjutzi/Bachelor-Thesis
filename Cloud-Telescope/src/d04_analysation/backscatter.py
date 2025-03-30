import pandas as pd
from src.d04_analysation.reverse_dns_lookup import *
from src.d04_analysation.count_percent import *
from dataclasses import dataclass
@dataclass
class DnsRirResponse:
    backscatter_dns: pd.DataFrame
    attack_server_name: pd.DataFrame


def calculate_mapped_asn_attacked_ocean(backscatter_unique: pd.DataFrame, compare_column_x: str, compare_column_y: str, threshold_percent: float, sort: bool) -> pd.DataFrame:

    result_df: pd.DataFrame = pd.DataFrame({
        f'{compare_column_x}': pd.Series(dtype=str),
        f'{compare_column_y}': pd.Series(dtype=str),
        'total': pd.Series(dtype=int),
    })

    for index, row in backscatter_unique.iterrows():
        x: str = row[compare_column_x]
        y: str = row[compare_column_y]

        founded_index = -1
        for index_result, row_result in result_df.iterrows():
            if x == row_result[compare_column_x] and y == row_result[compare_column_y]:
                founded_index = index_result
                break

        if founded_index != -1:
            result_df.loc[founded_index, 'total'] += 1
        else:
            result_df.loc[len(result_df)] = [x, y, 1]

    result_df = result_df.sort_values(by=[compare_column_x])
    result_df = result_df.reset_index(drop=True)

    # drop small (threshold_percent) values
    if sort:
        finished_x_val: list[str] = []
        indices_to_drop = []
        for index_result, row_result in result_df.iterrows():
            finished_x_val.append(row_result[compare_column_x])
            temp: pd.DataFrame = result_df[result_df[compare_column_x] == row_result[compare_column_x]]
            temp = temp[temp[compare_column_y] == row_result[compare_column_x]]
            if len(temp) > 0:
                x_self_total: int = temp['total'].max()
                if row_result['total'] < x_self_total * threshold_percent:
                    indices_to_drop.append(index_result)
        result_df = result_df.drop(indices_to_drop)

    all_founded_y_values: pd.Series = result_df[compare_column_y]
    all_founded_y_values = all_founded_y_values.drop_duplicates()
    finished_x_values: list[str] = []

    missing_df: pd.DataFrame = pd.DataFrame({
        f'{compare_column_x}': pd.Series(dtype=str),
        f'{compare_column_y}': pd.Series(dtype=str),
        'total': pd.Series(dtype=int),
    })

    # fill missing x values with null rows
    for index_result, row_result in result_df.iterrows():
        if row_result[compare_column_x] not in finished_x_values:
            finished_x_values.append(row_result[compare_column_x])
            temp_df: pd.DataFrame = result_df[result_df[compare_column_x] == row_result[compare_column_x]]

            missing_y: pd.Series = all_founded_y_values[~all_founded_y_values.isin(temp_df[compare_column_y])]
            for miss_y in missing_y:
                missing_df.loc[len(missing_df)] = [row_result[compare_column_x], miss_y, 0]

    result_df = pd.concat([result_df, missing_df], axis=0, ignore_index=True)

    result_df = result_df.sort_values(by=[compare_column_x, compare_column_y], ascending=[True, False])
    return result_df


def calc_rir_and_dns_information(backscatter_traffic: pd.DataFrame, backscatter_traffic_unique_attack_resp_ip: pd.DataFrame, special_ip_row: str = '') -> DnsRirResponse:
    id_row: str = 'id.resp_h'
    if special_ip_row != '':
        id_row = special_ip_row
    backscatter_dns: pd.DataFrame = reserve_dns(backscatter_traffic_unique_attack_resp_ip, id_row)
    backscatter_dns = backscatter_dns[[id_row, 'dns']]
    backscatter_dns = backscatter_traffic.merge(backscatter_dns, how='left', left_on=id_row, right_on=id_row)

    for index, row in backscatter_dns.iterrows():
        if row['dns'] != '':
            backscatter_dns.loc[index, 'result'] = row['dns']
        else:
            backscatter_dns.loc[index, 'result'] = row['resp_name_2025-01-27']

    attack_server_name: pd.DataFrame = column_calculation(backscatter_dns, {'result': -1}, False)[
        0].result_as_df

    return DnsRirResponse(backscatter_dns=backscatter_dns, attack_server_name=attack_server_name)