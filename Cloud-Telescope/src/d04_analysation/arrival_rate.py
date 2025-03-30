import pandas as pd
from src.d04_analysation.date_time_enum import DateTimeEnum
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class ArrivalRateReturn:
    arrival_rate_df: pd.DataFrame
    mean_arrival_rate: float


switch_sliced_time = {
    DateTimeEnum.year: lambda datetime_obj: datetime_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
    DateTimeEnum.month: lambda datetime_obj: datetime_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
    DateTimeEnum.day: lambda datetime_obj: datetime_obj.replace(hour=0, minute=0, second=0, microsecond=0),
    DateTimeEnum.hour: lambda datetime_obj: datetime_obj.replace(minute=0, second=0, microsecond=0),
    DateTimeEnum.minute: lambda datetime_obj: datetime_obj.replace(second=0, microsecond=0),
    DateTimeEnum.second: lambda datetime_obj: datetime_obj.replace(microsecond=0),
}

switch_time_dimension_difference = {
    DateTimeEnum.year: 12 * 30 * 24 * 60 * 60,
    DateTimeEnum.month: 30 * 24 * 60 * 60,  # todo: month with 31 days
    DateTimeEnum.day: 24 * 60 * 60,
    DateTimeEnum.hour: 60 * 60,
    DateTimeEnum.minute: 60,
    DateTimeEnum.second: 1,
}


def get_arrival_rate(dataframe: pd.DataFrame, start_point: datetime, end_point: datetime, dimension: DateTimeEnum, timestamp_column: Optional[str] = None) -> ArrivalRateReturn:
    """
    calculate the arrival time rate

    :param dataframe: dataframe which contains the timestamps
    :param dimension: the time unit which should be used for calculate the arrival rate (day, hour, second etc...)
    :param timestamp_column: if dataframe does not contain a 'ts' column this parameter can enumerate the name of the timestamp column
    :return: dataframe that contains the specific timestamps which the total traffic and the mean arrival
    """

    column_timestamp: str
    values_per_dimension: pd.DataFrame = pd.DataFrame(columns=['timestamp', 'total_count'])
    start_time: datetime = start_point

    if timestamp_column is None:
        column_timestamp = 'ts'
    else:
        column_timestamp = timestamp_column

    if column_timestamp in dataframe.columns:
        # for loop every timestamp between start and end
        loop_time_sliced: datetime = switch_sliced_time.get(dimension, lambda: datetime(0000, 00, 00, 00, 00, 00))(
            start_time)
        end_time_sliced: datetime = switch_sliced_time.get(dimension, lambda: datetime(0000, 00, 00, 00, 00, 00))(
            end_point)
        values_per_dimension['timestamp'] = pd.to_datetime(values_per_dimension['timestamp'])
        values_per_dimension['total_count'] = values_per_dimension['total_count'].astype(int)
        values_per_dimension.loc[0] = [switch_sliced_time.get(dimension)(start_time), 0]
        # for count the total number of similar timestamps (loop every row of the dataframe)
        current_df_index: int = 0
        current_time: datetime = dataframe.iloc[0, 0]
        current_time_sliced: datetime = switch_sliced_time.get(dimension, lambda: datetime(0000, 00, 00, 00, 00, 00))(
            current_time)
        while loop_time_sliced < end_time_sliced:
            if loop_time_sliced.hour == 0:
               print(f'Progress: {loop_time_sliced}')

            if loop_time_sliced == current_time_sliced:
                if current_df_index >= len(dataframe) - 1:
                    current_time = current_time + timedelta(minutes=1)
                    current_time_sliced = switch_sliced_time.get(dimension)(current_time)
                    continue

                old_row: pd.Series = values_per_dimension.loc[len(values_per_dimension) - 1]
                values_per_dimension.loc[len(values_per_dimension) - 1] = [old_row['timestamp'], old_row['total_count'] + 1]

                current_time = dataframe.iloc[current_df_index + 1, 0]
                current_time_sliced = switch_sliced_time.get(dimension)(current_time)
                current_df_index += 1

            elif loop_time_sliced < current_time_sliced:
                time_differentes: timedelta = current_time_sliced - loop_time_sliced
                total_seconds: float = time_differentes.total_seconds()
                total_difference_in_dimension: float = total_seconds / switch_time_dimension_difference.get(dimension, lambda: 1)

                if total_difference_in_dimension == 1 and current_df_index < len(dataframe) - 1:

                    values_per_dimension.loc[len(values_per_dimension)] = [current_time_sliced, 1]

                    loop_time_sliced = current_time_sliced

                    current_time = dataframe.iloc[current_df_index + 1, 0]
                    current_time_sliced = switch_sliced_time.get(dimension)(current_time)
                    current_df_index += 1

                else:

                    loop_time_sliced = loop_time_sliced + timedelta(minutes=1)
                    values_per_dimension.loc[len(values_per_dimension)] = [loop_time_sliced, 0]

    else:
        print('Dataframe do not contain a timestamp column named ts')

    total_seconds: float = len(values_per_dimension)
    total_arrival_traffic: int = values_per_dimension['total_count'].sum()
    mean_arrival_rate: float = total_arrival_traffic / total_seconds

    arrival_rate_return: ArrivalRateReturn = ArrivalRateReturn(arrival_rate_df=values_per_dimension, mean_arrival_rate=mean_arrival_rate)

    return arrival_rate_return
